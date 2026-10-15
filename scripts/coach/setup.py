"""Install-time steps of the coach component, run by scripts/coach/setup.ps1 inside the app venv:
data directory (attach or init), schema, probe of CLI and MCP from the installed copy, optional task."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

from scripts.coach import OWNER, db
from scripts.coach.config import LOCAL_NAME, load_config, write_local_override
from scripts.coach.datadir import open_data_dir
from scripts.coach.layout import AppPaths, DataPaths


def probe_cli(app: AppPaths) -> dict:
    result = subprocess.run([sys.executable, "-m", "scripts.coach.cli", "--root", str(app.root), "--compact", "status"],
                            cwd=str(app.root), capture_output=True, text=True, encoding="utf-8", errors="replace",
                            env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"), timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"CLI v nainštalovanej aplikácii nefunguje: {result.stderr.strip()[-800:]}")
    return json.loads(result.stdout.strip().splitlines()[-1])


async def probe_server(app: AppPaths) -> set[str]:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from scripts.coach.server import TOOLS
    params = StdioServerParameters(command=sys.executable, args=["-m", "scripts.coach.server", "--root", str(app.root)],
                                   cwd=str(app.root), env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await asyncio.wait_for(session.initialize(), timeout=60)
            names = {tool.name for tool in (await asyncio.wait_for(session.list_tools(), timeout=60)).tools}
            if names != set(TOOLS):
                raise RuntimeError(f"MCP nástroje nesedia so špecifikáciou: {sorted(names ^ set(TOOLS))}")
            result = await asyncio.wait_for(session.call_tool("status", {}), timeout=60)
            if getattr(result, "is_error", getattr(result, "isError", False)):
                raise RuntimeError("MCP nástroj status zlyhal.")
            return names


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True, help="koreň nainštalovanej aplikácie")
    p.add_argument("--repo", type=Path, required=True, help="koreň repozitára (zdroj konfigurácie)")
    p.add_argument("--data-dir", type=Path, help="dátový adresár vybraný v dialógu")
    p.add_argument("--prepare-only", action="store_true", help="bez registrácie v asistentoch")
    args = p.parse_args()
    app = AppPaths(args.root.resolve())
    if not app.marker.is_file() or app.marker.read_text(encoding="utf-8").strip() != OWNER:
        raise SystemExit("Koreň aplikácie nemá značku vlastníka bimbo-trener/app/v1.")
    config = load_config(args.repo.resolve(), {"data_dir": str(args.data_dir) if args.data_dir else None})
    if config.data_dir is None:
        raise SystemExit("Dátový adresár nie je určený (bimbo-trener.json, local alebo --data-dir).")
    data = open_data_dir(config.data_dir, config.database_name, config.fit_dir_name)
    created = db.ensure_schema(data)
    committed = load_config(args.repo.resolve()).values.get("data_dir")
    if str(data.root) != str(Path(os.path.normpath(os.path.expandvars(str(committed or ""))))):
        for root in (args.repo.resolve(), app.root):
            write_local_override(root, {"data_dir": str(data.root)})
    print(json.dumps({"data_dir": str(data.root), "schema": created}, ensure_ascii=False))
    print(json.dumps({"cli": probe_cli(app)}, ensure_ascii=False, default=str))
    names = asyncio.run(probe_server(app))
    print(json.dumps({"mcp_tools": sorted(names)}, ensure_ascii=False))
    if args.prepare_only:
        print("Registrácia v asistentoch preskočená (--prepare-only)."); return 0
    from scripts.lifecycle import register_claude, register_codex
    for register in (register_codex, register_claude):
        try:
            print(json.dumps(register(app), ensure_ascii=False))
        except RuntimeError as error:
            print(json.dumps({"warning": str(error)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
