"""Read-only Markdown preview of the coach's memory, generated from the database into <data_dir>/preview."""
from __future__ import annotations

import sqlite3
from collections import defaultdict
from pathlib import Path

from .layout import DataPaths
from .paths import atomic_write_bytes


def _write(path: Path, text: str) -> None:
    atomic_write_bytes(path, text.encode("utf-8"))


def render(connection: sqlite3.Connection, data: DataPaths) -> dict:
    written = []
    state = connection.execute("SELECT text, updated_at FROM coach_state WHERE id=1").fetchone()
    lines = ["# Stav trénera", "", "_Generovaný náhľad z databázy; nič sem nepíšte._", ""]
    lines += [state["text"], "", f"Aktualizované: {state['updated_at']}"] if state else ["Stav zatiaľ nebol zapísaný."]
    plan = connection.execute("SELECT * FROM training_plan WHERE active=1 ORDER BY version DESC LIMIT 1").fetchone()
    if plan:
        lines += ["", "## Dlhodobý plán", "", f"Cieľ: {plan['goal']} (verzia {plan['version']})", "", "```json",
                  plan["phases_json"], plan["milestones_json"], "```"]
    _write(data.preview / "STAV.md", "\n".join(lines) + "\n"); written.append("STAV.md")

    by_month: dict[str, list] = defaultdict(list)
    for row in connection.execute("SELECT event_date, kind, text, recorded_at FROM journal ORDER BY event_date, recorded_at"):
        by_month[row["event_date"][:7]].append(row)
    for month, rows in by_month.items():
        lines = [f"# Denník {month}", "", "_Generovaný náhľad z databázy._", ""]
        current = None
        for row in rows:
            if row["event_date"] != current:
                current = row["event_date"]; lines += [f"## {current}", ""]
            lines.append(f"- **{row['kind']}**: {row['text']}  ")
            lines.append(f"  _zapísané {row['recorded_at']}_")
        _write(data.preview / "dennik" / f"{month}.md", "\n".join(lines) + "\n"); written.append(f"dennik/{month}.md")

    for row in connection.execute("SELECT kind, period, text, recorded_at FROM summaries WHERE superseded=0 ORDER BY period"):
        name = f"{row['period']}.md"
        _write(data.preview / "zhrnutia" / name, f"# Zhrnutie {row['period']}\n\n{row['text']}\n\n_zapísané {row['recorded_at']}_\n")
        written.append(f"zhrnutia/{name}")

    lines = ["# Behy", "", "| Dátum | km | čas pohybu | tep priem./max | pocit | predpis |", "| --- | --- | --- | --- | --- | --- |"]
    for r in connection.execute(
            "SELECT r.date_local, r.total_distance, r.total_timer_time, r.avg_heart_rate, r.max_heart_rate, "
            "(SELECT value FROM feelings f WHERE f.activity_id=r.activity_id ORDER BY recorded_at DESC LIMIT 1) AS feeling, "
            "(SELECT workout_type FROM plans p WHERE p.activity_id=r.activity_id LIMIT 1) AS plan FROM runs r ORDER BY r.date_local DESC"):
        minutes = (r["total_timer_time"] or 0) / 60
        lines.append(f"| {r['date_local']} | {(r['total_distance'] or 0)/1000:.2f} | {int(minutes)}:{int((minutes % 1) * 60):02d} | "
                     f"{r['avg_heart_rate'] or '–'}/{r['max_heart_rate'] or '–'} | {r['feeling'] or '–'} | {r['plan'] or '–'} |")
    _write(data.preview / "behy.md", "\n".join(lines) + "\n"); written.append("behy.md")
    return {"preview_dir": str(data.preview), "written": written}
