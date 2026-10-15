import io
import json
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

import pytest
from garminconnect import GarminConnectAuthenticationError, GarminConnectTooManyRequestsError

from scripts.coach import db, garmin_sync
from scripts.coach.config import load_config, write_local_override
from scripts.coach.layout import AppPaths
from scripts.coach.tests.fit_builder import build_run

START = datetime(2026, 10, 14, 4, 52, 57, tzinfo=timezone.utc)


class FakeClient:
    """Minimal stand-in for garminconnect.Garmin: activities list, ORIGINAL download as ZIP, health calls."""
    class ActivityDownloadFormat:
        ORIGINAL = "ORIGINAL"

    def __init__(self, activities, fit_bytes, fail_with=None):
        self.activities, self.fit_bytes, self.fail_with = activities, fit_bytes, fail_with
        self.calls = []

    def login(self, tokenstore):
        if self.fail_with:
            raise self.fail_with
        self.calls.append(("login", tokenstore))

    def get_activities_by_date(self, start, end=None, activitytype=None, sortorder=None):
        self.calls.append(("activities", start, end)); return self.activities

    def download_activity(self, activity_id, dl_fmt=None):
        self.calls.append(("download", activity_id, dl_fmt))
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr(f"{activity_id}_ACTIVITY.fit", self.fit_bytes)
        return buffer.getvalue()

    def get_user_summary(self, d): return {"restingHeartRate": 49, "totalSteps": 7650, "bodyBatteryHighestValue": 80, "bodyBatteryLowestValue": 20,
                                           "averageStressLevel": 25, "maxStressLevel": 60, "totalKilocalories": 2500, "activeKilocalories": 500,
                                           "moderateIntensityMinutes": 24, "vigorousIntensityMinutes": 17, "minHeartRate": 45, "maxHeartRate": 134}
    def get_rhr_day(self, d): return {"allMetrics": {"metricsMap": {"WELLNESS_RESTING_HEART_RATE": [{"value": 49}]}}}
    def get_heart_rates(self, d): return {"heartRateValues": [[1, 60], [2, 61]]}
    def get_sleep_data(self, d): return {"dailySleepDTO": {"sleepTimeSeconds": 25200, "deepSleepSeconds": 5000, "lightSleepSeconds": 15000,
                                                            "remSleepSeconds": 5200, "awakeSleepSeconds": 600, "sleepScores": {"overall": {"value": 78}}}}
    def get_hrv_data(self, d): return {"hrvSummary": {"lastNightAvg": 42, "weeklyAvg": 40, "status": "BALANCED"}}
    def get_stress_data(self, d): return {"avgStressLevel": 25, "maxStressLevel": 60}
    def get_body_battery(self, s, e=None): return [{"date": s, "charged": 60, "drained": 55}]
    def get_training_readiness(self, d): return [{"score": 71, "level": "HIGH"}]
    def get_training_status(self, d): return {"mostRecentTrainingStatus": {"latestTrainingStatusData": {"x": {"trainingStatus": 3}}}}
    def get_respiration_data(self, d): return {"avgSleepRespirationValue": 14.0}
    def get_spo2_data(self, d): return {"averageSpO2": 95}
    def get_body_composition(self, s, e=None): return {"dateWeightList": [{"timestampGMT": 1760400000000, "calendarDate": s, "weight": 93900,
                                                                            "bmi": 28.3, "bodyFat": 24.0, "muscleMass": 35000, "boneMass": 3700,
                                                                            "bodyWater": 52.0, "sourceType": "INDEX_SCALE"}]}


@pytest.fixture
def enabled(repo: Path, data, tmp_path: Path, monkeypatch):
    write_local_override(repo, {"garmin_sync_enabled": True})
    config = load_config(repo)
    token_dir = config.token_dir; token_dir.mkdir(parents=True)
    (token_dir / "garmin_tokens.json").write_text("{}")
    fit = build_run(tmp_path / "sample.fit", START, laps=1, seconds_per_lap=30).read_bytes()
    return config, data, fit, monkeypatch


def test_sync_disabled_is_77(repo: Path, data):
    config = load_config(repo)
    result, code = garmin_sync.sync(config, data)
    assert code == 77 and "nie je sťahovanie nastavené" in result["message"]


def test_sync_without_tokens_is_77_without_requests(repo: Path, data, monkeypatch):
    write_local_override(repo, {"garmin_sync_enabled": True})
    config = load_config(repo)
    monkeypatch.setattr(garmin_sync, "make_client", lambda *a, **k: pytest.fail("no request expected"))
    result, code = garmin_sync.sync(config, data)
    assert code == 77 and "login" in result["message"]


def test_sync_downloads_imports_and_backs_up(enabled):
    config, data, fit, monkeypatch = enabled
    client = FakeClient([{"activityId": 1001, "activityName": "Beh na bežiacom páse", "startTimeLocal": "2026-10-14 06:52:57", "distance": 66.0}], fit)
    monkeypatch.setattr(garmin_sync, "make_client", lambda *a, **k: client)
    result, code = garmin_sync.sync(config, data, today=date(2026, 10, 15))
    assert code == 0, result
    assert result["backup"] and Path(result["backup"]).is_file()
    assert result["new_activities"][0]["activity_id"] == 1001 and len(result["imported"]["imported"]) == 1
    assert ("download", "1001", "ORIGINAL") in client.calls
    assert result["health_days"] == ["2026-10-15", "2026-10-14"]
    assert result["message"].startswith("1 nový beh")
    with db.connect(data, read_only=True) as c:
        assert db.get_meta(c, "last_sync")
        health = db.recent_health(c, days=3650)
        assert health[0]["resting_heart_rate"] == 49 and health[0]["sleep_score"] == 78 and health[0]["hrv_status"] == "BALANCED"
        assert c.execute("SELECT COUNT(*) FROM connect_raw").fetchone()[0] == 24
        comp = c.execute("SELECT weight_g, source FROM body_composition").fetchone()
        assert comp["weight_g"] == 93900 and comp["source"] == "INDEX_SCALE"
    # second run: nothing new -> no second backup, no writes
    before = sorted(p.name for p in data.backups.iterdir())
    result, code = garmin_sync.sync(config, data, today=date(2026, 10, 15))
    assert code == 0 and result["message"] == "Nič nové." and result["backup"] is None
    assert sorted(p.name for p in data.backups.iterdir()) == before


def test_sync_rate_limit_sets_cooldown_and_75(enabled):
    config, data, fit, monkeypatch = enabled
    client = FakeClient([], fit, fail_with=GarminConnectTooManyRequestsError("429"))
    monkeypatch.setattr(garmin_sync, "make_client", lambda *a, **k: client)
    result, code = garmin_sync.sync(config, data)
    assert code == 75 and "429" in result["message"]
    assert garmin_sync.cooldown_until(AppPaths(config.app_root)) is not None
    monkeypatch.setattr(garmin_sync, "make_client", lambda *a, **k: pytest.fail("cooldown must prevent requests"))
    result, code = garmin_sync.sync(config, data)
    assert code == 0 and "ďalší pokus" in result["message"].lower()


def test_sync_auth_failure_is_77(enabled):
    config, data, fit, monkeypatch = enabled
    client = FakeClient([], fit, fail_with=GarminConnectAuthenticationError("expired"))
    monkeypatch.setattr(garmin_sync, "make_client", lambda *a, **k: client)
    result, code = garmin_sync.sync(config, data)
    assert code == 77


def test_extract_fit_zip_and_bare():
    bare = b"\x0e\x10\x00\x00\x00\x00\x00\x00.FIT\x00\x00" + b"x" * 10
    assert garmin_sync.extract_fit(bare) == bare
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("a.fit", bare)
    assert garmin_sync.extract_fit(buffer.getvalue()) == bare
    assert garmin_sync.extract_fit(b"<gpx/>") is None
