from __future__ import annotations

import pandas as pd

TONELADAS_POR_KG = 1 / 1000


def produtividade(quantidade_t: pd.Series, area_colhida_ha: pd.Series) -> pd.Series:
    """Rendimento da lavoura em toneladas por hectare."""
    return _safe_ratio(quantidade_t, area_colhida_ha)


def participacao_regional(producao: pd.Series, total_agregado: float) -> pd.Series:
    """Peso relativo de cada unidade sobre o total, em porcentagem."""
    if total_agregado == 0:
        return pd.Series([pd.NA] * len(producao), index=producao.index, dtype="Float64")
    return producao / total_agregado * 100


def desvio_vs_referencia(valor: pd.Series, referencia: float) -> pd.Series:
    """Distância percentual de cada valor frente a uma referência de comparação."""
    if referencia == 0:
        return pd.Series([pd.NA] * len(valor), index=valor.index, dtype="Float64")
    return (valor - referencia) / referencia * 100


def variacao_periodo(serie_ordenada: pd.Series) -> pd.Series:
    """Variação percentual de um período para o seguinte."""
    return serie_ordenada.pct_change() * 100


def mix_etanol_acucar(
    etanol_mil_l: pd.Series, acucar_mil_t: pd.Series
) -> pd.Series:
    """Proporção entre etanol produzido (mil L) e açúcar produzido (mil t)."""
    return _safe_ratio(etanol_mil_l, acucar_mil_t)


def _safe_ratio(numerador: pd.Series, denominador: pd.Series) -> pd.Series:
    denominador = denominador.replace(0, pd.NA)
    return (numerador / denominador).astype("Float64")
