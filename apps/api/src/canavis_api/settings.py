import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


_VERDADEIROS = frozenset({"1", "true", "yes", "on"})


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    static_dir: Path
    external_dir: Path = Path("data/external")
    sources_file: Path = Path("config/sources.yaml")
    intl_live: bool = False

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Settings":
        fonte = os.environ if env is None else env
        return cls(
            data_dir=Path(fonte.get("CANAVIS_DATA_DIR", "data/processed")),
            static_dir=Path(fonte.get("CANAVIS_STATIC_DIR", "apps/web/dist")),
            external_dir=Path(fonte.get("CANAVIS_EXTERNAL_DIR", "data/external")),
            sources_file=Path(fonte.get("CANAVIS_SOURCES_FILE", "config/sources.yaml")),
            intl_live=fonte.get("CANAVIS_INTL_LIVE", "0").strip().lower() in _VERDADEIROS,
        )
