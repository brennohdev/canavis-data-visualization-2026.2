from __future__ import annotations

import numpy as np
import pandas as pd


def inclinacao(periodos: pd.Series, valores: pd.Series) -> float:
    """Inclinação da reta ajustada (unidade do valor por período)."""
    mascara = periodos.notna() & valores.notna()
    if mascara.sum() < 2:
        return float("nan")
    x = periodos[mascara].to_numpy(dtype=float)
    y = valores[mascara].to_numpy(dtype=float)
    return float(np.polyfit(x, y, 1)[0])


def coeficiente_variacao(valores: pd.Series) -> float:
    """Desvio-padrão relativo à média, em fração. Mede volatilidade."""
    limpo = valores.dropna()
    media = limpo.mean()
    if media == 0 or limpo.empty:
        return float("nan")
    return float(limpo.std(ddof=1) / media)


def compara_janelas(
    periodos: pd.Series, valores: pd.Series, corte: int
) -> dict[str, float]:
    """Compara a inclinação antes e depois de um período de corte.

    Serve para detectar inversão de regime: uma série que caía e passou a
    subir tem inclinações de sinais opostos, e a inclinação global engana.
    """
    antes = periodos <= corte
    return {
        "inclinacao_antes": inclinacao(periodos[antes], valores[antes]),
        "inclinacao_depois": inclinacao(periodos[~antes], valores[~antes]),
        "inclinacao_total": inclinacao(periodos, valores),
    }
