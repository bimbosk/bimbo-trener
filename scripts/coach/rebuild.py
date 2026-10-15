"""Rebuild the database from what is never overwritten: FIT files, connect_raw snapshots and journal-export.jsonl."""
from __future__ import annotations

import json
import os
from datetime import datetime

from . import db
from .config import Config
from .fit_import import import_pending
from .layout import DataPaths


def rebuild(data: DataPaths, config: Config) -> dict:
    kept = None
    with db.writer_lock(data):
        if data.database.exists():
            kept = data.database.with_name(f"{data.database.name}.rebuilt-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
            os.replace(data.database, kept)
    db.ensure_schema(data)
    imported = import_pending(data)
    replayed = {"feeling": 0, "journal": 0, "plan": 0, "plan_status": 0, "coach_state": 0, "summary": 0, "training_plan": 0, "convention": 0}
    skipped = []
    export_path = data.journal_export
    rows = db.read_export(data)
    # Replaying writes would append to the export again: rotate the old export aside and rewrite it from the replay.
    if export_path.is_file():
        os.replace(export_path, export_path.with_name(f"journal-export.before-rebuild-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jsonl"))
    plan_ids: dict[int, int] = {}
    for row in rows:
        kind, item = row.get("record"), row.get("data", {})
        try:
            if kind == "feeling":
                db.add_feeling(data, item["event_date"], item["value"], item.get("text"), item.get("activity_id"), recorded_by="rebuild")
            elif kind == "journal":
                if item.get("kind") in ("feeling",) or (item.get("kind") == "decision" and item.get("plan_id")):
                    continue   # written again by add_feeling / save_plan
                db.add_journal(data, item["event_date"], item["kind"], item["text"], item.get("activity_id"),
                               plan_ids.get(item.get("plan_id")), recorded_by=item.get("recorded_by", "rebuild"))
            elif kind == "plan":
                new = db.save_plan(data, item["plan_date"], item["workout_type"], item["segments"], item.get("note"), created_by=item.get("created_by", "rebuild"))
                plan_ids[item["plan_id"]] = new["plan_id"]
            elif kind == "plan_status":
                target = plan_ids.get(item["plan_id"])
                if target:
                    db.set_plan_status(data, target, item["status"], item.get("activity_id"))
            elif kind == "coach_state":
                db.update_state(data, item["text"], recorded_by="rebuild")
            elif kind == "summary":
                db.add_summary(data, item["kind"], item["period"], item["text"], recorded_by="rebuild")
            elif kind == "training_plan":
                db.set_training_plan(data, item["goal"], item["phases"], item["milestones"], item.get("reason"), recorded_by="rebuild")
            elif kind == "convention":
                db.set_convention(data, item["key"], item["value"], item.get("note"))
            else:
                skipped.append({"record": kind, "reason": "neznámy druh"}); continue
            replayed[kind] += 1
        except Exception as error:  # noqa: BLE001 - surfaced, not hidden
            skipped.append({"record": kind, "data": item, "error": f"{type(error).__name__}: {error}"})
    return {"previous_database": str(kept) if kept else None, "fit": {k: len(v) for k, v in imported.items()},
            "replayed": replayed, "skipped": skipped}
