"""Path safety helpers shared by every module: no symlinks or junctions, atomic writes."""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path


def assert_plain_path(path: Path) -> None:
    """Refuse paths that pass through a symlink or Windows junction (never write through links)."""
    for part in (path, *path.parents):
        if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
            raise RuntimeError(f"Cesta vedie cez symbolický odkaz alebo junction: {part}")


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Write via a temporary file in the same directory and an atomic replace."""
    assert_plain_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.pending-{uuid.uuid4().hex}")
    try:
        with temporary.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def write_json(path: Path, value: dict) -> None:
    atomic_write_bytes(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def read_json(path: Path) -> dict:
    assert_plain_path(path)
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Očakávaný JSON objekt: {path}")
    return value


def append_line(path: Path, line: str) -> None:
    """Append-only text file (journal export); never truncates."""
    assert_plain_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(line.rstrip("\n") + "\n")
        stream.flush()
        os.fsync(stream.fileno())
