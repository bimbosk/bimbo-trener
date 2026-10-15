import json
from datetime import datetime, timezone

import pytest

from scripts.coach import db, fit_import
from scripts.coach.tests.fit_builder import build_run

START = datetime(2026, 10, 14, 4, 52, 57, tzinfo=timezone.utc)


def test_builder_round_trip(tmp_path):
    path = build_run(tmp_path / "1001_ACTIVITY.fit", START, laps=2, seconds_per_lap=30)
    decoded = fit_import.decode(path)
    assert decoded.errors == []
    session = decoded.named("session")[0]
    assert session["sport"] == "running" and session["sub_sport"] == "treadmill"
    assert session["avg_vertical_oscillation"] == 85.0 and session["num_laps"] == 2
    assert len(decoded.named("record")) == 61 and len(decoded.named("lap")) == 2


def test_import_run_and_idempotence(data):
    path = build_run(data.fit / "1001_ACTIVITY.fit", START, laps=2, seconds_per_lap=30, local_offset_hours=2)
    result = fit_import.import_file(data, path, "garmin_sync")
    assert result["imported"] and result["activity_id"] == 1001 and result["date_local"] == "2026-10-14"
    assert result["records"] == 61 and result["laps"] == 2 and result["errors"] == []
    again = fit_import.import_file(data, path, "garmin_sync")
    assert again["imported"] is False and again["reason"] == "already_imported"
    with db.connect(data, read_only=True) as connection:
        run = dict(connection.execute("SELECT * FROM runs WHERE activity_id=1001").fetchone())
        assert run["start_time_utc"] == "2026-10-14T04:52:57Z"
        assert run["start_time_local"] == "2026-10-14T06:52:57"
        assert run["sub_sport"] == "treadmill" and run["avg_stance_time"] == 300.0 and run["total_distance"] == 132.0
        assert run["device_product"] == "venu4" and run["fit_path"] == "fit/1001_ACTIVITY.fit"
        assert connection.execute("SELECT COUNT(*) FROM records WHERE activity_id=1001").fetchone()[0] == 61
        assert connection.execute("SELECT COUNT(*) FROM laps WHERE activity_id=1001").fetchone()[0] == 2
        assert connection.execute("SELECT COUNT(*) FROM events WHERE activity_id=1001").fetchone()[0] == 2
        zone = dict(connection.execute("SELECT * FROM zone_snapshot WHERE activity_id=1001").fetchone())
        assert zone["functional_threshold_power"] == 353 and json.loads(zone["hr_zone_high_boundary"]) == [88, 106, 123, 141, 158, 176]
        tiz = connection.execute("SELECT time_in_hr_zone FROM time_in_zone WHERE activity_id=1001 AND reference_mesg='session'").fetchone()
        assert json.loads(tiz[0])[1] == 50.0
        assert connection.execute("SELECT COUNT(*) FROM splits WHERE activity_id=1001").fetchone()[0] == 1
        raw_names = {row[0] for row in connection.execute("SELECT DISTINCT mesg_name FROM fit_raw WHERE activity_id=1001")}
        assert {"file_id", "device_info", "sport", "activity"} <= raw_names
        assert "record" not in raw_names
        rec = connection.execute("SELECT heart_rate, enhanced_speed, vertical_oscillation FROM records WHERE activity_id=1001 AND seq=10").fetchone()
        assert rec["heart_rate"] == 110 and rec["enhanced_speed"] == 2.2 and rec["vertical_oscillation"] == 85.0
        assert db.get_meta(connection, "last_import")


def test_local_id_and_duplicate_by_start_time(data):
    build_run(data.fit_manual / "2026-10-14-06-52-57.fit", START, laps=1, seconds_per_lap=20)
    first = fit_import.import_pending(data)
    assert len(first["imported"]) == 1 and first["imported"][0]["id_kind"] == "local" and first["imported"][0]["activity_id"] < 0
    build_run(data.fit / "7777_ACTIVITY.fit", START, laps=1, seconds_per_lap=20)
    second = fit_import.import_pending(data)
    assert second["imported"] == [] and second["skipped"][0]["reason"] == "already_imported"


def test_other_sport_goes_to_activities_other(data):
    path = build_run(data.fit / "5005_ACTIVITY.fit", START, laps=1, seconds_per_lap=20, sport="cycling", sub_sport="generic")
    result = fit_import.import_file(data, path, "garmin_sync")
    assert result["table"] == "activities_other"
    with db.connect(data, read_only=True) as connection:
        assert connection.execute("SELECT sport FROM activities_other WHERE activity_id=5005").fetchone()[0] == "cycling"
        assert connection.execute("SELECT COUNT(*) FROM fit_raw WHERE activity_id=5005 AND mesg_name='record'").fetchone()[0] == 21


def test_plan_pairing(data):
    db.save_plan(data, "2026-10-14", "easy", [{"minutes": 5, "speed_kmh": 8, "incline_percent": 0} for _ in range(10)])
    path = build_run(data.fit / "1002_ACTIVITY.fit", START, laps=1, seconds_per_lap=20)
    result = fit_import.import_file(data, path, "garmin_sync")
    assert result["paired_plan_id"] == 1
    with db.connect(data, read_only=True) as connection:
        plan = db.get_plan(connection, "2026-10-14")
        assert plan["status"] == "done" and plan["activity_id"] == 1002


def test_not_a_fit_file_is_reported(data):
    (data.fit_manual / "junk.fit").write_bytes(b"not a fit file at all")
    result = fit_import.import_pending(data)
    assert result["failed"] and "junk.fit" == result["failed"][0]["file"]
