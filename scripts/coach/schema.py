"""SQLite schema (single owner of every stored fact) and forward-only migrations."""
from __future__ import annotations

import sqlite3

SCHEMA_VERSION = 1

# Measured data from FIT: append-only. Units exactly as FIT delivers them (m, s, m/s, mm, ms).
MEASURED = """
CREATE TABLE IF NOT EXISTS runs(
  activity_id INTEGER PRIMARY KEY,
  start_time_utc TEXT NOT NULL, start_time_local TEXT, date_local TEXT NOT NULL,
  sport TEXT, sub_sport TEXT, sport_profile_name TEXT,
  total_elapsed_time REAL, total_timer_time REAL, total_distance REAL,
  enhanced_avg_speed REAL, enhanced_max_speed REAL,
  avg_heart_rate INTEGER, max_heart_rate INTEGER,
  avg_running_cadence REAL, max_running_cadence REAL, avg_fractional_cadence REAL, max_fractional_cadence REAL,
  avg_power INTEGER, max_power INTEGER, normalized_power INTEGER, total_work INTEGER,
  total_strides INTEGER, total_cycles INTEGER,
  avg_step_length REAL, avg_vertical_ratio REAL, avg_vertical_oscillation REAL, avg_stance_time REAL,
  total_training_effect REAL, total_anaerobic_training_effect REAL, training_load_peak REAL,
  total_calories INTEGER, metabolic_calories INTEGER,
  num_laps INTEGER, trigger TEXT,
  device_product TEXT, device_serial TEXT, device_software_version REAL,
  fit_path TEXT NOT NULL, source TEXT NOT NULL, imported_at TEXT NOT NULL,
  import_errors TEXT
);
CREATE INDEX IF NOT EXISTS ix_runs_date ON runs(date_local);

CREATE TABLE IF NOT EXISTS activities_other(
  activity_id INTEGER PRIMARY KEY,
  start_time_utc TEXT NOT NULL, date_local TEXT NOT NULL, sport TEXT, sub_sport TEXT, sport_profile_name TEXT,
  total_elapsed_time REAL, total_timer_time REAL, total_distance REAL,
  avg_heart_rate INTEGER, max_heart_rate INTEGER, total_calories INTEGER,
  device_product TEXT, fit_path TEXT NOT NULL, source TEXT NOT NULL, imported_at TEXT NOT NULL,
  session_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS laps(
  activity_id INTEGER NOT NULL, lap_index INTEGER NOT NULL,
  start_time_utc TEXT, total_elapsed_time REAL, total_timer_time REAL, total_distance REAL,
  enhanced_avg_speed REAL, enhanced_max_speed REAL, avg_heart_rate INTEGER, max_heart_rate INTEGER,
  avg_running_cadence REAL, max_running_cadence REAL, avg_power INTEGER, max_power INTEGER, normalized_power INTEGER,
  total_strides INTEGER, total_calories INTEGER,
  avg_step_length REAL, avg_vertical_ratio REAL, avg_vertical_oscillation REAL, avg_stance_time REAL,
  lap_trigger TEXT, intensity TEXT,
  PRIMARY KEY(activity_id, lap_index)
);

CREATE TABLE IF NOT EXISTS records(
  activity_id INTEGER NOT NULL, timestamp_utc TEXT NOT NULL, seq INTEGER NOT NULL,
  distance REAL, enhanced_speed REAL, heart_rate INTEGER, cadence INTEGER, fractional_cadence REAL,
  power INTEGER, accumulated_power INTEGER,
  vertical_oscillation REAL, vertical_ratio REAL, step_length REAL, stance_time REAL,
  activity_type TEXT,
  position_lat INTEGER, position_long INTEGER, altitude REAL, enhanced_altitude REAL, temperature INTEGER,
  PRIMARY KEY(activity_id, seq)
);
CREATE INDEX IF NOT EXISTS ix_records_time ON records(activity_id, timestamp_utc);

CREATE TABLE IF NOT EXISTS events(
  activity_id INTEGER NOT NULL, timestamp_utc TEXT NOT NULL, seq INTEGER NOT NULL,
  event TEXT, event_type TEXT, event_group INTEGER, timer_trigger TEXT, data INTEGER,
  PRIMARY KEY(activity_id, timestamp_utc, seq)
);

CREATE TABLE IF NOT EXISTS time_in_zone(
  activity_id INTEGER NOT NULL, reference_mesg TEXT NOT NULL, reference_index INTEGER NOT NULL,
  time_in_hr_zone TEXT, time_in_power_zone TEXT, time_in_speed_zone TEXT, time_in_cadence_zone TEXT,
  PRIMARY KEY(activity_id, reference_mesg, reference_index)
);

CREATE TABLE IF NOT EXISTS zone_snapshot(
  activity_id INTEGER PRIMARY KEY,
  max_heart_rate INTEGER, resting_heart_rate INTEGER, threshold_heart_rate INTEGER,
  functional_threshold_power INTEGER, hr_calc_type TEXT, pwr_calc_type TEXT,
  hr_zone_high_boundary TEXT, power_zone_high_boundary TEXT
);

CREATE TABLE IF NOT EXISTS splits(
  activity_id INTEGER NOT NULL, split_index INTEGER NOT NULL,
  split_type TEXT, start_time_utc TEXT, end_time_utc TEXT, total_elapsed_time REAL, total_timer_time REAL,
  total_distance REAL, avg_speed REAL, avg_heart_rate INTEGER, max_heart_rate INTEGER, total_calories INTEGER,
  PRIMARY KEY(activity_id, split_index)
);

CREATE TABLE IF NOT EXISTS fit_raw(
  activity_id INTEGER NOT NULL, mesg_name TEXT NOT NULL, mesg_index INTEGER NOT NULL, fields_json TEXT NOT NULL,
  PRIMARY KEY(activity_id, mesg_name, mesg_index)
);
"""

# Daily health data from Garmin Connect: re-fetched for the last N days, upsert.
HEALTH = """
CREATE TABLE IF NOT EXISTS daily_health(
  date TEXT PRIMARY KEY,
  resting_heart_rate INTEGER, min_heart_rate INTEGER, max_heart_rate INTEGER,
  hrv_last_night_avg REAL, hrv_weekly_avg REAL, hrv_status TEXT,
  sleep_seconds INTEGER, sleep_score INTEGER, deep_sleep_seconds INTEGER, light_sleep_seconds INTEGER,
  rem_sleep_seconds INTEGER, awake_seconds INTEGER,
  avg_stress INTEGER, max_stress INTEGER,
  body_battery_high INTEGER, body_battery_low INTEGER, body_battery_charged INTEGER, body_battery_drained INTEGER,
  training_readiness_score INTEGER, training_readiness_level TEXT, training_status TEXT,
  avg_respiration REAL, avg_spo2 REAL,
  steps INTEGER, total_calories INTEGER, active_calories INTEGER,
  moderate_intensity_minutes INTEGER, vigorous_intensity_minutes INTEGER,
  fetched_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS body_composition(
  timestamp_utc TEXT PRIMARY KEY, date TEXT NOT NULL,
  weight_g INTEGER, bmi REAL, body_fat_percent REAL, muscle_mass_g INTEGER, bone_mass_g INTEGER,
  body_water_percent REAL, source TEXT, fetched_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS connect_raw(
  date TEXT NOT NULL, kind TEXT NOT NULL, payload_json TEXT NOT NULL, fetched_at TEXT NOT NULL,
  PRIMARY KEY(date, kind)
);
"""

# Coach and owner data. Journal is append-only; coach_state is overwritten; plans change status.
OWN = """
CREATE TABLE IF NOT EXISTS plans(
  plan_id INTEGER PRIMARY KEY,
  plan_date TEXT NOT NULL, workout_type TEXT NOT NULL, total_minutes INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'proposed', activity_id INTEGER, note TEXT,
  created_by TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_plans_date ON plans(plan_date);

CREATE TABLE IF NOT EXISTS plan_segments(
  plan_id INTEGER NOT NULL REFERENCES plans(plan_id) ON DELETE CASCADE,
  seq INTEGER NOT NULL, minutes REAL NOT NULL, speed_kmh INTEGER NOT NULL, incline_percent INTEGER NOT NULL,
  PRIMARY KEY(plan_id, seq)
);

CREATE TABLE IF NOT EXISTS feelings(
  feeling_id INTEGER PRIMARY KEY,
  event_date TEXT NOT NULL, activity_id INTEGER, value TEXT NOT NULL, text TEXT, recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS journal(
  entry_id INTEGER PRIMARY KEY,
  event_date TEXT NOT NULL, kind TEXT NOT NULL, text TEXT NOT NULL,
  activity_id INTEGER, plan_id INTEGER, recorded_at TEXT NOT NULL, recorded_by TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_journal_event ON journal(event_date);
CREATE INDEX IF NOT EXISTS ix_journal_recorded ON journal(recorded_at);

CREATE TABLE IF NOT EXISTS summaries(
  summary_id INTEGER PRIMARY KEY,
  kind TEXT NOT NULL, period TEXT NOT NULL, text TEXT NOT NULL, recorded_at TEXT NOT NULL, superseded INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_summaries_period ON summaries(kind, period);

CREATE TABLE IF NOT EXISTS coach_state(
  id INTEGER PRIMARY KEY CHECK(id = 1), text TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS training_plan(
  version INTEGER PRIMARY KEY, goal TEXT NOT NULL, phases_json TEXT NOT NULL, milestones_json TEXT NOT NULL,
  reason TEXT, created_at TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS conventions(key TEXT PRIMARY KEY, value TEXT NOT NULL, note TEXT);

CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""

FTS = (
    "CREATE VIRTUAL TABLE IF NOT EXISTS journal_fts USING fts5(text, content='journal', content_rowid='entry_id', "
    "tokenize='unicode61 remove_diacritics 2')",
    "CREATE TRIGGER IF NOT EXISTS journal_ai AFTER INSERT ON journal BEGIN "
    "INSERT INTO journal_fts(rowid, text) VALUES (new.entry_id, new.text); END",
    "CREATE VIRTUAL TABLE IF NOT EXISTS summaries_fts USING fts5(text, content='summaries', content_rowid='summary_id', "
    "tokenize='unicode61 remove_diacritics 2')",
    "CREATE TRIGGER IF NOT EXISTS summaries_ai AFTER INSERT ON summaries BEGIN "
    "INSERT INTO summaries_fts(rowid, text) VALUES (new.summary_id, new.text); END",
)

DEFAULT_CONVENTIONS = {
    "segments": ("10", "presne 10 rovnakých úsekov v každom predpise"),
    "incline_percent_per_0_4_kmh": ("1", "1 % sklonu ≈ +0,4 km/h; konvencia, nie meranie"),
    "min_running_speed_kmh": ("7", "6 km/h nie je beh"),
    "integer_speeds": ("true", "desatinné rýchlosti sa nahrádzajú sklonom"),
    "comfortable_speed_kmh": ("8", "pohodlná pracovná rýchlosť k 29. 8. 2026; aktuálnu drží coach_state"),
    "fast_segment_speed_kmh": ("9", "výrazne rýchlejší úsek, nie maximum"),
    "goal_distance_km": ("21.1", "polmaratón; medzicieľ 15 → 17 → 19 → 21,1 km"),
    "long_goal": ("marathon", "neskôr maratón"),
}

MIGRATIONS: dict[int, tuple[str, ...]] = {
    # 1 -> 2 etc. are added here as plain SQL tuples; db.migrate() applies them in order with a backup first.
}


def create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(MEASURED + HEALTH + OWN)
    for statement in FTS:
        connection.execute(statement)
    connection.execute("INSERT OR IGNORE INTO meta(key, value) VALUES ('schema_version', ?)", (str(SCHEMA_VERSION),))
    for key, (value, note) in DEFAULT_CONVENTIONS.items():
        connection.execute("INSERT OR IGNORE INTO conventions(key, value, note) VALUES (?, ?, ?)", (key, value, note))


def current_version(connection: sqlite3.Connection) -> int:
    row = connection.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
    return int(row[0]) if row else 0
