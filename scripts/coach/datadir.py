"""Data directory lifecycle: marker, init (never adopts a foreign directory) and attach (existing marker)."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from . import DATA_FORMAT, VERSION
from .layout import DataPaths
from .paths import assert_plain_path, read_json, write_json


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _check_location(path: Path) -> None:
    if not path.is_absolute():
        raise ValueError("Dátový adresár musí byť absolútna cesta.")
    text = str(path)
    if text.startswith("\\\\") or text.startswith("//"):
        raise ValueError("Dátový adresár nesmie byť sieťová cesta (UNC).")
    assert_plain_path(path)


def init_data_dir(path: Path, database_name: str, fit_dir_name: str) -> DataPaths:
    """Create a new data directory. Refuses a non-empty directory without our marker."""
    path = Path(path)
    _check_location(path)
    if path.exists() and (not path.is_dir() or any(path.iterdir())):
        raise ValueError(f"Nový dátový adresár musí byť prázdny alebo neexistujúci: {path}")
    data = DataPaths(path, database_name, fit_dir_name)
    path.mkdir(parents=True, exist_ok=True)
    for sub in data.subdirs():
        sub.mkdir(parents=True, exist_ok=True)
    write_json(data.marker, {"format": DATA_FORMAT, "data_id": str(uuid.uuid4()), "created_at": utcnow(),
                             "app_version": VERSION, "database": database_name, "fit_dir": fit_dir_name})
    return data


def attach_data_dir(path: Path, database_name: str, fit_dir_name: str) -> DataPaths:
    """Use an existing data directory (e.g. synced from another PC). Nothing is created except
    disposable subdirectories; nothing is overwritten."""
    path = Path(path)
    _check_location(path)
    data = DataPaths(path, database_name, fit_dir_name)
    if not data.marker.is_file():
        raise ValueError(f"{path} nie je dátový adresár Bimbo trénera (chýba bimbo-data.json). "
                         "Použite 'init' pre nový alebo vyberte existujúci.")
    marker = read_json(data.marker)
    if marker.get("format") != DATA_FORMAT or not marker.get("data_id"):
        raise ValueError("Neplatný marker dátového adresára.")
    if marker.get("database", database_name) != database_name or marker.get("fit_dir", fit_dir_name) != fit_dir_name:
        raise ValueError("Marker dátového adresára má iný názov databázy alebo priečinka FIT než konfigurácia.")
    for sub in data.subdirs():
        sub.mkdir(parents=True, exist_ok=True)
    return data


def open_data_dir(path: Path, database_name: str, fit_dir_name: str) -> DataPaths:
    """Attach, or init when the directory does not exist yet or is empty (installer's choice dialog)."""
    path = Path(path)
    if path.is_dir() and (DataPaths(path, database_name, fit_dir_name).marker.is_file()):
        return attach_data_dir(path, database_name, fit_dir_name)
    return init_data_dir(path, database_name, fit_dir_name)


def marker_info(data: DataPaths) -> dict:
    info = read_json(data.marker)
    info["path"] = os.fspath(data.root)
    return info
