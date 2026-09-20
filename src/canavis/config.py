from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

_CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class HttpSettings:
    timeout_seconds: int
    user_agent: str


@dataclass(frozen=True)
class LayerPaths:
    raw: Path
    interim: Path
    processed: Path

    def ensure_exist(self) -> None:
        for path in (self.raw, self.interim, self.processed):
            path.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class StorageSettings:
    format: str
    compression: str


@dataclass(frozen=True)
class Settings:
    http: HttpSettings
    paths: LayerPaths
    storage: StorageSettings
    log_level: str
    log_format: str


def _read_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@lru_cache
def load_settings() -> Settings:
    raw = _read_yaml(_CONFIG_DIR / "settings.yaml")
    paths = raw["paths"]
    return Settings(
        http=HttpSettings(**raw["http"]),
        paths=LayerPaths(
            raw=_PROJECT_ROOT / paths["raw"],
            interim=_PROJECT_ROOT / paths["interim"],
            processed=_PROJECT_ROOT / paths["processed"],
        ),
        storage=StorageSettings(**raw["storage"]),
        log_level=raw["logging"]["level"],
        log_format=raw["logging"]["format"],
    )


@lru_cache
def load_sources() -> dict[str, dict]:
    return _read_yaml(_CONFIG_DIR / "sources.yaml")


def source_config(key: str) -> dict:
    sources = load_sources()
    if key not in sources:
        raise KeyError(f"Fonte '{key}' não encontrada em sources.yaml")
    return sources[key]
