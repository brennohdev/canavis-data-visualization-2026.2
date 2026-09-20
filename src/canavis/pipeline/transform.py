from __future__ import annotations

from pathlib import Path

import pandas as pd

from canavis import storage
from canavis.config import load_settings
from canavis.logging import get_logger

_log = get_logger(__name__)

_MISSING_TOKENS = {"-", "..", "...", "X"}


def transform_all() -> dict[str, Path]:
    """Camada silver: padroniza tipos e valores ausentes em data/interim."""
    settings = load_settings()

    transformers = {
        "ibge_pam": _transform_ibge,
        "conab_cana": _transform_conab,
        "anp_vendas_etanol": _transform_anp_vendas,
        "anp_producao_etanol": _transform_anp_producao,
    }

    written: dict[str, Path] = {}
    for key, transformer in transformers.items():
        if not storage.exists(settings.paths.raw, key):
            _log.warning("silver | %s | ausente em raw, pulando", key)
            continue
        frame = transformer(storage.read(settings.paths.raw, key))
        destination = storage.write(frame, settings.paths.interim, key)
        _log.info("silver | %s | %d linhas | %s", key, len(frame), destination.name)
        written[key] = destination
    return written


def _to_numeric(series: pd.Series) -> pd.Series:
    cleaned = series.astype(str).str.strip().replace(_MISSING_TOKENS, pd.NA)
    cleaned = cleaned.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(cleaned, errors="coerce")


def _transform_ibge(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame["valor"] = _to_numeric(frame["valor"])
    frame["periodo"] = pd.to_numeric(frame["periodo"], errors="coerce").astype("Int64")
    return frame.dropna(subset=["valor"])


def _transform_conab(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    for column in frame.columns:
        if column not in {"ano_agricola", "dsc_safra_previsao", "uf", "produto", "dsc_situacao_levantamento"}:
            frame[column] = _to_numeric(frame[column])
    return frame


def _transform_anp_vendas(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [c.lower().replace(" ", "_") for c in frame.columns]
    frame["vendas"] = _to_numeric(frame["vendas"])
    return frame


def _transform_anp_producao(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [c.lower().replace(" ", "_") for c in frame.columns]
    frame["produção"] = _to_numeric(frame["produção"])
    return frame
