"""Derived indicators computed on demand from measured rows. Every result carries `source` so the coach
can label it: 'derived' (arithmetic on measured data), 'convention' (uses an owner convention) or 'estimate'."""
from __future__ import annotations

import json
import sqlite3
from datetime import date, timedelta
from statistics import mean


def _conv(connection: sqlite3.Connection) -> dict:
    return {row["key"]: row["value"] for row in connection.execute("SELECT key, value FROM conventions")}


def equivalent_speed_kmh(speed_kmh: float, incline_percent: float, conventions: dict) -> float:
    """Owner convention: 1 % incline ≈ +0.4 km/h (convention, not a measurement)."""
    per_percent = 0.4 / float(conventions.get("incline_percent_per_0_4_kmh", "1"))
    return round(speed_kmh + incline_percent * per_percent, 2)


def weekly_volume(connection: sqlite3.Connection, weeks: int = 8) -> dict:
    since = (date.today() - timedelta(weeks=weeks)).isoformat()
    rows = connection.execute(
        "SELECT strftime('%Y-W%W', date_local) AS week, COUNT(*) AS runs, SUM(total_distance) AS meters, "
        "SUM(total_timer_time) AS seconds, MAX(total_distance) AS longest_m FROM runs WHERE date_local >= ? "
        "GROUP BY week ORDER BY week", (since,)).fetchall()
    weeks_out = [{"week": r["week"], "runs": r["runs"], "km": round((r["meters"] or 0) / 1000, 2),
                  "minutes": round((r["seconds"] or 0) / 60, 1), "longest_km": round((r["longest_m"] or 0) / 1000, 2)} for r in rows]
    changes = []
    for previous, current in zip(weeks_out, weeks_out[1:]):
        if previous["km"] > 0:
            changes.append({"week": current["week"], "km_change_percent": round((current["km"] - previous["km"]) / previous["km"] * 100, 1)})
    return {"source": "derived", "weeks": weeks_out, "changes": changes}


def pace_at_heart_rate(connection: sqlite3.Connection, reference_hr: int = 115, tolerance: int = 3,
                       months: int = 6, treadmill_only: bool = True) -> dict:
    """Average pace (min/km) of record seconds whose heart rate is within ±tolerance of the reference, per run."""
    since = (date.today() - timedelta(days=30 * months)).isoformat()
    sql = ("SELECT r.activity_id, r.date_local, AVG(rec.enhanced_speed) AS speed, COUNT(*) AS seconds FROM runs r "
           "JOIN records rec ON rec.activity_id=r.activity_id WHERE r.date_local >= ? AND rec.heart_rate BETWEEN ? AND ? "
           "AND rec.enhanced_speed > 0.5")
    params: list = [since, reference_hr - tolerance, reference_hr + tolerance]
    if treadmill_only:
        sql += " AND r.sub_sport='treadmill'"
    sql += " GROUP BY r.activity_id HAVING seconds >= 120 ORDER BY r.date_local"
    points = []
    for row in connection.execute(sql, params):
        pace = 1000 / row["speed"] / 60
        points.append({"activity_id": row["activity_id"], "date": row["date_local"], "pace_min_per_km": round(pace, 2),
                       "seconds_in_band": row["seconds"]})
    return {"source": "derived", "reference_hr": reference_hr, "tolerance": tolerance, "points": points,
            "note": "iba sekundy s tepom v pásme a rýchlosťou > 0,5 m/s; behy s menej než 120 takými sekundami vynechané"}


def heart_rate_drift(connection: sqlite3.Connection, activity_id: int) -> dict:
    """Mean HR in minutes 10–20 vs the last 10 minutes at comparable speed; None when the run is too short."""
    rows = connection.execute("SELECT seq, heart_rate, enhanced_speed FROM records WHERE activity_id=? ORDER BY seq",
                              (activity_id,)).fetchall()
    if len(rows) < 1800:
        return {"source": "derived", "activity_id": activity_id, "drift_bpm": None, "reason": "beh kratší než 30 minút"}
    early = [r for r in rows[600:1200] if r["heart_rate"] and r["enhanced_speed"]]
    late = [r for r in rows[-600:] if r["heart_rate"] and r["enhanced_speed"]]
    if not early or not late:
        return {"source": "derived", "activity_id": activity_id, "drift_bpm": None, "reason": "chýba tep alebo rýchlosť"}
    speed_early, speed_late = mean(r["enhanced_speed"] for r in early), mean(r["enhanced_speed"] for r in late)
    comparable = abs(speed_early - speed_late) <= 0.15
    return {"source": "derived", "activity_id": activity_id,
            "hr_early": round(mean(r["heart_rate"] for r in early), 1), "hr_late": round(mean(r["heart_rate"] for r in late), 1),
            "drift_bpm": round(mean(r["heart_rate"] for r in late) - mean(r["heart_rate"] for r in early), 1),
            "speed_early": round(speed_early, 3), "speed_late": round(speed_late, 3), "comparable_speed": comparable}


def compare_plan_run(connection: sqlite3.Connection, activity_id: int) -> dict:
    """Split the run's records into N equal time segments (owner's segments, not watch laps) and compare
    each with the prescribed speed/incline. Values per segment are derived from records."""
    plan = connection.execute("SELECT * FROM plans WHERE activity_id=? ORDER BY updated_at DESC LIMIT 1", (activity_id,)).fetchone()
    if not plan:
        return {"source": "derived", "activity_id": activity_id, "plan": None, "segments": [], "reason": "beh nemá spárovaný predpis"}
    segments = connection.execute("SELECT seq, minutes, speed_kmh, incline_percent FROM plan_segments WHERE plan_id=? ORDER BY seq",
                                  (plan["plan_id"],)).fetchall()
    records = connection.execute("SELECT seq, timestamp_utc, heart_rate, enhanced_speed, cadence FROM records WHERE activity_id=? ORDER BY seq",
                                 (activity_id,)).fetchall()
    moving = [r for r in records if r["enhanced_speed"] and r["enhanced_speed"] > 0.5]
    if not moving:
        return {"source": "derived", "activity_id": activity_id, "plan": dict(plan), "segments": [], "reason": "bez pohybu v záznamoch"}
    first = moving[0]["seq"]
    conventions = _conv(connection)
    out = []
    for segment in segments:
        length = int(round(segment["minutes"] * 60))
        window = [r for r in records if first + (segment["seq"] - 1) * length <= r["seq"] < first + segment["seq"] * length]
        speeds = [r["enhanced_speed"] for r in window if r["enhanced_speed"]]
        hrs = [r["heart_rate"] for r in window if r["heart_rate"]]
        actual_kmh = round(mean(speeds) * 3.6, 2) if speeds else None
        out.append({"seq": segment["seq"], "planned_speed_kmh": segment["speed_kmh"], "planned_incline_percent": segment["incline_percent"],
                    "planned_equivalent_kmh": equivalent_speed_kmh(segment["speed_kmh"], segment["incline_percent"], conventions),
                    "actual_speed_kmh": actual_kmh, "hr_mean": round(mean(hrs), 1) if hrs else None,
                    "hr_max": max(hrs) if hrs else None, "seconds": len(window)})
    return {"source": "derived", "activity_id": activity_id, "plan": {"plan_id": plan["plan_id"], "workout_type": plan["workout_type"],
            "total_minutes": plan["total_minutes"]}, "segments": out,
            "note": "úseky odvodené z času od prvého pohybu; rýchlosť hodiniek na páse kolíše okolo nastavenej; sklon hodinky nemerajú"}


def warnings(connection: sqlite3.Connection) -> list[dict]:
    """Named observations, never decisions. Thresholds are general recommendations."""
    out = []
    volume = weekly_volume(connection, weeks=3)["weeks"]
    if len(volume) >= 2 and volume[-2]["km"] > 0:
        change = (volume[-1]["km"] - volume[-2]["km"]) / volume[-2]["km"] * 100
        if change > 15:
            out.append({"kind": "volume_jump", "source": "recommendation", "text": f"týždenný objem stúpol o {change:.0f} % (odporúčanie: najviac 10–15 %)"})
    last = connection.execute("SELECT MAX(date_local) FROM runs").fetchone()[0]
    if last:
        gap = (date.today() - date.fromisoformat(last)).days
        reason = connection.execute("SELECT 1 FROM journal WHERE kind='circumstance' AND event_date > ?", (last,)).fetchone()
        if gap > 7 and not reason:
            out.append({"kind": "gap", "source": "derived", "text": f"{gap} dní bez behu bez zapísaného dôvodu"})
    pains = connection.execute("SELECT COUNT(*) FROM journal WHERE event_date >= date('now','-14 days') AND "
                               "(text LIKE '%bol%' OR text LIKE '%koleno%' OR text LIKE '%achil%')").fetchone()[0]
    if pains >= 2:
        out.append({"kind": "pain", "source": "derived", "text": f"{pains} zmienky bolesti v denníku za 14 dní"})
    return out


def analysis(connection: sqlite3.Connection, kind: str, **params) -> dict:
    if kind == "weekly_volume":
        return weekly_volume(connection, int(params.get("weeks", 8)))
    if kind == "pace_at_hr":
        return pace_at_heart_rate(connection, int(params.get("reference_hr", 115)), int(params.get("tolerance", 3)))
    if kind == "drift":
        return heart_rate_drift(connection, int(params["activity_id"]))
    if kind == "compare":
        return compare_plan_run(connection, int(params["activity_id"]))
    if kind == "warnings":
        return {"source": "mixed", "warnings": warnings(connection)}
    raise ValueError(f"Neznáma analýza: {kind}")
