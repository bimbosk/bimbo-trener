"""Headless CLI: python -m scripts.coach.cli [--root DIR] [--data-dir DIR] <command>. JSON on stdout.

Exit codes: 0 ok · 75 temporary failure (rate limit, network) · 77 missing login/setup · 1 error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import db
from .config import Config, load_config, repository_root, write_local_override
from .datadir import attach_data_dir, init_data_dir, marker_info, open_data_dir
from .layout import DataPaths

EXIT_OK, EXIT_ERROR, EXIT_TEMPFAIL, EXIT_NOPERM = 0, 1, 75, 77


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"{self.prog}: chyba: {message}", file=sys.stderr)
        raise SystemExit(EXIT_ERROR)


def build_parser() -> Parser:
    p = Parser(prog="bimbo-trener", description="Bimbo tréner: lokálna databáza behov a pamäť trénera.")
    p.add_argument("--root", type=Path, help="koreň repozitára alebo aplikácie (kde je bimbo-trener.json)")
    p.add_argument("--data-dir", type=Path, help="dátový adresár (prepíše konfiguráciu)")
    p.add_argument("--compact", action="store_true", help="JSON v jednom riadku")
    subs = p.add_subparsers(dest="command", required=True, parser_class=Parser)
    subs.add_parser("config", help="výsledná konfigurácia")
    for name in ("init", "attach"):
        s = subs.add_parser(name, help="nový / existujúci dátový adresár"); s.add_argument("--data-dir", type=Path, dest="target")
        s.add_argument("--write-local", action="store_true", help="zapísať cestu do bimbo-trener.local.json")
    subs.add_parser("status")
    subs.add_parser("import", help="import nových FIT súborov z fit/ a fit/manual/")
    r = subs.add_parser("recent"); r.add_argument("--days", type=int, default=7); r.add_argument("--runs", type=int, default=3)
    st = subs.add_parser("state").add_subparsers(dest="state_command", required=True, parser_class=Parser)
    st.add_parser("show"); st.add_parser("set").add_argument("text")
    pl = subs.add_parser("plan").add_subparsers(dest="plan_command", required=True, parser_class=Parser)
    pa = pl.add_parser("add"); pa.add_argument("plan_date"); pa.add_argument("workout_type")
    pa.add_argument("--segments", required=True, help='JSON: [{"minutes":5,"speed_kmh":8,"incline_percent":0}, …]')
    pa.add_argument("--note")
    pl.add_parser("list").add_argument("--limit", type=int, default=20)
    ps = pl.add_parser("show"); ps.add_argument("--date"); ps.add_argument("--id", type=int)
    pst = pl.add_parser("status"); pst.add_argument("plan_id", type=int); pst.add_argument("status", choices=db.PLAN_STATUSES)
    pst.add_argument("--activity-id", type=int)
    fe = subs.add_parser("feeling"); fe.add_argument("event_date"); fe.add_argument("value", choices=db.FEELING_VALUES)
    fe.add_argument("--text"); fe.add_argument("--activity-id", type=int)
    jo = subs.add_parser("journal").add_subparsers(dest="journal_command", required=True, parser_class=Parser)
    ja = jo.add_parser("add"); ja.add_argument("event_date"); ja.add_argument("kind", choices=db.JOURNAL_KINDS); ja.add_argument("text")
    ja.add_argument("--activity-id", type=int); ja.add_argument("--plan-id", type=int)
    js = jo.add_parser("search"); js.add_argument("query"); js.add_argument("--limit", type=int, default=20)
    su = subs.add_parser("summary").add_subparsers(dest="summary_command", required=True, parser_class=Parser)
    sa = su.add_parser("add"); sa.add_argument("kind", choices=db.SUMMARY_KINDS); sa.add_argument("period"); sa.add_argument("text")
    su.add_parser("latest").add_argument("kind", choices=db.SUMMARY_KINDS)
    tp = subs.add_parser("training-plan").add_subparsers(dest="tp_command", required=True, parser_class=Parser)
    tp.add_parser("show")
    ts = tp.add_parser("set"); ts.add_argument("goal"); ts.add_argument("--phases", required=True); ts.add_argument("--milestones", required=True)
    ts.add_argument("--reason")
    an = subs.add_parser("analysis"); an.add_argument("kind", choices=["weekly_volume", "pace_at_hr", "drift", "compare", "warnings"])
    an.add_argument("--activity-id", type=int); an.add_argument("--weeks", type=int); an.add_argument("--reference-hr", type=int)
    subs.add_parser("health").add_argument("--days", type=int, default=3)
    subs.add_parser("backup")
    subs.add_parser("restore").add_argument("--from", dest="source", type=Path, required=True)
    subs.add_parser("rebuild", help="nová databáza z FIT súborov a exportu denníka")
    subs.add_parser("render", help="Markdown náhľad do preview/")
    subs.add_parser("login", help="prihlásenie do Garmin Connect (interaktívne, iba v konzole)")
    sy = subs.add_parser("sync", help="stiahnutie nových dát z Garmin Connect a import")
    sy.add_argument("--force-health", action="store_true", help="stiahnuť denné dáta aj bez novej aktivity")
    return p


def output(value, compact: bool) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=None if compact else 2, default=str), flush=True)


def resolve(args) -> tuple[Config, DataPaths | None]:
    config = load_config(args.root or repository_root(), {"data_dir": str(args.data_dir) if args.data_dir else None})
    if config.data_dir is None:
        return config, None
    return config, DataPaths(config.data_dir, config.database_name, config.fit_dir_name)


def require_data(config: Config, data: DataPaths | None) -> DataPaths:
    if data is None or not data.marker.is_file():
        raise SystemExit(_fail("Dátový adresár nie je nastavený alebo neexistuje. Použite 'init' alebo 'attach'.", EXIT_NOPERM))
    db.ensure_schema(data)
    return data


def _fail(message: str, code: int) -> int:
    print(json.dumps({"error": message, "exit_code": code}, ensure_ascii=False), file=sys.stderr, flush=True)
    return code


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run(args)
    except SystemExit as exit_:          # require_data() reports and exits with its own code
        return int(exit_.code) if isinstance(exit_.code, int) else EXIT_ERROR
    except db.StoreError as error:
        return _fail(str(error), EXIT_ERROR)
    except (ValueError, FileNotFoundError) as error:
        return _fail(str(error), EXIT_ERROR)


def run(args) -> int:
    config, data = resolve(args)
    compact = args.compact
    command = args.command

    if command == "config":
        output({"root": str(config.root), "app_root": str(config.app_root), "data_dir": str(config.data_dir) if config.data_dir else None,
                "garmin_sync_enabled": config.garmin_sync_enabled, "token_dir": str(config.token_dir), "sync": config.sync,
                "backups_keep": config.backups_keep}, compact)
        return EXIT_OK
    if command in ("init", "attach"):
        target = args.target or config.data_dir
        if target is None:
            return _fail("Zadajte --data-dir.", EXIT_ERROR)
        fn = init_data_dir if command == "init" else attach_data_dir
        paths = fn(Path(target).resolve(), config.database_name, config.fit_dir_name)
        created = db.ensure_schema(paths)
        if args.write_local:
            write_local_override(config.root, {"data_dir": str(paths.root)})
        output({"command": command, "data_dir": str(paths.root), "marker": marker_info(paths), "schema": created}, compact)
        return EXIT_OK

    data = require_data(config, data)
    if command == "status":
        output(db.status(data), compact); return EXIT_OK
    if command == "import":
        from .fit_import import import_pending
        output(import_pending(data), compact); return EXIT_OK
    if command == "recent":
        with db.connect(data, read_only=True) as c:
            output({"state": db.get_state(c), "week_summary": db.latest_summary(c, "week"),
                    "journal": db.recent_journal(c, args.days), "runs": db.recent_runs(c, args.runs),
                    "health": db.recent_health(c, 3)}, compact)
        return EXIT_OK
    if command == "state":
        if args.state_command == "show":
            with db.connect(data, read_only=True) as c:
                output(db.get_state(c), compact)
        else:
            output(db.update_state(data, args.text, recorded_by="cli"), compact)
        return EXIT_OK
    if command == "plan":
        if args.plan_command == "add":
            output(db.save_plan(data, args.plan_date, args.workout_type, json.loads(args.segments), args.note, created_by="cli"), compact)
        elif args.plan_command == "list":
            with db.connect(data, read_only=True) as c:
                output(db.list_plans(c, args.limit), compact)
        elif args.plan_command == "show":
            with db.connect(data, read_only=True) as c:
                output(db.get_plan(c, args.date, args.id), compact)
        else:
            output(db.set_plan_status(data, args.plan_id, args.status, args.activity_id), compact)
        return EXIT_OK
    if command == "feeling":
        output(db.add_feeling(data, args.event_date, args.value, args.text, args.activity_id, recorded_by="cli"), compact); return EXIT_OK
    if command == "journal":
        if args.journal_command == "add":
            output(db.add_journal(data, args.event_date, args.kind, args.text, args.activity_id, args.plan_id, recorded_by="cli"), compact)
        else:
            with db.connect(data, read_only=True) as c:
                output(db.search_journal(c, args.query, args.limit), compact)
        return EXIT_OK
    if command == "summary":
        if args.summary_command == "add":
            output(db.add_summary(data, args.kind, args.period, args.text, recorded_by="cli"), compact)
        else:
            with db.connect(data, read_only=True) as c:
                output(db.latest_summary(c, args.kind), compact)
        return EXIT_OK
    if command == "training-plan":
        if args.tp_command == "show":
            with db.connect(data, read_only=True) as c:
                output(db.get_training_plan(c), compact)
        else:
            output(db.set_training_plan(data, args.goal, json.loads(args.phases), json.loads(args.milestones), args.reason, recorded_by="cli"), compact)
        return EXIT_OK
    if command == "analysis":
        from .analysis import analysis
        params = {k: v for k, v in (("activity_id", args.activity_id), ("weeks", args.weeks), ("reference_hr", args.reference_hr)) if v is not None}
        with db.connect(data, read_only=True) as c:
            output(analysis(c, args.kind, **params), compact)
        return EXIT_OK
    if command == "health":
        with db.connect(data, read_only=True) as c:
            output(db.recent_health(c, args.days), compact)
        return EXIT_OK
    if command == "backup":
        path = db.backup_database(data, keep=config.backups_keep)
        output({"backup": str(path) if path else None, "note": None if path else "dnešná záloha už existuje"}, compact); return EXIT_OK
    if command == "restore":
        output({"restored_from": str(args.source), "previous": str(db.restore_database(data, args.source))}, compact); return EXIT_OK
    if command == "rebuild":
        from .rebuild import rebuild
        output(rebuild(data, config), compact); return EXIT_OK
    if command == "render":
        from .render import render
        with db.connect(data, read_only=True) as c:
            output(render(c, data), compact)
        return EXIT_OK
    if command == "login":
        from .garmin_sync import interactive_login
        return interactive_login(config, compact)
    if command == "sync":
        from .garmin_sync import sync
        result, code = sync(config, data, force_health=args.force_health)
        output(result, compact)
        return code
    return _fail(f"Neznámy príkaz {command}", EXIT_ERROR)


if __name__ == "__main__":
    raise SystemExit(main())
