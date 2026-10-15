"""Ownership journal and reversible registration of the MCP server in Codex and Claude Code.

Codex: entry in config.toml (backup of the previous file, foreign entries never overwritten).
Claude Code: `claude mcp add/remove --scope user`. Both are recorded in <app>/sprava/sprava.json so that
uninstall removes only what this installation created.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import subprocess
import sys
import tomllib
import uuid
from pathlib import Path

from scripts.coach import OWNER
from scripts.coach.layout import AppPaths
from scripts.coach.paths import assert_plain_path, atomic_write_bytes, read_json, write_json

SERVER = "bimbo_trener"


def journal_path(app: AppPaths) -> Path:
    return app.management / "sprava.json"


def load_journal(app: AppPaths) -> dict:
    path = journal_path(app)
    return read_json(path) if path.is_file() else {"owner": OWNER, "codex": None, "claude": None, "shortcut": None, "task": None}


def save_journal(app: AppPaths, data: dict) -> None:
    app.management.mkdir(parents=True, exist_ok=True)
    write_json(journal_path(app), data)


def server_definition(app: AppPaths) -> dict:
    python = app.venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    return {"command": str(python), "args": ["-m", "scripts.coach.server", "--root", str(app.root)],
            "cwd": str(app.root), "enabled": True, "startup_timeout_sec": 60, "tool_timeout_sec": 300}


# --- Codex ---------------------------------------------------------------------------------

def codex_config_path() -> Path:
    home = os.environ.get("CODEX_HOME")
    base = Path(home) if home else Path.home() / ".codex"
    if not base.is_absolute():
        raise RuntimeError("CODEX_HOME musí byť absolútna cesta.")
    return base / "config.toml"


def _updated_toml(existing: bytes, desired: dict | None, previous_owned: dict | None) -> bytes:
    import tomlkit
    text = existing.decode("utf-8-sig")
    before = tomllib.loads(text)
    document = tomlkit.parse(text)
    servers = document.setdefault("mcp_servers", tomlkit.table())
    current = before.get("mcp_servers", {}).get(SERVER)
    if current is not None and current != desired and current != previous_owned:
        raise RuntimeError(f"Codex už má cudziu alebo zmenenú registráciu {SERVER}; nebude prepísaná.")
    if desired is None:
        if SERVER in servers:
            del servers[SERVER]
    else:
        entry = tomlkit.table()
        for key, value in desired.items():
            entry[key] = value
        servers[SERVER] = entry
    result = tomlkit.dumps(document).encode("utf-8")
    expected = copy.deepcopy(before)
    expected.setdefault("mcp_servers", {})
    if desired is None:
        expected["mcp_servers"].pop(SERVER, None)
    else:
        expected["mcp_servers"][SERVER] = desired
    actual = tomllib.loads(result.decode("utf-8"))
    for value in (actual, expected):           # tomlkit may drop an emptied [mcp_servers] table
        if value.get("mcp_servers") == {}:
            value.pop("mcp_servers")
    if actual != expected:
        raise RuntimeError("Pri úprave config.toml sa zmenilo nesúvisiace nastavenie; zastavené.")
    return result


def register_codex(app: AppPaths) -> dict:
    config = codex_config_path()
    assert_plain_path(config)
    journal = load_journal(app)
    desired = server_definition(app)
    existing = config.read_bytes() if config.exists() else b""
    previous_owned = (journal.get("codex") or {}).get("after")
    content = _updated_toml(existing, desired, previous_owned)
    before_entry = tomllib.loads(existing.decode("utf-8-sig")).get("mcp_servers", {}).get(SERVER)
    if content != existing:
        if existing:
            backup = app.management / "zalohy" / f"codex-config-{uuid.uuid4().hex}.toml"
            atomic_write_bytes(backup, existing)
        atomic_write_bytes(config, content)
    journal["codex"] = {"config": str(config), "before": before_entry if previous_owned is None else (journal["codex"] or {}).get("before"),
                        "after": desired}
    save_journal(app, journal)
    return {"codex_config": str(config), "server": SERVER}


def unregister_codex(app: AppPaths) -> dict:
    journal = load_journal(app)
    entry = journal.get("codex")
    if not entry:
        return {"codex": "nebolo registrované"}
    config = Path(entry["config"])
    existing = config.read_bytes() if config.exists() else b""
    current = tomllib.loads(existing.decode("utf-8-sig")).get("mcp_servers", {}).get(SERVER)
    if current is None:
        journal["codex"] = None; save_journal(app, journal)
        return {"codex": "už odstránené"}
    if current != entry["after"]:
        raise RuntimeError(f"Registrácia {SERVER} v Codexe bola zmenená; zachovaná, odinštalovanie zastavené.")
    content = _updated_toml(existing, entry.get("before"), entry["after"]) if entry.get("before") else _updated_toml(existing, None, entry["after"])
    backup = app.management / "zalohy" / f"codex-config-{uuid.uuid4().hex}.toml"
    atomic_write_bytes(backup, existing)
    atomic_write_bytes(config, content)
    journal["codex"] = None; save_journal(app, journal)
    return {"codex": "odstránené", "backup": str(backup)}


# --- Claude Code ---------------------------------------------------------------------------

def claude_executable() -> str | None:
    for name in ("claude.cmd", "claude.exe", "claude"):
        found = shutil.which(name)
        if found:
            return found
    return None


def register_claude(app: AppPaths) -> dict:
    claude = claude_executable()
    if not claude:
        return {"claude": "preskočené: príkaz claude nie je v PATH (Claude Code nie je nainštalovaný?)"}
    definition = server_definition(app)
    subprocess.run([claude, "mcp", "remove", "--scope", "user", SERVER], capture_output=True, text=True, timeout=120)
    command = [claude, "mcp", "add", "--scope", "user", "--transport", "stdio", "--env", f"PYTHONPATH={app.root}",
               SERVER, "--", definition["command"], *definition["args"]]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"claude mcp add zlyhalo: {result.stderr.strip()[-500:]}")
    journal = load_journal(app)
    journal["claude"] = {"scope": "user", "server": SERVER, "command": command[1:]}
    save_journal(app, journal)
    return {"claude": "registrované", "server": SERVER}


def unregister_claude(app: AppPaths) -> dict:
    journal = load_journal(app)
    if not journal.get("claude"):
        return {"claude": "nebolo registrované"}
    claude = claude_executable()
    if claude:
        subprocess.run([claude, "mcp", "remove", "--scope", "user", SERVER], capture_output=True, text=True, timeout=120)
    journal["claude"] = None; save_journal(app, journal)
    return {"claude": "odstránené"}


# --- CLI for the installer --------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["register", "unregister"])
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--target", choices=["codex", "claude", "all"], default="all")
    args = p.parse_args()
    app = AppPaths(args.root.resolve())
    if not app.marker.is_file() or app.marker.read_text(encoding="utf-8").strip() != OWNER:
        print(json.dumps({"error": "Koreň aplikácie nemá značku vlastníka."}), file=sys.stderr); return 1
    out = {}
    try:
        if args.target in ("codex", "all"):
            out.update(register_codex(app) if args.action == "register" else unregister_codex(app))
        if args.target in ("claude", "all"):
            out.update(register_claude(app) if args.action == "register" else unregister_claude(app))
    except RuntimeError as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr); return 1
    print(json.dumps(out, ensure_ascii=False)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
