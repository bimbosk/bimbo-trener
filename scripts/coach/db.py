"""The SQLite store: the only module that writes SQL.

Responsibilities: connection settings (no WAL, foreign keys), writer lock, schema creation and
migration (with a pre-migration backup), sync-bound compressed backups with rotation, the
append-only journal export, and the read/write API used by CLI and MCP.
"""
from __future__ import annotations

import gzip
import json
import os
import sqlite3
import time
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from . import schema
from .layout import DataPaths
from .paths import append_line, assert_plain_path

FEELING_VALUES = ("easy", "ok", "hard")
JOURNAL_KINDS = ("feeling", "note", "circumstance", "decision", "conversation_summary")
PLAN_STATUSES = ("proposed", "done", "skipped")
SUMMARY_KINDS = ("week", "month")
WRITER_WAIT_S = 5.0


class StoreError(RuntimeError):
    """A visible failure; never swallowed."""


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _try_lock(handle) -> bool:
    try:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError:
        return False


@contextmanager
def writer_lock(data: DataPaths, wait_s: float = WRITER_WAIT_S) -> Iterator[None]:
    """One writer at a time per data directory (sync, import, coach writes)."""
    assert_plain_path(data.write_lock)
    data.root.mkdir(parents=True, exist_ok=True)
    with data.write_lock.open("a+b") as handle:
        handle.seek(0); handle.write(b"0"); handle.flush(); handle.seek(0)
        deadline = time.monotonic() + wait_s
        while not _try_lock(handle):
            if time.monotonic() >= deadline:
                raise StoreError("Iný zápis do databázy práve beží (writer.lock).")
            time.sleep(0.05)
        try:
            yield
        finally:
            if os.name == "nt":
                import msvcrt
                handle.seek(0); msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle, fcntl.LOCK_UN)


def connect(data: DataPaths, read_only: bool = False) -> sqlite3.Connection:
    assert_plain_path(data.database)
    if read_only:
        if not data.database.is_file():
            raise StoreError(f"Databáza neexistuje: {data.database}")
        connection = sqlite3.connect(f"{data.database.resolve().as_uri()}?mode=ro", uri=True, timeout=10)
    else:
        connection = sqlite3.connect(data.database, timeout=10)
        # One file on disk (no -wal/-shm) so the sync tool never sees a half-written database.
        connection.execute("PRAGMA journal_mode=DELETE")
        connection.execute("PRAGMA synchronous=FULL")
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


# --- schema and migrations ---------------------------------------------------------------

def ensure_schema(data: DataPaths) -> dict:
    """Create the schema in a new database or migrate an older one (backup first)."""
    with writer_lock(data):
        created = not data.database.is_file()
        with connect(data) as connection:
            if created:
                schema.create_schema(connection)
                connection.execute("INSERT OR REPLACE INTO meta(key, value) VALUES ('created_at', ?)", (utcnow(),))
                return {"created": True, "schema_version": schema.SCHEMA_VERSION}
            version = schema.current_version(connection)
        if version > schema.SCHEMA_VERSION:
            raise StoreError(f"Databáza má novšiu schému ({version}) než tento kód ({schema.SCHEMA_VERSION}).")
        if version < schema.SCHEMA_VERSION:
            _migrate(data, version)
        return {"created": False, "schema_version": schema.SCHEMA_VERSION, "migrated_from": version if version < schema.SCHEMA_VERSION else None}


def _migrate(data: DataPaths, from_version: int) -> None:
    backup = backup_database(data, tag="pre-migration", rotate=False)
    with connect(data) as connection:
        for version in range(from_version + 1, schema.SCHEMA_VERSION + 1):
            for statement in schema.MIGRATIONS.get(version, ()):
                connection.execute(statement)
            connection.execute("INSERT OR REPLACE INTO meta(key, value) VALUES ('schema_version', ?)", (str(version),))
        schema.create_schema(connection)   # idempotent: new tables/indexes for this version
    with connect(data, read_only=True) as connection:
        if connection.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise StoreError(f"Databáza po migrácii neprešla quick_check; záloha: {backup}")


# --- backups and export --------------------------------------------------------------------

def backup_database(data: DataPaths, tag: str | None = None, rotate: bool = True, keep: int = 5,
                    today: date | None = None) -> Path | None:
    """Compressed consistent copy via the SQLite backup API. Returns None when today's regular backup exists."""
    data.backups.mkdir(parents=True, exist_ok=True)
    stamp = (today or date.today()).isoformat()
    name = f"runs-{stamp}{'-' + tag if tag else ''}.sqlite3.gz"
    target = data.backups / name
    assert_plain_path(target)
    if target.exists() and not tag:
        return None
    temporary = data.backups / f"{name}.pending"
    plain = data.backups / f"{name}.plain-{os.getpid()}"
    for stale in (temporary, plain):
        stale.unlink(missing_ok=True)
    source = connect(data, read_only=True)
    try:
        disk = sqlite3.connect(plain)
        try:
            source.backup(disk)     # consistent copy even while readers are open
        finally:
            disk.close()
    finally:
        source.close()
    try:
        with plain.open("rb") as src, gzip.open(temporary, "wb", compresslevel=6) as dst:
            while chunk := src.read(1024 * 1024):
                dst.write(chunk)
    finally:
        plain.unlink(missing_ok=True)
    os.replace(temporary, target)
    if rotate:
        regular = sorted(p for p in data.backups.glob("runs-*.sqlite3.gz") if "-pre-migration" not in p.name)
        for old in regular[:-keep] if keep > 0 else []:
            old.unlink()
    return target


def restore_database(data: DataPaths, backup: Path) -> Path:
    """Replace the live database with a backup; the previous file is kept as .broken-<time>."""
    assert_plain_path(backup)
    if not backup.is_file():
        raise StoreError(f"Záloha neexistuje: {backup}")
    with writer_lock(data):
        broken = None
        if data.database.exists():
            broken = data.database.with_name(f"{data.database.name}.broken-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
            os.replace(data.database, broken)
        temporary = data.database.with_name(data.database.name + ".restoring")
        with gzip.open(backup, "rb") as src, temporary.open("wb") as dst:
            while chunk := src.read(1024 * 1024):
                dst.write(chunk)
        os.replace(temporary, data.database)
    with connect(data, read_only=True) as connection:
        if connection.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise StoreError("Obnovená databáza neprešla quick_check.")
    return broken or data.database


def export_record(data: DataPaths, kind: str, payload: dict) -> None:
    """Append one coach/owner write to journal-export.jsonl (never truncated)."""
    line = json.dumps({"record": kind, "exported_at": utcnow(), "data": payload}, ensure_ascii=False, default=str)
    append_line(data.journal_export, line)


def read_export(data: DataPaths) -> list[dict]:
    if not data.journal_export.is_file():
        return []
    rows = []
    for number, line in enumerate(data.journal_export.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as error:
            raise StoreError(f"journal-export.jsonl riadok {number} nie je platný JSON: {error}") from None
    return rows


# --- meta ---------------------------------------------------------------------------------

def get_meta(connection: sqlite3.Connection, key: str) -> str | None:
    row = connection.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row[0] if row else None


def set_meta(connection: sqlite3.Connection, key: str, value: str) -> None:
    connection.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", (key, value))


# --- own data: writes (each one exported) ----------------------------------------------------

def _date(value: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        raise StoreError(f"Dátum musí byť RRRR-MM-DD: {value!r}") from None


def add_feeling(data: DataPaths, event_date: str, value: str, text: str | None = None,
                activity_id: int | None = None, recorded_by: str = "coach") -> dict:
    if value not in FEELING_VALUES:
        raise StoreError(f"Pocit musí byť jeden z {FEELING_VALUES}: {value!r}")
    event_date = _date(event_date)
    now = utcnow()
    with writer_lock(data), connect(data) as connection:
        cursor = connection.execute(
            "INSERT INTO feelings(event_date, activity_id, value, text, recorded_at) VALUES (?, ?, ?, ?, ?)",
            (event_date, activity_id, value, text, now))
        feeling_id = cursor.lastrowid
        connection.execute(
            "INSERT INTO journal(event_date, kind, text, activity_id, recorded_at, recorded_by) VALUES (?, 'feeling', ?, ?, ?, ?)",
            (event_date, f"pocit: {value}" + (f" — {text}" if text else ""), activity_id, now, recorded_by))
    row = {"feeling_id": feeling_id, "event_date": event_date, "activity_id": activity_id, "value": value,
           "text": text, "recorded_at": now}
    export_record(data, "feeling", row)
    return row


def add_journal(data: DataPaths, event_date: str, kind: str, text: str, activity_id: int | None = None,
                plan_id: int | None = None, recorded_by: str = "coach") -> dict:
    if kind not in JOURNAL_KINDS:
        raise StoreError(f"Druh záznamu musí byť jeden z {JOURNAL_KINDS}: {kind!r}")
    if not text or not text.strip():
        raise StoreError("Text záznamu nesmie byť prázdny.")
    event_date = _date(event_date)
    now = utcnow()
    with writer_lock(data), connect(data) as connection:
        cursor = connection.execute(
            "INSERT INTO journal(event_date, kind, text, activity_id, plan_id, recorded_at, recorded_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (event_date, kind, text.strip(), activity_id, plan_id, now, recorded_by))
        entry_id = cursor.lastrowid
    row = {"entry_id": entry_id, "event_date": event_date, "kind": kind, "text": text.strip(),
           "activity_id": activity_id, "plan_id": plan_id, "recorded_at": now, "recorded_by": recorded_by}
    export_record(data, "journal", row)
    return row


def save_plan(data: DataPaths, plan_date: str, workout_type: str, segments: list[dict], note: str | None = None,
              created_by: str = "coach", conventions: dict | None = None) -> dict:
    """Store a prescription. Enforces the owner's format: exactly N equal segments, integer speeds."""
    plan_date = _date(plan_date)
    with connect(data, read_only=True) as connection:
        conv = conventions or get_conventions(connection)
    expected = int(conv.get("segments", "10"))
    min_speed = int(conv.get("min_running_speed_kmh", "7"))
    if len(segments) != expected:
        raise StoreError(f"Predpis musí mať presne {expected} úsekov, má {len(segments)}.")
    minutes = {float(s["minutes"]) for s in segments}
    if len(minutes) != 1:
        raise StoreError("Všetky úseky musia byť rovnako dlhé.")
    for index, segment in enumerate(segments, 1):
        speed, incline = segment["speed_kmh"], segment.get("incline_percent", 0)
        if not float(speed).is_integer() or not float(incline).is_integer():
            raise StoreError(f"Úsek {index}: rýchlosť a sklon musia byť celé čísla (desatiny rieši sklon).")
        if int(speed) < min_speed:
            raise StoreError(f"Úsek {index}: {speed} km/h je pod bežeckou rýchlosťou {min_speed} km/h.")
        if int(incline) < 0:
            raise StoreError(f"Úsek {index}: sklon nesmie byť záporný.")
    total = int(round(minutes.pop() * expected))
    now = utcnow()
    with writer_lock(data), connect(data) as connection:
        cursor = connection.execute(
            "INSERT INTO plans(plan_date, workout_type, total_minutes, status, note, created_by, created_at, updated_at) "
            "VALUES (?, ?, ?, 'proposed', ?, ?, ?, ?)", (plan_date, workout_type, total, note, created_by, now, now))
        plan_id = cursor.lastrowid
        connection.executemany(
            "INSERT INTO plan_segments(plan_id, seq, minutes, speed_kmh, incline_percent) VALUES (?, ?, ?, ?, ?)",
            [(plan_id, i, float(s["minutes"]), int(s["speed_kmh"]), int(s.get("incline_percent", 0)))
             for i, s in enumerate(segments, 1)])
        connection.execute(
            "INSERT INTO journal(event_date, kind, text, plan_id, recorded_at, recorded_by) VALUES (?, 'decision', ?, ?, ?, ?)",
            (plan_date, f"predpis {workout_type}, {total} min: " + format_segments(segments), plan_id, now, created_by))
    row = {"plan_id": plan_id, "plan_date": plan_date, "workout_type": workout_type, "total_minutes": total,
           "status": "proposed", "note": note, "segments": [
               {"seq": i, "minutes": float(s["minutes"]), "speed_kmh": int(s["speed_kmh"]),
                "incline_percent": int(s.get("incline_percent", 0))} for i, s in enumerate(segments, 1)],
           "created_by": created_by, "created_at": now}
    export_record(data, "plan", row)
    return row


def format_segments(segments: list[dict]) -> str:
    return "; ".join(f"{i}. {float(s['minutes']):g} min – {int(s['speed_kmh'])} km/h – {int(s.get('incline_percent', 0))} %"
                     for i, s in enumerate(segments, 1))


def set_plan_status(data: DataPaths, plan_id: int, status: str, activity_id: int | None = None) -> dict:
    if status not in PLAN_STATUSES:
        raise StoreError(f"Stav predpisu musí byť jeden z {PLAN_STATUSES}: {status!r}")
    now = utcnow()
    with writer_lock(data), connect(data) as connection:
        if not connection.execute("SELECT 1 FROM plans WHERE plan_id=?", (plan_id,)).fetchone():
            raise StoreError(f"Predpis {plan_id} neexistuje.")
        connection.execute("UPDATE plans SET status=?, activity_id=COALESCE(?, activity_id), updated_at=? WHERE plan_id=?",
                           (status, activity_id, now, plan_id))
    row = {"plan_id": plan_id, "status": status, "activity_id": activity_id, "updated_at": now}
    export_record(data, "plan_status", row)
    return row


def update_state(data: DataPaths, text: str, recorded_by: str = "coach") -> dict:
    if not text or not text.strip():
        raise StoreError("Stav trénera nesmie byť prázdny.")
    now = utcnow()
    with writer_lock(data), connect(data) as connection:
        connection.execute("INSERT OR REPLACE INTO coach_state(id, text, updated_at) VALUES (1, ?, ?)", (text.strip(), now))
    row = {"text": text.strip(), "updated_at": now, "recorded_by": recorded_by}
    export_record(data, "coach_state", row)
    return row


def add_summary(data: DataPaths, kind: str, period: str, text: str, recorded_by: str = "coach") -> dict:
    if kind not in SUMMARY_KINDS:
        raise StoreError(f"Druh zhrnutia musí byť jeden z {SUMMARY_KINDS}: {kind!r}")
    if not text or not text.strip():
        raise StoreError("Text zhrnutia nesmie byť prázdny.")
    now = utcnow()
    with writer_lock(data), connect(data) as connection:
        connection.execute("UPDATE summaries SET superseded=1 WHERE kind=? AND period=? AND superseded=0", (kind, period))
        cursor = connection.execute(
            "INSERT INTO summaries(kind, period, text, recorded_at) VALUES (?, ?, ?, ?)", (kind, period, text.strip(), now))
        summary_id = cursor.lastrowid
    row = {"summary_id": summary_id, "kind": kind, "period": period, "text": text.strip(), "recorded_at": now,
           "recorded_by": recorded_by}
    export_record(data, "summary", row)
    return row


def set_training_plan(data: DataPaths, goal: str, phases: list[dict], milestones: list[dict], reason: str | None = None,
                      recorded_by: str = "coach") -> dict:
    now = utcnow()
    with writer_lock(data), connect(data) as connection:
        row = connection.execute("SELECT COALESCE(MAX(version), 0) FROM training_plan").fetchone()
        version = int(row[0]) + 1
        connection.execute("UPDATE training_plan SET active=0 WHERE active=1")
        connection.execute(
            "INSERT INTO training_plan(version, goal, phases_json, milestones_json, reason, created_at, active) VALUES (?, ?, ?, ?, ?, ?, 1)",
            (version, goal, json.dumps(phases, ensure_ascii=False), json.dumps(milestones, ensure_ascii=False), reason, now))
    row = {"version": version, "goal": goal, "phases": phases, "milestones": milestones, "reason": reason,
           "created_at": now, "recorded_by": recorded_by}
    export_record(data, "training_plan", row)
    return row


def set_convention(data: DataPaths, key: str, value: str, note: str | None = None) -> dict:
    with writer_lock(data), connect(data) as connection:
        connection.execute("INSERT OR REPLACE INTO conventions(key, value, note) VALUES (?, ?, ?)", (key, value, note))
    row = {"key": key, "value": value, "note": note, "recorded_at": utcnow()}
    export_record(data, "convention", row)
    return row


# --- reads ----------------------------------------------------------------------------------

def _rows(cursor) -> list[dict]:
    return [dict(row) for row in cursor.fetchall()]


def get_conventions(connection: sqlite3.Connection) -> dict:
    return {row["key"]: row["value"] for row in connection.execute("SELECT key, value FROM conventions")}


def get_state(connection: sqlite3.Connection) -> dict | None:
    row = connection.execute("SELECT text, updated_at FROM coach_state WHERE id=1").fetchone()
    return dict(row) if row else None


def recent_runs(connection: sqlite3.Connection, limit: int = 3, days: int | None = None) -> list[dict]:
    sql = ("SELECT r.activity_id, r.date_local, r.start_time_local, r.sub_sport, r.total_distance, r.total_timer_time, "
           "r.total_elapsed_time, r.enhanced_avg_speed, r.avg_heart_rate, r.max_heart_rate, r.avg_running_cadence, "
           "r.avg_power, r.total_training_effect, r.total_anaerobic_training_effect, r.training_load_peak, r.num_laps, "
           "(SELECT value FROM feelings f WHERE f.activity_id=r.activity_id ORDER BY recorded_at DESC LIMIT 1) AS feeling, "
           "(SELECT plan_id FROM plans p WHERE p.activity_id=r.activity_id LIMIT 1) AS plan_id FROM runs r")
    params: list[Any] = []
    if days is not None:
        sql += " WHERE r.date_local >= date('now', ?)"; params.append(f"-{int(days)} days")
    sql += " ORDER BY r.start_time_utc DESC LIMIT ?"; params.append(int(limit))
    return _rows(connection.execute(sql, params))


def recent_journal(connection: sqlite3.Connection, days: int = 7, limit: int = 100) -> list[dict]:
    return _rows(connection.execute(
        "SELECT entry_id, event_date, kind, text, activity_id, plan_id, recorded_at, recorded_by FROM journal "
        "WHERE event_date >= date('now', ?) ORDER BY event_date DESC, recorded_at DESC LIMIT ?",
        (f"-{int(days)} days", int(limit))))


def search_journal(connection: sqlite3.Connection, query: str, limit: int = 20) -> dict:
    if not query or not query.strip():
        raise StoreError("Hľadaný výraz nesmie byť prázdny.")
    match = " ".join(f'"{token}"' for token in query.replace('"', " ").split())
    journal = _rows(connection.execute(
        "SELECT j.entry_id, j.event_date, j.kind, j.text, j.recorded_at FROM journal_fts f JOIN journal j ON j.entry_id=f.rowid "
        "WHERE journal_fts MATCH ? ORDER BY j.event_date DESC LIMIT ?", (match, int(limit))))
    summaries = _rows(connection.execute(
        "SELECT s.summary_id, s.kind, s.period, s.text, s.recorded_at FROM summaries_fts f JOIN summaries s ON s.summary_id=f.rowid "
        "WHERE summaries_fts MATCH ? AND s.superseded=0 ORDER BY s.period DESC LIMIT ?", (match, int(limit))))
    return {"query": query, "journal": journal, "summaries": summaries}


def latest_summary(connection: sqlite3.Connection, kind: str) -> dict | None:
    row = connection.execute("SELECT summary_id, kind, period, text, recorded_at FROM summaries WHERE kind=? AND superseded=0 "
                             "ORDER BY period DESC, recorded_at DESC LIMIT 1", (kind,)).fetchone()
    return dict(row) if row else None


def get_plan(connection: sqlite3.Connection, plan_date: str | None = None, plan_id: int | None = None) -> dict | None:
    if plan_id is not None:
        row = connection.execute("SELECT * FROM plans WHERE plan_id=?", (plan_id,)).fetchone()
    elif plan_date is not None:
        row = connection.execute("SELECT * FROM plans WHERE plan_date=? ORDER BY created_at DESC LIMIT 1",
                                 (_date(plan_date),)).fetchone()
    else:
        row = connection.execute("SELECT * FROM plans ORDER BY plan_date DESC, created_at DESC LIMIT 1").fetchone()
    if not row:
        return None
    plan = dict(row)
    plan["segments"] = _rows(connection.execute(
        "SELECT seq, minutes, speed_kmh, incline_percent FROM plan_segments WHERE plan_id=? ORDER BY seq", (plan["plan_id"],)))
    return plan


def list_plans(connection: sqlite3.Connection, limit: int = 20) -> list[dict]:
    return _rows(connection.execute(
        "SELECT plan_id, plan_date, workout_type, total_minutes, status, activity_id, created_by, created_at FROM plans "
        "ORDER BY plan_date DESC, created_at DESC LIMIT ?", (int(limit),)))


def get_training_plan(connection: sqlite3.Connection) -> dict | None:
    row = connection.execute("SELECT * FROM training_plan WHERE active=1 ORDER BY version DESC LIMIT 1").fetchone()
    if not row:
        return None
    plan = dict(row)
    plan["phases"] = json.loads(plan.pop("phases_json")); plan["milestones"] = json.loads(plan.pop("milestones_json"))
    return plan


def recent_health(connection: sqlite3.Connection, days: int = 3) -> list[dict]:
    return _rows(connection.execute(
        "SELECT * FROM daily_health WHERE date >= date('now', ?) ORDER BY date DESC", (f"-{int(days)} days",)))


def status(data: DataPaths) -> dict:
    with connect(data, read_only=True) as connection:
        counts = {table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                  for table in ("runs", "activities_other", "records", "plans", "journal", "summaries", "daily_health", "body_composition")}
        last_run = connection.execute("SELECT activity_id, date_local, total_distance, total_timer_time FROM runs "
                                      "ORDER BY start_time_utc DESC LIMIT 1").fetchone()
        meta = {row["key"]: row["value"] for row in connection.execute("SELECT key, value FROM meta")}
    backups = sorted(p.name for p in data.backups.glob("runs-*.sqlite3.gz")) if data.backups.is_dir() else []
    return {"data_dir": os.fspath(data.root), "database": os.fspath(data.database), "counts": counts,
            "last_run": dict(last_run) if last_run else None, "meta": meta, "backups": backups,
            "journal_export_lines": sum(1 for _ in data.journal_export.open(encoding="utf-8")) if data.journal_export.is_file() else 0}
