import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.coach import cli, db
from scripts.coach.analysis import analysis, compare_plan_run, equivalent_speed_kmh
from scripts.coach.render import render
from scripts.coach.rebuild import rebuild
from scripts.coach.tests.fit_builder import build_run

START = datetime(2026, 10, 14, 4, 52, 57, tzinfo=timezone.utc)
TEN = json.dumps([{"minutes": 1, "speed_kmh": 8, "incline_percent": i % 2} for i in range(10)])


def run_cli(capsys, repo: Path, *args) -> tuple[int, dict | list | None]:
    code = cli.main(["--root", str(repo), "--compact", *args])
    out = capsys.readouterr().out.strip().splitlines()
    return code, (json.loads(out[-1]) if out else None)


def test_cli_daily_flow(capsys, repo: Path, tmp_path: Path):
    code, result = run_cli(capsys, repo, "init")
    assert code == 0 and result["schema"]["created"]
    data = db.DataPaths(tmp_path / "data")
    build_run(data.fit / "1001_ACTIVITY.fit", START, laps=1, seconds_per_lap=600, local_offset_hours=2)
    code, result = run_cli(capsys, repo, "plan", "add", "2026-10-14", "easy", "--segments", TEN)
    assert code == 0 and result["total_minutes"] == 10
    code, result = run_cli(capsys, repo, "import")
    assert code == 0 and len(result["imported"]) == 1 and result["imported"][0]["paired_plan_id"] == 1
    code, _ = run_cli(capsys, repo, "feeling", "2026-10-14", "ok", "--text", "v pohode", "--activity-id", "1001")
    assert code == 0
    code, _ = run_cli(capsys, repo, "journal", "add", "2026-10-14", "circumstance", "ľavé koleno trochu ťahalo")
    assert code == 0
    code, _ = run_cli(capsys, repo, "state", "set", "fáza základ; na rade dlhý beh")
    assert code == 0
    code, _ = run_cli(capsys, repo, "summary", "add", "week", "2026-W41", "1 beh, 1,3 km")
    assert code == 0
    code, recent = run_cli(capsys, repo, "recent", "--days", "3650")
    assert code == 0 and recent["state"]["text"].startswith("fáza") and recent["runs"][0]["feeling"] == "ok"
    assert recent["runs"][0]["plan_id"] == 1 and recent["week_summary"]["period"] == "2026-W41"
    code, hit = run_cli(capsys, repo, "journal", "search", "koleno")
    assert code == 0 and hit["journal"]
    code, cmp = run_cli(capsys, repo, "analysis", "compare", "--activity-id", "1001")
    assert code == 0 and len(cmp["segments"]) == 10 and cmp["segments"][0]["actual_speed_kmh"] == 7.92
    assert cmp["segments"][1]["planned_equivalent_kmh"] == 8.4
    code, vol = run_cli(capsys, repo, "analysis", "weekly_volume")
    assert code == 0 and vol["source"] == "derived"
    code, rendered = run_cli(capsys, repo, "render")
    assert code == 0 and "STAV.md" in rendered["written"] and (data.preview / "behy.md").is_file()
    assert "koleno" in (data.preview / "dennik" / "2026-10.md").read_text(encoding="utf-8")
    code, backup = run_cli(capsys, repo, "backup")
    assert code == 0 and backup["backup"]
    code, status = run_cli(capsys, repo, "status")
    assert code == 0 and status["counts"]["runs"] == 1 and status["backups"]


def test_cli_without_data_dir_is_77(capsys, repo: Path):
    code, _ = run_cli(capsys, repo, "status")
    assert code == 77


def test_cli_rejects_bad_plan(capsys, repo: Path):
    run_cli(capsys, repo, "init")
    code, _ = run_cli(capsys, repo, "plan", "add", "2026-10-14", "easy", "--segments", json.dumps([{"minutes": 5, "speed_kmh": 8}] * 9))
    assert code == 1


def test_rebuild_restores_own_data(repo: Path, data):
    from scripts.coach.config import load_config
    config = load_config(repo)
    build_run(data.fit / "1001_ACTIVITY.fit", START, laps=1, seconds_per_lap=30)
    from scripts.coach.fit_import import import_pending
    import_pending(data)
    db.add_feeling(data, "2026-10-14", "easy", "ľahké", 1001)
    db.add_journal(data, "2026-10-15", "circumstance", "horúčava")
    plan = db.save_plan(data, "2026-10-16", "tempo", [{"minutes": 5, "speed_kmh": 9, "incline_percent": 0}] * 10)
    db.set_plan_status(data, plan["plan_id"], "skipped")
    db.update_state(data, "stav A"); db.update_state(data, "stav B")
    db.add_summary(data, "month", "2026-10", "október")
    before = db.status(data)["counts"]
    result = rebuild(data, config)
    assert result["previous_database"] and result["fit"]["imported"] == 1 and result["skipped"] == []
    after = db.status(data)["counts"]
    assert after == before
    with db.connect(data, read_only=True) as c:
        assert db.get_state(c)["text"] == "stav B"
        assert db.get_plan(c, "2026-10-16")["status"] == "skipped"
        assert db.latest_summary(c, "month")["text"] == "október"
    assert len(db.read_export(data)) == 7


def test_equivalent_speed_and_drift(data):
    assert equivalent_speed_kmh(8, 2, {"incline_percent_per_0_4_kmh": "1"}) == 8.8
    build_run(data.fit / "1003_ACTIVITY.fit", START, laps=1, seconds_per_lap=1900)
    from scripts.coach.fit_import import import_pending
    import_pending(data)
    with db.connect(data, read_only=True) as c:
        drift = analysis(c, "drift", activity_id=1003)
        assert drift["drift_bpm"] is not None and drift["comparable_speed"] is True
        pace = analysis(c, "pace_at_hr", reference_hr=120, tolerance=30)
        assert pace["points"] and pace["points"][0]["activity_id"] == 1003
        assert compare_plan_run(c, 1003)["plan"] is None
        assert isinstance(analysis(c, "warnings")["warnings"], list)
