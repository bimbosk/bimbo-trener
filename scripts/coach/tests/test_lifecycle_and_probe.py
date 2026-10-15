import asyncio
import os
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from scripts import lifecycle
from scripts.coach import OWNER
from scripts.coach.layout import AppPaths


def test_codex_toml_registration_preserves_foreign_entries(tmp_path: Path, monkeypatch):
    app_root = tmp_path / "app"; app_root.mkdir(); (app_root / ".bimbo-trener-installer").write_text(OWNER)
    app = AppPaths(app_root)
    codex_home = tmp_path / "codex"; codex_home.mkdir()
    (codex_home / "config.toml").write_text('model = "x"\n\n[mcp_servers.other]\ncommand = "foo"\n', encoding="utf-8")
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    lifecycle.register_codex(app)
    parsed = tomllib.loads((codex_home / "config.toml").read_text(encoding="utf-8"))
    assert parsed["model"] == "x" and parsed["mcp_servers"]["other"]["command"] == "foo"
    entry = parsed["mcp_servers"]["bimbo_trener"]
    assert entry["args"][:2] == ["-m", "scripts.coach.server"] and entry["cwd"] == str(app_root)
    assert list((app.management / "zalohy").glob("codex-config-*.toml"))
    lifecycle.register_codex(app)   # idempotent
    # foreign change is never overwritten
    text = (codex_home / "config.toml").read_text(encoding="utf-8").replace('cwd = ', 'cwd = "/elsewhere" #')
    (codex_home / "config.toml").write_text(text, encoding="utf-8")
    with pytest.raises(RuntimeError):
        lifecycle.unregister_codex(app)


def test_codex_unregister_restores(tmp_path: Path, monkeypatch):
    app_root = tmp_path / "app"; app_root.mkdir(); (app_root / ".bimbo-trener-installer").write_text(OWNER)
    app = AppPaths(app_root)
    codex_home = tmp_path / "codex"; codex_home.mkdir()
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    lifecycle.register_codex(app)
    assert "bimbo_trener" in tomllib.loads((codex_home / "config.toml").read_text())["mcp_servers"]
    lifecycle.unregister_codex(app)
    assert "bimbo_trener" not in tomllib.loads((codex_home / "config.toml").read_text()).get("mcp_servers", {})
    assert lifecycle.load_journal(app)["codex"] is None


def test_mcp_stdio_handshake(repo: Path, data):
    """The installed-copy probe: start the server as a subprocess over stdio and list its tools."""
    from scripts.coach.server import TOOLS

    async def probe():
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        params = StdioServerParameters(command=sys.executable, args=["-m", "scripts.coach.server", "--root", str(repo)],
                                       cwd=str(Path(__file__).resolve().parents[3]),
                                       env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"))
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await asyncio.wait_for(session.initialize(), timeout=60)
                tools = await asyncio.wait_for(session.list_tools(), timeout=60)
                result = await asyncio.wait_for(session.call_tool("status", {}), timeout=60)
                return {t.name for t in tools.tools}, result

    names, result = asyncio.run(probe())
    assert names == set(TOOLS)
    assert not getattr(result, "is_error", getattr(result, "isError", False))


def test_cli_module_runs_as_subprocess(repo: Path, data):
    result = subprocess.run([sys.executable, "-m", "scripts.coach.cli", "--root", str(repo), "--compact", "status"],
                            cwd=str(Path(__file__).resolve().parents[3]), capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stderr
    assert '"counts"' in result.stdout
