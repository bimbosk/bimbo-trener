"""Garmin Connect -> data directory: new activities as original FIT, daily health data, body composition.

Rules (docs/coach/garmin-sync.md): never log in with a password unattended; no tokens -> exit 77 without a
single request; 429 -> cooldown and exit 75; nothing new -> no backup and no write; one request per second.
"""
from __future__ import annotations

import io
import json
import logging
import os
import stat
import sys
import time
import zipfile
from datetime import date, datetime, timedelta, timezone
from getpass import getpass
from pathlib import Path

from . import db
from .config import Config
from .fit_import import import_pending
from .layout import AppPaths, DataPaths
from .paths import assert_plain_path, atomic_write_bytes

EXIT_OK, EXIT_ERROR, EXIT_TEMPFAIL, EXIT_NOPERM = 0, 1, 75, 77
log = logging.getLogger("bimbo.sync")

HEALTH_CALLS = (
    ("user_summary", "get_user_summary", 1), ("rhr", "get_rhr_day", 1), ("heart_rates", "get_heart_rates", 1),
    ("sleep", "get_sleep_data", 1), ("hrv", "get_hrv_data", 1), ("stress", "get_stress_data", 1),
    ("body_battery", "get_body_battery", 2), ("training_readiness", "get_training_readiness", 1),
    ("training_status", "get_training_status", 1), ("respiration", "get_respiration_data", 1),
    ("spo2", "get_spo2_data", 1), ("body_composition", "get_body_composition", 2),
)


class SyncOutcome(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message); self.code = code; self.message = message


def _progress(message: str) -> None:
    """Progress lines go to stderr so stdout stays JSON for the CLI contract; sync.ps1 shows both."""
    print(message, file=sys.stderr, flush=True)
    log.info(message)


def setup_logging(app: AppPaths) -> None:
    app.logs.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(app.logs / "sync.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    log.addHandler(handler); log.setLevel(logging.INFO)


# --- cooldown ------------------------------------------------------------------------------

def cooldown_until(app: AppPaths) -> datetime | None:
    try:
        until = datetime.fromisoformat(app.cooldown_file.read_text(encoding="utf-8").strip())
    except (FileNotFoundError, ValueError):
        return None
    return until if datetime.now(timezone.utc) < until else None


def set_cooldown(app: AppPaths, minutes: int) -> datetime:
    until = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    atomic_write_bytes(app.cooldown_file, until.isoformat(timespec="seconds").encode("utf-8"))
    return until


# --- client ---------------------------------------------------------------------------------

def _restrict(path: Path) -> None:
    try:
        os.chmod(path, stat.S_IRWXU)
    except OSError:
        pass   # Windows ACLs are set by the installer (icacls)


def make_client(config: Config, **kwargs):
    from garminconnect import Garmin
    return Garmin(**kwargs)


def interactive_login(config: Config, compact: bool = False) -> int:
    """One-time login in a console: email, hidden password, MFA code. Stores tokens; never the password."""
    if sys.stdin is None or not sys.stdin.isatty():
        print(json.dumps({"error": "Prihlásenie vyžaduje interaktívnu konzolu (python.exe, nie pythonw.exe)."}), file=sys.stderr)
        return EXIT_ERROR
    token_dir = config.token_dir
    assert_plain_path(token_dir)
    token_dir.mkdir(parents=True, exist_ok=True); _restrict(token_dir)
    email = input("Garmin e-mail: ").strip()
    password = getpass("Garmin heslo (nezobrazuje sa): ")
    client = make_client(config, email=email, password=password, prompt_mfa=lambda: input("MFA kód: ").strip())
    del password
    try:
        client.login(str(token_dir))
        client.client.dump(str(token_dir))   # login() suppresses dump errors; make a write failure visible now
    except Exception as error:  # noqa: BLE001 - reported without the response body
        print(json.dumps({"error": f"Prihlásenie zlyhalo ({type(error).__name__}). Neopakujte rýchlo; pri 429 počkajte hodiny."}),
              file=sys.stderr)
        return EXIT_TEMPFAIL
    token_file = token_dir / "garmin_tokens.json"
    if not token_file.is_file():
        print(json.dumps({"error": f"Token sa nezapísal do {token_dir}."}), file=sys.stderr)
        return EXIT_ERROR
    _restrict(token_file)
    print(json.dumps({"login": "ok", "token_dir": str(token_dir), "next": "zapnite sťahovanie: garmin_sync_enabled=true v bimbo-trener.local.json"},
                     ensure_ascii=False))
    return EXIT_OK


def token_login(config: Config):
    token_file = config.token_dir / "garmin_tokens.json"
    if not token_file.is_file():
        raise SyncOutcome(EXIT_NOPERM, f"Chýba prihlásenie do Garminu ({token_file}). Spustite: bimbo-trener login")
    client = make_client(config)
    client.login(str(config.token_dir))   # loads and refreshes tokens; never prompts
    return client


# --- helpers -------------------------------------------------------------------------------

def extract_fit(blob: bytes) -> bytes | None:
    if blob[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            for member in archive.namelist():
                if member.lower().endswith(".fit"):
                    return archive.read(member)
        return None
    if len(blob) >= 12 and blob[8:12] == b".FIT":
        return blob
    return None


def _classify(error: Exception) -> SyncOutcome:
    from garminconnect import (GarminConnectAuthenticationError, GarminConnectConnectionError,
                               GarminConnectTooManyRequestsError)
    if isinstance(error, GarminConnectTooManyRequestsError):
        return SyncOutcome(EXIT_TEMPFAIL, "Garmin odmietol (429, príliš veľa požiadaviek).")
    if isinstance(error, GarminConnectAuthenticationError):
        return SyncOutcome(EXIT_NOPERM, "Prihlásenie do Garminu neplatí; spustite 'bimbo-trener login' v konzole.")
    if isinstance(error, GarminConnectConnectionError):
        text = str(error)
        if "403" in text:
            return SyncOutcome(EXIT_TEMPFAIL, "Garmin blokuje klienta alebo sieť (403); skúste neskôr, bez VPN.")
        return SyncOutcome(EXIT_TEMPFAIL, f"Sieťová chyba pri komunikácii s Garminom ({type(error).__name__}).")
    return SyncOutcome(EXIT_ERROR, f"Neočakávaná chyba ({type(error).__name__}): {error}")


# --- sync --------------------------------------------------------------------------------------

def sync(config: Config, data: DataPaths, force_health: bool = False, today: date | None = None) -> tuple[dict, int]:
    app = AppPaths(config.app_root)
    setup_logging(app)
    pause = float(config.sync.get("request_pause_seconds", 1.0))
    result: dict = {"new_activities": [], "health_days": [], "backup": None, "imported": None, "skipped": [], "message": ""}
    if not config.garmin_sync_enabled:
        result["message"] = "Na tomto počítači nie je sťahovanie nastavené (garmin_sync_enabled nie je zapnuté)."
        return result, EXIT_NOPERM
    until = cooldown_until(app)
    if until:
        result["message"] = f"Garmin nedávno odmietol; ďalší pokus až po {until.astimezone().strftime('%H:%M')}."
        return result, EXIT_OK
    try:
        _progress("Prihlasujem sa tokenom…")
        client = token_login(config)
        with db.connect(data, read_only=True) as connection:
            last_sync = db.get_meta(connection, "last_sync")
        start = (datetime.fromisoformat(last_sync.replace("Z", "+00:00")).date() - timedelta(days=1)) if last_sync else date(2000, 1, 1)
        end = today or date.today()
        _progress(f"Zoznam aktivít od {start.isoformat()}…")
        activities = client.get_activities_by_date(start.isoformat(), end.isoformat()) or []
        time.sleep(pause)
        with db.connect(data, read_only=True) as connection:
            known = {row[0] for row in connection.execute("SELECT activity_id FROM runs UNION ALL SELECT activity_id FROM activities_other")}
        new = [a for a in activities if a.get("activityId") not in known]
        if not new and not force_health and last_sync:
            result["message"] = "Nič nové."
            _progress("HOTOVO: nič nové")
            return result, EXIT_OK
        backup = db.backup_database(data, keep=config.backups_keep, today=end)
        result["backup"] = str(backup) if backup else None
        for activity in new:
            activity_id = activity["activityId"]
            target = data.fit / f"{activity_id}_ACTIVITY.fit"
            if target.exists():
                continue
            _progress(f"Sťahujem {activity.get('activityName', '')} {activity.get('startTimeLocal', '')}…")
            blob = client.download_activity(str(activity_id), dl_fmt=client.ActivityDownloadFormat.ORIGINAL)
            time.sleep(pause)
            fit = extract_fit(blob)
            if fit is None:
                result["skipped"].append({"activity_id": activity_id, "reason": "originál neobsahuje FIT (ručne nahraná aktivita?)"})
                log.warning("activity %s: no FIT in original download", activity_id)
                continue
            atomic_write_bytes(target, fit)
            result["new_activities"].append({"activity_id": activity_id, "name": activity.get("activityName"),
                                             "start": activity.get("startTimeLocal"), "distance_m": activity.get("distance")})
        _progress("Importujem FIT…")
        result["imported"] = import_pending(data)
        days = int(config.sync.get("health_days", 4))
        _progress(f"Denné zdravotné dáta za {days} dni…")
        result["health_days"] = fetch_health(client, data, end, days, pause)
        with db.writer_lock(data), db.connect(data) as connection:
            db.set_meta(connection, "last_sync", db.utcnow())
        count = len(result["imported"]["imported"]) if result["imported"] else 0
        if count:
            first = result["imported"]["imported"][0]
            result["message"] = f"{count} nový beh: {first.get('date_local')}" if count == 1 else f"{count} nové aktivity"
        else:
            result["message"] = "Nič nové." if not result["health_days"] else "Aktualizované denné dáta, žiadny nový beh."
        _progress("HOTOVO: " + result["message"])
        return result, EXIT_OK
    except SyncOutcome as outcome:
        result["message"] = outcome.message
        if outcome.code == EXIT_TEMPFAIL:
            until = set_cooldown(app, int(config.sync.get("cooldown_minutes", 90)))
            result["message"] += f" Ďalší pokus po {until.astimezone().strftime('%H:%M')}."
        log.error(outcome.message)
        return result, outcome.code
    except Exception as error:  # noqa: BLE001 - classified, never hidden
        outcome = _classify(error)
        result["message"] = outcome.message
        if outcome.code == EXIT_TEMPFAIL:
            until = set_cooldown(app, int(config.sync.get("cooldown_minutes", 90)))
            result["message"] += f" Ďalší pokus po {until.astimezone().strftime('%H:%M')}."
        log.exception("sync failed: %s", outcome.message)
        return result, outcome.code


def fetch_health(client, data: DataPaths, end: date, days: int, pause: float) -> list[str]:
    """Raw JSON per (date, kind) into connect_raw plus normalized daily_health / body_composition rows."""
    fetched_days = []
    now = db.utcnow()
    for offset in range(days):
        day = (end - timedelta(days=offset)).isoformat()
        payloads: dict[str, object] = {}
        for kind, method, nargs in HEALTH_CALLS:
            fn = getattr(client, method, None)
            if fn is None:
                log.warning("garminconnect has no %s()", method); continue
            try:
                payloads[kind] = fn(*([day] * nargs))
            except Exception as error:  # noqa: BLE001 - auth/429 propagate; a single missing metric does not stop the day
                from garminconnect import GarminConnectAuthenticationError, GarminConnectTooManyRequestsError
                if isinstance(error, (GarminConnectAuthenticationError, GarminConnectTooManyRequestsError)):
                    raise
                log.warning("%s(%s) failed: %s", method, day, error)
                payloads[kind] = None
            time.sleep(pause)
        store_health_day(data, day, payloads, now)
        fetched_days.append(day)
    return fetched_days


def _get(value, *path, default=None):
    for key in path:
        if isinstance(value, dict):
            value = value.get(key)
        elif isinstance(value, list) and isinstance(key, int) and len(value) > key:
            value = value[key]
        else:
            return default
    return default if value is None else value


def store_health_day(data: DataPaths, day: str, payloads: dict, fetched_at: str) -> None:
    """Normalization is best effort and documented in docs/coach/data-model.md; raw JSON is always kept."""
    summary, rhr, sleep, hrv, stress = payloads.get("user_summary"), payloads.get("rhr"), payloads.get("sleep"), payloads.get("hrv"), payloads.get("stress")
    battery, readiness, tstatus, resp, spo2 = (payloads.get("body_battery"), payloads.get("training_readiness"),
                                               payloads.get("training_status"), payloads.get("respiration"), payloads.get("spo2"))
    sleep_dto = _get(sleep, "dailySleepDTO", default={}) or {}
    battery_day = battery[0] if isinstance(battery, list) and battery else {}
    readiness_item = readiness[0] if isinstance(readiness, list) and readiness else (readiness or {})
    row = {
        "date": day,
        "resting_heart_rate": _get(summary, "restingHeartRate") or _get(rhr, "allMetrics", "metricsMap", "WELLNESS_RESTING_HEART_RATE", 0, "value"),
        "min_heart_rate": _get(summary, "minHeartRate"), "max_heart_rate": _get(summary, "maxHeartRate"),
        "hrv_last_night_avg": _get(hrv, "hrvSummary", "lastNightAvg"), "hrv_weekly_avg": _get(hrv, "hrvSummary", "weeklyAvg"),
        "hrv_status": _get(hrv, "hrvSummary", "status"),
        "sleep_seconds": sleep_dto.get("sleepTimeSeconds"), "sleep_score": _get(sleep_dto, "sleepScores", "overall", "value"),
        "deep_sleep_seconds": sleep_dto.get("deepSleepSeconds"), "light_sleep_seconds": sleep_dto.get("lightSleepSeconds"),
        "rem_sleep_seconds": sleep_dto.get("remSleepSeconds"), "awake_seconds": sleep_dto.get("awakeSleepSeconds"),
        "avg_stress": _get(summary, "averageStressLevel") or _get(stress, "avgStressLevel"),
        "max_stress": _get(summary, "maxStressLevel") or _get(stress, "maxStressLevel"),
        "body_battery_high": _get(summary, "bodyBatteryHighestValue"), "body_battery_low": _get(summary, "bodyBatteryLowestValue"),
        "body_battery_charged": _get(summary, "bodyBatteryChargedValue") or _get(battery_day, "charged"),
        "body_battery_drained": _get(summary, "bodyBatteryDrainedValue") or _get(battery_day, "drained"),
        "training_readiness_score": _get(readiness_item, "score"), "training_readiness_level": _get(readiness_item, "level"),
        "training_status": _get(tstatus, "mostRecentTrainingStatus", "latestTrainingStatusData", default=None) and json.dumps(
            _get(tstatus, "mostRecentTrainingStatus", "latestTrainingStatusData"), ensure_ascii=False, default=str),
        "avg_respiration": _get(resp, "avgSleepRespirationValue") or _get(resp, "avgWakingRespirationValue"),
        "avg_spo2": _get(spo2, "averageSpO2"),
        "steps": _get(summary, "totalSteps"), "total_calories": _get(summary, "totalKilocalories"),
        "active_calories": _get(summary, "activeKilocalories"),
        "moderate_intensity_minutes": _get(summary, "moderateIntensityMinutes"),
        "vigorous_intensity_minutes": _get(summary, "vigorousIntensityMinutes"),
        "fetched_at": fetched_at,
    }
    with db.writer_lock(data), db.connect(data) as connection:
        for kind, payload in payloads.items():
            if payload is None:
                continue
            connection.execute("INSERT OR REPLACE INTO connect_raw(date, kind, payload_json, fetched_at) VALUES (?,?,?,?)",
                               (day, kind, json.dumps(payload, ensure_ascii=False, default=str), fetched_at))
        if any(v is not None for k, v in row.items() if k not in ("date", "fetched_at")):
            columns = ", ".join(row); marks = ", ".join("?" for _ in row)
            connection.execute(f"INSERT OR REPLACE INTO daily_health({columns}) VALUES ({marks})", tuple(row.values()))
        composition = payloads.get("body_composition")
        for entry in (_get(composition, "dateWeightList", default=[]) or []):
            stamp = entry.get("timestampGMT") or entry.get("date")
            if stamp is None:
                continue
            ts = datetime.fromtimestamp(stamp / 1000, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z") \
                if isinstance(stamp, (int, float)) else str(stamp)
            connection.execute(
                "INSERT OR REPLACE INTO body_composition(timestamp_utc, date, weight_g, bmi, body_fat_percent, muscle_mass_g, "
                "bone_mass_g, body_water_percent, source, fetched_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (ts, entry.get("calendarDate") or day, entry.get("weight"), entry.get("bmi"), entry.get("bodyFat"),
                 entry.get("muscleMass"), entry.get("boneMass"), entry.get("bodyWater"), entry.get("sourceType"), fetched_at))
