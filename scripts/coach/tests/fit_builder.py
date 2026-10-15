"""Synthetic FIT activity files for tests (no personal data), built with the official encoder."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from garmin_fit_sdk import Encoder, Profile

MESG = {name: num for num, entry in Profile["messages"].items() for name in [entry["name"]]}


def build_run(path: Path, start: datetime, laps: int = 2, seconds_per_lap: int = 60, speed: float = 2.2,
              heart_rate: int = 110, sport: str = "running", sub_sport: str = "treadmill",
              local_offset_hours: int = 2) -> Path:
    start = start.astimezone(timezone.utc).replace(microsecond=0)
    total = laps * seconds_per_lap
    encoder = Encoder()
    encoder.write_mesg({"mesg_num": MESG["file_id"], "type": "activity", "manufacturer": "garmin", "product": 4643,
                        "serial_number": 123456789, "time_created": start})
    encoder.write_mesg({"mesg_num": MESG["device_info"], "timestamp": start, "manufacturer": "garmin", "product": 4643,
                        "software_version": 18.32, "device_index": "creator"})
    encoder.write_mesg({"mesg_num": MESG["sport"], "sport": sport, "sub_sport": sub_sport, "name": "Bežiaci pás"})
    encoder.write_mesg({"mesg_num": MESG["event"], "timestamp": start, "event": "timer", "event_type": "start",
                        "event_group": 0, "timer_trigger": "manual"})
    distance = 0.0
    for second in range(total + 1):
        stamp = start + timedelta(seconds=second)
        moving = 0 < second <= total
        distance += speed if moving else 0.0
        encoder.write_mesg({"mesg_num": MESG["record"], "timestamp": stamp, "distance": round(distance, 2),
                            "enhanced_speed": speed if moving else 0.0, "heart_rate": heart_rate + (second // 30),
                            "cadence": 76 if moving else 0, "power": 290 if moving else 0,
                            "vertical_oscillation": 85.0, "stance_time": 300.0, "step_length": 900.0,
                            "vertical_ratio": 9.5, "activity_type": "running"})
    for index in range(laps):
        lap_start = start + timedelta(seconds=index * seconds_per_lap)
        encoder.write_mesg({"mesg_num": MESG["lap"], "timestamp": lap_start + timedelta(seconds=seconds_per_lap),
                            "start_time": lap_start, "message_index": index, "total_elapsed_time": float(seconds_per_lap),
                            "total_timer_time": float(seconds_per_lap), "total_distance": round(speed * seconds_per_lap, 2),
                            "enhanced_avg_speed": speed, "enhanced_max_speed": speed, "avg_heart_rate": heart_rate + index,
                            "max_heart_rate": heart_rate + index + 5, "avg_power": 290, "max_power": 320,
                            "lap_trigger": "distance", "intensity": "interval", "sport": sport, "sub_sport": sub_sport,
                            "event": "lap", "event_type": "stop"})
    encoder.write_mesg({"mesg_num": MESG["event"], "timestamp": start + timedelta(seconds=total), "event": "timer",
                        "event_type": "stop_all", "event_group": 0, "timer_trigger": "manual"})
    encoder.write_mesg({"mesg_num": MESG["session"], "timestamp": start + timedelta(seconds=total), "start_time": start,
                        "message_index": 0, "sport": sport, "sub_sport": sub_sport, "sport_profile_name": "Bežiaci pás",
                        "total_elapsed_time": float(total), "total_timer_time": float(total),
                        "total_distance": round(speed * total, 2), "enhanced_avg_speed": speed, "enhanced_max_speed": speed,
                        "avg_heart_rate": heart_rate, "max_heart_rate": heart_rate + 10, "avg_power": 290, "max_power": 320,
                        "normalized_power": 295, "total_calories": 100, "num_laps": laps, "first_lap_index": 0,
                        "total_training_effect": 2.5, "total_anaerobic_training_effect": 0.0,
                        "avg_vertical_oscillation": 85.0, "avg_stance_time": 300.0, "avg_step_length": 900.0,
                        "avg_vertical_ratio": 9.5, "event": "session", "event_type": "stop", "trigger": "activity_end"})
    encoder.write_mesg({"mesg_num": MESG["time_in_zone"], "timestamp": start + timedelta(seconds=total),
                        "reference_mesg": "session", "reference_index": 0,
                        "time_in_hr_zone": [10.0, float(total - 10), 0.0, 0.0, 0.0, 0.0, 0.0],
                        "hr_zone_high_boundary": [88, 106, 123, 141, 158, 176], "max_heart_rate": 176,
                        "resting_heart_rate": 49, "threshold_heart_rate": 154, "functional_threshold_power": 353,
                        "hr_calc_type": "percent_max_hr", "pwr_calc_type": "percent_ftp"})
    encoder.write_mesg({"mesg_num": MESG["split"], "timestamp": start + timedelta(seconds=total), "message_index": 0,
                        "split_type": "rwd_run", "start_time": start, "end_time": start + timedelta(seconds=total),
                        "total_elapsed_time": float(total), "total_timer_time": float(total),
                        "total_distance": round(speed * total, 2), "avg_speed": speed, "avg_heart_rate": heart_rate,
                        "max_heart_rate": heart_rate + 10, "total_calories": 100})
    local = start + timedelta(seconds=total, hours=local_offset_hours)   # activity.local_timestamp pairs with its timestamp (end)
    encoder.write_mesg({"mesg_num": MESG["activity"], "timestamp": start + timedelta(seconds=total),
                        "total_timer_time": float(total), "num_sessions": 1, "type": "manual", "event": "activity",
                        "event_type": "stop", "local_timestamp": local.replace(tzinfo=timezone.utc)})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoder.close())
    return path
