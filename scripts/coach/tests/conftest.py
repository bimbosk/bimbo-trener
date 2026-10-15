import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A throwaway repository root with a committed config pointing to a data dir inside tmp."""
    root = tmp_path / "repo"
    root.mkdir()
    (root / "bimbo-trener.json").write_text(json.dumps({
        "schema_version": 1, "install_root": "../bimbo-trener-app", "data_dir": str(tmp_path / "data"),
        "database": "runs.sqlite3", "fit_dir": "fit", "backups": {"keep": 3},
        "sync": {"health_days": 2, "cooldown_minutes": 90, "daily_task_time": "07:30", "request_pause_seconds": 0.0},
        "garmin": {"token_dir": "<app>/config/garmin"}}), encoding="utf-8")
    return root


@pytest.fixture
def data(repo: Path):
    from scripts.coach.config import load_config
    from scripts.coach.datadir import init_data_dir
    from scripts.coach import db
    config = load_config(repo)
    paths = init_data_dir(config.data_dir, config.database_name, config.fit_dir_name)
    db.ensure_schema(paths)
    return paths
