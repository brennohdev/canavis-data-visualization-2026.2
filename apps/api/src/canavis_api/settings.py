"""Configuração da API por variáveis de ambiente (ver `.env.example`)."""

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    static_dir: Path
    port: int
    log_level: str


@lru_cache
def get_settings() -> Settings:
    # PORT é o fallback usado por hospedagens como o Render (plano B de deploy).
    porta = os.environ.get("CANAVIS_PORT") or os.environ.get("PORT") or "7860"
    return Settings(
        data_dir=Path(os.environ.get("CANAVIS_DATA_DIR", "data/processed")),
        static_dir=Path(os.environ.get("CANAVIS_STATIC_DIR", "apps/web/dist")),
        port=int(porta),
        log_level=os.environ.get("CANAVIS_LOG_LEVEL", "info"),
    )
