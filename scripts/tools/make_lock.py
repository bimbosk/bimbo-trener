"""Build scripts/requirements.lock (name==version --hash=sha256:…) from a directory of downloaded wheels.

Usage: python -m scripts.tools.make_lock <wheel_dir>
The wheels come from: pip download --only-binary=:all: --platform win_amd64 --python-version 3.14
--implementation cp --abi cp314 --abi abi3 --abi none -r scripts/requirements.in -d <wheel_dir>
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^(?P<name>[A-Za-z0-9_.]+)-(?P<version>[^-]+)-")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__); return 1
    wheel_dir = Path(argv[1])
    entries = {}
    for wheel in sorted(wheel_dir.glob("*.whl")):
        match = NAME_RE.match(wheel.name)
        if not match:
            print(f"preskočené: {wheel.name}"); continue
        name = match.group("name").replace("_", "-").lower()
        digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
        entries.setdefault((name, match.group("version")), []).append(digest)
    lock = Path(__file__).resolve().parents[1] / "requirements.lock"
    lines = ["# Generované scripts/tools/make_lock.py pre win_amd64 / CPython 3.14; neupravovať ručne.",
             "# Inštalácia: uv pip install --require-hashes -r scripts/requirements.lock", ""]
    for (name, version), digests in sorted(entries.items()):
        hashes = " \\\n    ".join(f"--hash=sha256:{d}" for d in digests)
        lines.append(f"{name}=={version} \\\n    {hashes}")
    lock.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{lock}: {len(entries)} balíkov")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
