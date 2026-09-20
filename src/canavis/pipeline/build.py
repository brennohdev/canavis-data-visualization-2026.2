from __future__ import annotations

from pathlib import Path

import pandas as pd

from canavis import storage
from canavis.config import load_settings
from canavis.domain import indicators
from canavis.logging import get_logger

_log = get_logger(__name__)

_VARIAVEL_QUANTIDADE = "Quantidade produzida"
_VARIAVEL_AREA = "Área colhida"


def build_all() -> dict[str, Path]:
    """Camada gold: aplica indicadores e grava datasets prontos em data/processed."""
    settings = load_settings()

    ibge = storage.read(settings.paths.interim, "ibge_pam")

    produtividade = _build_produtividade(ibge)
    destination = storage.write(produtividade, settings.paths.processed, "produtividade_regional")
    _log.info("gold | produtividade_regional | %d linhas | %s", len(produtividade), destination.name)

    return {"produtividade_regional": destination}


def _build_produtividade(ibge: pd.DataFrame) -> pd.DataFrame:
    wide = (
        ibge.pivot_table(
            index=["extracao", "cod_local", "local", "periodo"],
            columns="variavel",
            values="valor",
            aggfunc="first",
        )
        .reset_index()
    )
    wide["produtividade_t_ha"] = indicators.produtividade(
        wide[_VARIAVEL_QUANTIDADE], wide[_VARIAVEL_AREA]
    )

    referencia = wide["produtividade_t_ha"].mean(skipna=True)
    wide["desvio_vs_media_pct"] = indicators.desvio_vs_referencia(
        wide["produtividade_t_ha"], referencia
    )
    return wide
