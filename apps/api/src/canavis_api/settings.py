import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    static_dir: Path

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Settings":
        fonte = os.environ if env is None else env
        return cls(
            data_dir=Path(fonte.get("CANAVIS_DATA_DIR", "data/processed")),
            static_dir=Path(fonte.get("CANAVIS_STATIC_DIR", "apps/web/dist")),
        )
