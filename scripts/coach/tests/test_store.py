import gzip
import json
import sqlite3
from datetime import date
from pathlib import Path

import pytest

from scripts.coach import db, schema
from scripts.coach.config import LOCAL_NAME, load_config, write_local_override
from scripts.coach.datadir import attach_data_dir, init_data_dir, open_data_dir


def test_config_layers(repo: Path, tmp_path: Path):
    config = load_config(repo)
    assert config.app_root == (tmp_path / "bimbo-trener-app")
    assert config.garmin_sync_enabled is False
    assert config.token_dir == tmp_path / "bimbo-trener-app" / "config" / "garmin"
    write_local_override(repo, {"garmin_sync_enabled": True, "data_dir": str(tmp_path / "other")})
    config = load_config(repo)
    assert config.garmin_sync_enabled is True and config.data_dir == tmp_path / "other"
    assert (repo / LOCAL_NAME).is_file()


def test_committed_config_must_not_enable_sync(repo: Path):
    path = repo / "bimbo-trener.json"
    raw = json.loads(path.read_text()); raw["garmin_sync_enabled"] = True
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError):
        load_config(repo)


def test_init_refuses_foreign_directory(tmp_path: Path):
    foreign = tmp_path / "foreign"; foreign.mkdir(); (foreign / "x.txt").write_text("x")
    with pytest.raises(ValueError):
        init_data_dir(foreign, "runs.sqlite3", "fit")
    with pytest.raises(ValueError):
        attach_data_dir(foreign, "runs.sqlite3", "fit")


def test_init_then_attach_and_open(tmp_path: Path):
    paths = init_data_dir(tmp_path / "d", "runs.sqlite3", "fit")
    assert paths.marker.is_file() and paths.fit_manual.is_dir()
    again = attach_data_dir(tmp_path / "d", "runs.sqlite3", "fit")
    assert again.marker.read_text() == paths.marker.read_text()
    assert open_data_dir(tmp_path / "d", "runs.sqlite3", "fit").root == paths.root
    with pytest.raises(ValueError):
        attach_data_dir(tmp_path / "d", "other.sqlite3", "fit")


def test_schema_created_and_no_wal(data):
    with db.connect(data) as connection:
        assert schema.current_version(connection) == schema.SCHEMA_VERSION
        assert connection.execute("PRAGMA journal_mode").fetchone()[0] == "delete"
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for table in ("runs", "laps", "records", "time_in_zone", "splits", "fit_raw", "daily_health", "body_composition",
                  "connect_raw", "plans", "plan_segments", "feelings", "journal", "summaries", "coach_state",
                  "training_plan", "conventions", "meta"):
        assert table in tables
    assert not data.database.with_name("runs.sqlite3-wal").exists()
    assert db.ensure_schema(data)["created"] is False


def test_migration_backs_up_first(data):
    with db.connect(data) as connection:
        connection.execute("UPDATE meta SET value='0' WHERE key='schema_version'")
    result = db.ensure_schema(data)
    assert result["migrated_from"] == 0
    assert any("pre-migration" in p.name for p in data.backups.iterdir())


def test_newer_schema_is_refused(data):
    with db.connect(data) as connection:
        connection.execute("UPDATE meta SET value='99' WHERE key='schema_version'")
    with pytest.raises(db.StoreError):
        db.ensure_schema(data)


def test_backup_rotation_and_restore(data):
    db.update_state(data, "stav 1")
    made = [db.backup_database(data, keep=3, today=date(2026, 10, d)) for d in (1, 2, 3, 4, 5)]
    assert all(made)
    names = sorted(p.name for p in data.backups.glob("runs-*.sqlite3.gz"))
    assert names == ["runs-2026-10-03.sqlite3.gz", "runs-2026-10-04.sqlite3.gz", "runs-2026-10-05.sqlite3.gz"]
    assert db.backup_database(data, keep=3, today=date(2026, 10, 5)) is None   # same day: no second backup
    with gzip.open(data.backups / "runs-2026-10-05.sqlite3.gz", "rb") as stream:
        assert stream.read(16) == b"SQLite format 3\x00"
    db.update_state(data, "stav 2")
    broken = db.restore_database(data, data.backups / "runs-2026-10-05.sqlite3.gz")
    assert broken.name.startswith("runs.sqlite3.broken-")
    with db.connect(data, read_only=True) as connection:
        assert db.get_state(connection)["text"] == "stav 1"


def test_pre_migration_backup_not_rotated(data):
    for d in (1, 2, 3):
        db.backup_database(data, keep=2, today=date(2026, 10, d))
    db.backup_database(data, tag="pre-migration", rotate=False, today=date(2026, 10, 4))
    db.backup_database(data, keep=2, today=date(2026, 10, 5))
    names = sorted(p.name for p in data.backups.glob("runs-*.sqlite3.gz"))
    assert "runs-2026-10-04-pre-migration.sqlite3.gz" in names and len(names) == 3


def test_own_writes_and_export(data):
    feeling = db.add_feeling(data, "2026-10-15", "ok", "koleno trochu ťahalo")
    entry = db.add_journal(data, "2026-10-15", "circumstance", "horúčava 36 °C")
    plan = db.save_plan(data, "2026-10-16", "easy", [{"minutes": 5, "speed_kmh": 8, "incline_percent": i % 2} for i in range(10)])
    state = db.update_state(data, "fáza: základ; na rade: dlhý beh")
    summary = db.add_summary(data, "week", "2026-W42", "4 behy, 28 km")
    db.add_summary(data, "week", "2026-W42", "4 behy, 28 km, opravené")
    tp = db.set_training_plan(data, "polmaratón", [{"name": "základ"}], [{"km": 15}])
    with db.connect(data, read_only=True) as connection:
        assert db.get_state(connection)["text"].startswith("fáza")
        assert db.get_plan(connection, "2026-10-16")["total_minutes"] == 50
        assert len(db.get_plan(connection, plan_id=plan["plan_id"])["segments"]) == 10
        assert db.latest_summary(connection, "week")["text"].endswith("opravené")
        assert db.get_training_plan(connection)["version"] == tp["version"] == 1
        kinds = [r["kind"] for r in db.recent_journal(connection, days=3650)]
        assert set(kinds) >= {"feeling", "circumstance", "decision"}
        hit = db.search_journal(connection, "koleno")
        assert hit["journal"] and "koleno" in hit["journal"][0]["text"]
        assert db.search_journal(connection, "horucava")["journal"]   # diacritics-insensitive
    export = db.read_export(data)
    assert [row["record"] for row in export] == ["feeling", "journal", "plan", "coach_state", "summary", "summary", "training_plan"]
    assert export[0]["data"]["feeling_id"] == feeling["feeling_id"] and export[1]["data"]["entry_id"] == entry["entry_id"]


def test_plan_format_is_enforced(data):
    ten = [{"minutes": 5, "speed_kmh": 8, "incline_percent": 0} for _ in range(10)]
    with pytest.raises(db.StoreError):
        db.save_plan(data, "2026-10-16", "easy", ten[:9])
    bad = [dict(s) for s in ten]; bad[3]["minutes"] = 6
    with pytest.raises(db.StoreError):
        db.save_plan(data, "2026-10-16", "easy", bad)
    bad = [dict(s) for s in ten]; bad[0]["speed_kmh"] = 8.4
    with pytest.raises(db.StoreError):
        db.save_plan(data, "2026-10-16", "easy", bad)
    bad = [dict(s) for s in ten]; bad[0]["speed_kmh"] = 6
    with pytest.raises(db.StoreError):
        db.save_plan(data, "2026-10-16", "easy", bad)
    with pytest.raises(db.StoreError):
        db.add_feeling(data, "2026-10-15", "great")
    with pytest.raises(db.StoreError):
        db.add_journal(data, "15.10.2026", "note", "x")


def test_writer_lock_is_exclusive(data):
    with db.writer_lock(data):
        with pytest.raises(db.StoreError):
            with db.writer_lock(data, wait_s=0.1):
                pass


def test_status(data):
    db.update_state(data, "x")
    result = db.status(data)
    assert result["counts"]["runs"] == 0 and result["journal_export_lines"] == 1
    assert result["meta"]["schema_version"] == str(schema.SCHEMA_VERSION)
