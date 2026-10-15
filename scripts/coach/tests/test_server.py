import asyncio
import json
from pathlib import Path

import pytest

from scripts.coach import server as server_module


def call(server, name, **arguments):
    result = asyncio.run(server.call_tool(name, arguments))
    # mcp 2.x returns (content, structured) or a CallToolResult-like object; normalise to the structured dict
    if isinstance(result, tuple):
        content, structured = result
        value = structured if structured is not None else json.loads(content[0].text)
    else:
        structured = getattr(result, "structured_content", None)
        if structured is None:
            structured = getattr(result, "structuredContent", None)
        value = structured if structured is not None else json.loads(result.content[0].text)
    if isinstance(value, dict) and set(value) == {"result"}:   # non-object returns are wrapped by the SDK
        return value["result"]
    return value


def test_tools_and_annotations(repo: Path, data):
    server = server_module.create_server(repo)
    tools = asyncio.run(server.list_tools())
    names = {t.name for t in tools}
    assert names == set(server_module.TOOLS)
    by_name = {t.name: t for t in tools}
    for name in server_module.READ_TOOLS:
        assert by_name[name].annotations.read_only_hint is True, name
    for name in server_module.WRITE_TOOLS:
        assert by_name[name].annotations.read_only_hint is False, name


def test_write_then_read_through_server(repo: Path, data):
    server = server_module.create_server(repo)
    state = call(server, "get_state")
    assert state["state"] is None and state["conventions"]["segments"] == "10"
    plan = call(server, "save_plan", plan_date="2026-10-16", workout_type="easy",
                segments=[{"minutes": 5, "speed_kmh": 8, "incline_percent": 0}] * 10)
    assert plan["total_minutes"] == 50
    call(server, "add_feeling", event_date="2026-10-15", value="ok", text="v pohode")
    call(server, "add_journal", event_date="2026-10-15", kind="circumstance", text="teplo")
    call(server, "update_state", text="fáza základ")
    assert call(server, "get_state")["state"]["text"] == "fáza základ"
    journal = call(server, "recent_journal", days=3650)
    assert {row["kind"] for row in journal} >= {"feeling", "circumstance", "decision"}
    assert call(server, "get_plan", plan_date="2026-10-16")["plan_id"] == plan["plan_id"]
    assert call(server, "status")["journal_export_lines"] == 4
    sync = call(server, "run_sync")
    assert sync["exit_code"] == 77
