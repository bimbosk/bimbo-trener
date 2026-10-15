"""Paths owned by the application and by the data directory; nothing else composes these."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    root: Path

    @property
    def runtime(self) -> Path: return self.root / "runtime"
    @property
    def venv(self) -> Path: return self.runtime / "venv"
    @property
    def config(self) -> Path: return self.root / "config"
    @property
    def logs(self) -> Path: return self.root / "logs"
    @property
    def management(self) -> Path: return self.root / "sprava"
    @property
    def marker(self) -> Path: return self.root / ".bimbo-trener-installer"
    @property
    def scripts(self) -> Path: return self.root / "scripts"
    @property
    def cooldown_file(self) -> Path: return self.config / "sync-cooldown.txt"


@dataclass(frozen=True)
class DataPaths:
    root: Path
    database_name: str = "runs.sqlite3"
    fit_dir_name: str = "fit"

    @property
    def marker(self) -> Path: return self.root / "bimbo-data.json"
    @property
    def database(self) -> Path: return self.root / self.database_name
    @property
    def fit(self) -> Path: return self.root / self.fit_dir_name
    @property
    def fit_manual(self) -> Path: return self.fit / "manual"
    @property
    def backups(self) -> Path: return self.root / "backups"
    @property
    def preview(self) -> Path: return self.root / "preview"
    @property
    def logs(self) -> Path: return self.root / "logs"
    @property
    def journal_export(self) -> Path: return self.root / "journal-export.jsonl"
    @property
    def write_lock(self) -> Path: return self.root / "writer.lock"

    def subdirs(self) -> tuple[Path, ...]:
        return (self.fit, self.fit_manual, self.backups, self.preview, self.logs)
