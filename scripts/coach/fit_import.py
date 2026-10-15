"""FIT file -> SQLite. Units exactly as FIT delivers them; missing fields stay NULL; nothing is estimated.

Every message of the file ends up in the database: mapped messages in their tables, everything
else (known but unmapped messages, unknown message numbers, unknown fields) in `fit_raw`.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

from garmin_fit_sdk import Decoder, Stream

from . import db
from .layout import DataPaths
from .paths import assert_plain_path

FIT_EPOCH = datetime(1989, 12, 31, tzinfo=timezone.utc)
ACTIVITY_FILE = re.compile(r"^(\d+)_ACTIVITY\.fit$", re.IGNORECASE)

RUN_COLUMNS = (
    "sport", "sub_sport", "sport_profile_name", "total_elapsed_time", "total_timer_time", "total_distance",
    "enhanced_avg_speed", "enhanced_max_speed", "avg_heart_rate", "max_heart_rate",
    "avg_running_cadence", "max_running_cadence", "avg_fractional_cadence", "max_fractional_cadence",
    "avg_power", "max_power", "normalized_power", "total_work", "total_strides", "total_cycles",
    "avg_step_length", "avg_vertical_ratio", "avg_vertical_oscillation", "avg_stance_time",
    "total_training_effect", "total_anaerobic_training_effect", "training_load_peak",
    "total_calories", "metabolic_calories", "num_laps", "trigger",
)
LAP_COLUMNS = (
    "total_elapsed_time", "total_timer_time", "total_distance", "enhanced_avg_speed", "enhanced_max_speed",
    "avg_heart_rate", "max_heart_rate", "avg_running_cadence", "max_running_cadence", "avg_power", "max_power",
    "normalized_power", "total_strides", "total_calories", "avg_step_length", "avg_vertical_ratio",
    "avg_vertical_oscillation", "avg_stance_time", "lap_trigger", "intensity",
)
RECORD_COLUMNS = (
    "distance", "enhanced_speed", "heart_rate", "cadence", "fractional_cadence", "power", "accumulated_power",
    "vertical_oscillation", "vertical_ratio", "step_length", "stance_time", "activity_type",
    "position_lat", "position_long", "altitude", "enhanced_altitude", "temperature",
)
EVENT_COLUMNS = ("event", "event_type", "event_group", "timer_trigger", "data")
SPLIT_COLUMNS = ("split_type", "total_elapsed_time", "total_timer_time", "total_distance", "avg_speed",
                 "avg_heart_rate", "max_heart_rate", "total_calories")
ZONE_COLUMNS = ("max_heart_rate", "resting_heart_rate", "threshold_heart_rate", "functional_threshold_power",
                "hr_calc_type", "pwr_calc_type")
MAPPED = {"session", "lap", "record", "event", "time_in_zone", "split"}


class ImportError_(RuntimeError):
    """Visible import failure."""


@dataclass
class Decoded:
    path: Path
    messages: dict
    errors: list = field(default_factory=list)

    def named(self, name: str) -> list[dict]:
        return self.messages.get(f"{name}_mesgs", [])


def decode(path: Path) -> Decoded:
    assert_plain_path(path)
    stream = Stream.from_file(str(path))
    decoder = Decoder(stream)
    if not decoder.is_fit():
        raise ImportError_(f"Nie je FIT súbor: {path}")
    messages, errors = decoder.read(convert_datetimes_to_dates=True, expand_components=True)
    return Decoded(path=path, messages=messages, errors=[str(e) for e in errors])


def _iso(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if isinstance(value, int):
        return (FIT_EPOCH + timedelta(seconds=value)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return str(value)


def _json_ready(value):
    if isinstance(value, datetime):
        return _iso(value)
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, (list, tuple)):
        return [_json_ready(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _json_ready(v) for k, v in value.items()}
    return value


def _pick(message: dict, columns: tuple[str, ...]) -> dict:
    out = {}
    for column in columns:
        value = message.get(column)
        if isinstance(value, datetime):
            value = _iso(value)
        elif isinstance(value, (list, tuple, dict)):
            value = json.dumps(_json_ready(value), ensure_ascii=False)
        out[column] = value
    return out


def activity_id_for(path: Path, decoded: Decoded) -> tuple[int, str]:
    """Garmin activity id from the file name; otherwise a local id derived from the FIT creation time."""
    match = ACTIVITY_FILE.match(path.name)
    if match:
        return int(match.group(1)), "garmin"
    file_id = decoded.named("file_id")
    created = file_id[0].get("time_created") if file_id else None
    if created is None:
        raise ImportError_(f"FIT súbor bez file_id.time_created a bez Garmin id v názve: {path.name}")
    seconds = int((created - FIT_EPOCH).total_seconds()) if isinstance(created, datetime) else int(created)
    return -seconds, "local"


def local_offset(decoded: Decoded, start_utc: datetime) -> timedelta | None:
    """activity.local_timestamp is 'local time pretending to be UTC'; the difference is the device offset."""
    for message in decoded.named("activity"):
        local = message.get("local_timestamp")
        if local is None:
            continue
        if isinstance(local, datetime):
            local_dt = local.replace(tzinfo=None)
        else:
            local_dt = (FIT_EPOCH + timedelta(seconds=int(local))).replace(tzinfo=None)
        stamp = message.get("timestamp")
        if isinstance(stamp, datetime):
            base = stamp.astimezone(timezone.utc).replace(tzinfo=None)
        else:
            base = start_utc.replace(tzinfo=None)
        return local_dt - base
    return None


def import_file(data: DataPaths, path: Path, source: str) -> dict:
    """Import one FIT file idempotently. Returns a summary; raises ImportError_ on a hard failure."""
    decoded = decode(path)
    sessions = decoded.named("session")
    if not sessions:
        raise ImportError_(f"FIT súbor nemá správu session: {path.name}")
    session = sessions[0]
    activity_id, id_kind = activity_id_for(path, decoded)
    start = session.get("start_time") or session.get("timestamp")
    if not isinstance(start, datetime):
        raise ImportError_(f"Session bez start_time: {path.name}")
    start_utc = start.astimezone(timezone.utc)
    offset = local_offset(decoded, start_utc)
    start_local = (start_utc + offset).replace(tzinfo=None) if offset is not None else None
    date_local = (start_local or start_utc).date().isoformat()
    sport = session.get("sport")
    is_run = sport == "running"
    device = next(iter(decoded.named("file_id")), {})
    now = db.utcnow()
    fit_path = str(path.relative_to(data.root)) if path.is_relative_to(data.root) else str(path)

    with db.writer_lock(data), db.connect(data) as connection:
        for table in ("runs", "activities_other"):
            existing = connection.execute(f"SELECT activity_id, fit_path FROM {table} WHERE activity_id=? OR start_time_utc=?",
                                          (activity_id, _iso(start_utc))).fetchone()
            if existing:
                return {"activity_id": existing["activity_id"], "imported": False, "reason": "already_imported",
                        "table": table, "fit_path": existing["fit_path"], "file": path.name}
        if is_run:
            row = _pick(session, RUN_COLUMNS)
            row.update(activity_id=activity_id, start_time_utc=_iso(start_utc),
                       start_time_local=start_local.isoformat() if start_local else None, date_local=date_local,
                       device_product=str(device.get("garmin_product") or device.get("product") or "") or None,
                       device_serial=str(device.get("serial_number")) if device.get("serial_number") is not None else None,
                       device_software_version=next((m.get("software_version") for m in decoded.named("device_info")
                                                     if m.get("software_version") is not None), None),
                       fit_path=fit_path, source=source, imported_at=now,
                       import_errors="; ".join(decoded.errors) or None)
            _insert(connection, "runs", row)
            _import_details(connection, activity_id, decoded)
            table = "runs"
        else:
            row = _pick(session, ("sport", "sub_sport", "sport_profile_name", "total_elapsed_time", "total_timer_time",
                                  "total_distance", "avg_heart_rate", "max_heart_rate", "total_calories"))
            row.update(activity_id=activity_id, start_time_utc=_iso(start_utc), date_local=date_local,
                       device_product=str(device.get("garmin_product") or device.get("product") or "") or None,
                       fit_path=fit_path, source=source, imported_at=now,
                       session_json=json.dumps(_json_ready({str(k): v for k, v in session.items()}), ensure_ascii=False))
            _insert(connection, "activities_other", row)
            _import_raw(connection, activity_id, decoded, include_mapped=True)
            table = "activities_other"
        db.set_meta(connection, "last_import", now)
        paired = _pair_plan(connection, activity_id, date_local) if is_run else None
    return {"activity_id": activity_id, "id_kind": id_kind, "imported": True, "table": table, "date_local": date_local,
            "fit_path": fit_path, "file": path.name, "errors": decoded.errors, "paired_plan_id": paired,
            "records": len(decoded.named("record")), "laps": len(decoded.named("lap"))}


def _insert(connection, table: str, row: dict) -> None:
    columns = ", ".join(row)
    marks = ", ".join("?" for _ in row)
    connection.execute(f"INSERT INTO {table}({columns}) VALUES ({marks})", tuple(row.values()))


def _import_details(connection, activity_id: int, decoded: Decoded) -> None:
    for index, lap in enumerate(decoded.named("lap")):
        row = _pick(lap, LAP_COLUMNS)
        row.update(activity_id=activity_id, lap_index=index, start_time_utc=_iso(lap.get("start_time")))
        _insert(connection, "laps", row)
    rows = []
    for seq, record in enumerate(decoded.named("record")):
        row = _pick(record, RECORD_COLUMNS)
        row.update(activity_id=activity_id, timestamp_utc=_iso(record.get("timestamp")), seq=seq)
        rows.append(row)
    if rows:
        columns = list(rows[0])
        connection.executemany(f"INSERT INTO records({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)})",
                               [tuple(r[c] for c in columns) for r in rows])
    for seq, event in enumerate(decoded.named("event")):
        row = _pick(event, EVENT_COLUMNS)
        row.update(activity_id=activity_id, timestamp_utc=_iso(event.get("timestamp")), seq=seq)
        _insert(connection, "events", row)
    snapshot = None
    for message in decoded.named("time_in_zone"):
        row = {"activity_id": activity_id, "reference_mesg": str(message.get("reference_mesg")),
               "reference_index": int(message.get("reference_index") or 0)}
        for key in ("time_in_hr_zone", "time_in_power_zone", "time_in_speed_zone", "time_in_cadence_zone"):
            value = message.get(key)
            row[key] = json.dumps(_json_ready(value)) if value is not None else None
        connection.execute("INSERT OR REPLACE INTO time_in_zone(activity_id, reference_mesg, reference_index, time_in_hr_zone, "
                           "time_in_power_zone, time_in_speed_zone, time_in_cadence_zone) VALUES (?,?,?,?,?,?,?)",
                           tuple(row.values()))
        if row["reference_mesg"] == "session" and snapshot is None:
            snapshot = _pick(message, ZONE_COLUMNS)
            for key in ("hr_zone_high_boundary", "power_zone_high_boundary"):
                value = message.get(key)
                snapshot[key] = json.dumps(_json_ready(value)) if value is not None else None
    if snapshot:
        snapshot["activity_id"] = activity_id
        _insert(connection, "zone_snapshot", snapshot)
    for index, split in enumerate(decoded.named("split")):
        row = _pick(split, SPLIT_COLUMNS)
        row.update(activity_id=activity_id, split_index=index, start_time_utc=_iso(split.get("start_time")),
                   end_time_utc=_iso(split.get("end_time")))
        _insert(connection, "splits", row)
    _import_raw(connection, activity_id, decoded, include_mapped=False)


def _import_raw(connection, activity_id: int, decoded: Decoded, include_mapped: bool) -> None:
    """Everything not mapped above: unmapped known messages, unknown message numbers, unknown fields."""
    rows = []
    for key, messages in decoded.messages.items():
        name = key[:-6] if isinstance(key, str) and key.endswith("_mesgs") else str(key)
        known = isinstance(key, str) and key.endswith("_mesgs")
        for index, message in enumerate(messages):
            if known and name in MAPPED and not include_mapped:
                extra = {str(k): v for k, v in message.items() if not isinstance(k, str)}
                if extra:
                    rows.append((activity_id, f"{name}.unknown_fields", index, json.dumps(_json_ready(extra), ensure_ascii=False)))
                continue
            rows.append((activity_id, name, index, json.dumps(_json_ready({str(k): v for k, v in message.items()}), ensure_ascii=False)))
    if rows:
        connection.executemany("INSERT OR REPLACE INTO fit_raw(activity_id, mesg_name, mesg_index, fields_json) VALUES (?,?,?,?)", rows)


def _pair_plan(connection, activity_id: int, date_local: str) -> int | None:
    candidates = connection.execute(
        "SELECT plan_id FROM plans WHERE plan_date=? AND status='proposed' AND activity_id IS NULL ORDER BY created_at DESC",
        (date_local,)).fetchall()
    if len(candidates) != 1:
        return None
    plan_id = candidates[0]["plan_id"]
    connection.execute("UPDATE plans SET status='done', activity_id=?, updated_at=? WHERE plan_id=?",
                       (activity_id, db.utcnow(), plan_id))
    return plan_id


def pending_files(data: DataPaths) -> list[Path]:
    """FIT files in fit/ and fit/manual/ whose path is not yet recorded in the database."""
    with db.connect(data, read_only=True) as connection:
        known = {row[0] for row in connection.execute("SELECT fit_path FROM runs UNION ALL SELECT fit_path FROM activities_other")}
    files = []
    for folder in (data.fit, data.fit_manual):
        if folder.is_dir():
            files.extend(sorted(p for p in folder.glob("*.fit") if p.is_file()))
    return [p for p in files if str(p.relative_to(data.root)) not in known]


def import_pending(data: DataPaths) -> dict:
    """Import every new FIT file; a failing file is reported and skipped, never hidden."""
    results, failures = [], []
    for path in pending_files(data):
        source = "manual_fit" if path.parent == data.fit_manual else "garmin_sync"
        try:
            results.append(import_file(data, path, source))
        except Exception as error:  # noqa: BLE001 - each failure is surfaced in the summary
            failures.append({"file": path.name, "error": f"{type(error).__name__}: {error}"})
    return {"imported": [r for r in results if r["imported"]], "skipped": [r for r in results if not r["imported"]],
            "failed": failures}
