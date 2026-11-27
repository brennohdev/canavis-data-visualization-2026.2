from __future__ import annotations

import pandas as pd

TONELADAS_POR_KG = 1 / 1000
FATOR_ATR_ACUCAR = 1.0495
FATOR_ATR_ETANOL_ANIDRO = 1.7651
FATOR_ATR_ETANOL_HIDRATADO = 1.6913
KG_POR_MIL_T = 1_000_000
L_POR_MIL_L = 1_000


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


def _ausente(valor) -> bool:
    return valor is None or bool(pd.isna(valor))


def _soma(valores) -> float:
    return float(sum(float(v) for v in valores))


def produtividade_ponderada(quantidade_t, area_ha):
    quantidades = list(pd.Series(quantidade_t, dtype="Float64"))
    areas = list(pd.Series(area_ha, dtype="Float64"))
    if not quantidades or not areas:
        return pd.NA
    if any(_ausente(v) for v in quantidades) or any(_ausente(v) for v in areas):
        return pd.NA
    area_total = _soma(areas)
    if area_total == 0:
        return pd.NA
    return _soma(quantidades) / area_total


def participacao(valor, total):
    if _ausente(valor) or _ausente(total) or float(total) == 0:
        return pd.NA
    return float(valor) / float(total) * 100


def desvio_percentual(valor, referencia):
    if _ausente(valor) or _ausente(referencia) or float(referencia) == 0:
        return pd.NA
    return (float(valor) - float(referencia)) / float(referencia) * 100


def desvio_vs_selecao(produtividade_territorio, quantidade_selecao, area_selecao):
    referencia = produtividade_ponderada(quantidade_selecao, area_selecao)
    return desvio_percentual(produtividade_territorio, referencia)


def desvio_vs_grupo(produtividade_territorio, tier, quantidade_grupo, area_grupo):
    if _ausente(tier):
        return pd.NA
    referencia = produtividade_ponderada(quantidade_grupo, area_grupo)
    return desvio_percentual(produtividade_territorio, referencia)


def atr_equivalente_acucar(acucar_mil_t):
    if _ausente(acucar_mil_t):
        return pd.NA
    return float(acucar_mil_t) * KG_POR_MIL_T * FATOR_ATR_ACUCAR


def atr_equivalente_etanol(anidro_mil_l, hidratado_mil_l):
    if _ausente(anidro_mil_l) or _ausente(hidratado_mil_l):
        return pd.NA
    return (
        float(anidro_mil_l) * L_POR_MIL_L * FATOR_ATR_ETANOL_ANIDRO
        + float(hidratado_mil_l) * L_POR_MIL_L * FATOR_ATR_ETANOL_HIDRATADO
    )


def _atr_total(acucar_mil_t, anidro_mil_l, hidratado_mil_l):
    acucar = atr_equivalente_acucar(acucar_mil_t)
    etanol = atr_equivalente_etanol(anidro_mil_l, hidratado_mil_l)
    if _ausente(acucar) or _ausente(etanol) or acucar + etanol <= 0:
        return pd.NA, pd.NA, pd.NA
    return acucar, etanol, acucar + etanol


def share_atr_acucar(acucar_mil_t, anidro_mil_l, hidratado_mil_l):
    acucar, _, total = _atr_total(acucar_mil_t, anidro_mil_l, hidratado_mil_l)
    if _ausente(total):
        return pd.NA
    return acucar / total * 100


def share_atr_etanol(acucar_mil_t, anidro_mil_l, hidratado_mil_l):
    _, etanol, total = _atr_total(acucar_mil_t, anidro_mil_l, hidratado_mil_l)
    if _ausente(total):
        return pd.NA
    return etanol / total * 100
