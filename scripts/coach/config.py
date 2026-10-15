"""Configuration: bimbo-trener.json (committed) -> bimbo-trener.local.json (per PC) -> explicit overrides.

The committed file never carries `garmin_sync_enabled`; that key is honoured only from the local
override or an explicit parameter, so a synced repository cannot switch downloading on elsewhere.
"""
from __future__ import annotations

import copy
import os
from dataclasses import dataclass, field
from pathlib import Path

from .paths import read_json

CONFIG_NAME = "bimbo-trener.json"
LOCAL_NAME = "bimbo-trener.local.json"
SCHEMA_VERSION = 1
LOCAL_ONLY_KEYS = {"garmin_sync_enabled"}

DEFAULTS: dict = {
    "schema_version": SCHEMA_VERSION,
    "install_root": "../bimbo-trener-app",
    "data_dir": None,
    "database": "runs.sqlite3",
    "fit_dir": "fit",
    "backups": {"keep": 5},
    "sync": {"health_days": 4, "cooldown_minutes": 90, "daily_task_time": "07:30", "request_pause_seconds": 1.0},
    "garmin": {"token_dir": "<app>/config/garmin"},
    "garmin_sync_enabled": False,
}


def repository_root(start: Path | None = None) -> Path:
    """The repository (or installed app) root: the directory holding bimbo-trener.json above this package."""
    here = (start or Path(__file__)).resolve()
    for candidate in (here, *here.parents):
        if (candidate / CONFIG_NAME).is_file():
            return candidate
    raise FileNotFoundError(f"{CONFIG_NAME} sa nenašiel nad {here}")


def _merge(base: dict, override: dict) -> dict:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


def _validate(config: dict, source: Path) -> None:
    if config.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"{source}: schema_version musí byť {SCHEMA_VERSION}")
    if not isinstance(config.get("backups", {}).get("keep"), int) or config["backups"]["keep"] < 1:
        raise ValueError(f"{source}: backups.keep musí byť celé číslo >= 1")
    sync = config.get("sync", {})
    if not isinstance(sync.get("health_days"), int) or not 1 <= sync["health_days"] <= 30:
        raise ValueError(f"{source}: sync.health_days musí byť 1..30")
    if not isinstance(sync.get("cooldown_minutes"), int) or sync["cooldown_minutes"] < 1:
        raise ValueError(f"{source}: sync.cooldown_minutes musí byť celé číslo >= 1")
    for key in ("database", "fit_dir"):
        value = config.get(key)
        if not isinstance(value, str) or not value or Path(value).is_absolute() or "/" in value or "\\" in value:
            raise ValueError(f"{source}: {key} musí byť jednoduchý názov relatívny k dátovému adresáru")


@dataclass(frozen=True)
class Config:
    root: Path                      # repository or installed app root (where bimbo-trener.json lives)
    values: dict = field(repr=False)

    @property
    def app_root(self) -> Path:
        value = os.path.expandvars(str(self.values["install_root"]))
        path = Path(value)
        if not path.is_absolute():
            path = (self.root / path)
        return Path(os.path.normpath(path))

    @property
    def data_dir(self) -> Path | None:
        value = self.values.get("data_dir")
        if not value:
            return None
        return Path(os.path.normpath(os.path.expandvars(str(value))))

    @property
    def database_name(self) -> str:
        return self.values["database"]

    @property
    def fit_dir_name(self) -> str:
        return self.values["fit_dir"]

    @property
    def backups_keep(self) -> int:
        return int(self.values["backups"]["keep"])

    @property
    def sync(self) -> dict:
        return dict(self.values["sync"])

    @property
    def garmin_sync_enabled(self) -> bool:
        return bool(self.values.get("garmin_sync_enabled", False))

    @property
    def token_dir(self) -> Path:
        value = str(self.values["garmin"]["token_dir"]).replace("<app>", str(self.app_root))
        return Path(os.path.normpath(os.path.expandvars(value)))


def load_config(root: Path | None = None, overrides: dict | None = None) -> Config:
    root = (root or repository_root()).resolve()
    committed = read_json(root / CONFIG_NAME)
    for key in LOCAL_ONLY_KEYS & set(committed):
        raise ValueError(f"{CONFIG_NAME} nesmie obsahovať {key}; patrí iba do {LOCAL_NAME}")
    values = _merge(DEFAULTS, committed)
    local_path = root / LOCAL_NAME
    if local_path.is_file():
        values = _merge(values, read_json(local_path))
    if overrides:
        values = _merge(values, {k: v for k, v in overrides.items() if v is not None})
    _validate(values, root / CONFIG_NAME)
    return Config(root=root, values=values)


def write_local_override(root: Path, updates: dict) -> Path:
    """Merge keys into bimbo-trener.local.json (per PC, ignored by Git)."""
    from .paths import write_json
    path = root / LOCAL_NAME
    current = read_json(path) if path.is_file() else {}
    write_json(path, _merge(current, updates))
    return path
