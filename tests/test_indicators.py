import pandas as pd
import pytest

from canavis.domain import indicators


def test_produtividade_reproduz_rendimento_conhecido():
    quantidade = pd.Series([5_763_000.0])
    area = pd.Series([89_083.0])
    resultado = indicators.produtividade(quantidade, area)
    assert resultado.iloc[0] == pytest.approx(64.69, abs=0.01)


def test_produtividade_com_area_zero_retorna_ausente():
    resultado = indicators.produtividade(pd.Series([100.0]), pd.Series([0.0]))
    assert pd.isna(resultado.iloc[0])


def test_participacao_regional_soma_cem():
    producao = pd.Series([25.0, 75.0])
    resultado = indicators.participacao_regional(producao, total_agregado=100.0)
    assert resultado.tolist() == [25.0, 75.0]


def test_participacao_regional_total_zero_retorna_ausente():
    resultado = indicators.participacao_regional(pd.Series([10.0]), total_agregado=0.0)
    assert pd.isna(resultado.iloc[0])


def test_desvio_vs_referencia_positivo_e_negativo():
    valores = pd.Series([120.0, 80.0])
    resultado = indicators.desvio_vs_referencia(valores, referencia=100.0)
    assert resultado.tolist() == [20.0, -20.0]


def test_variacao_periodo():
    serie = pd.Series([100.0, 110.0, 99.0])
    resultado = indicators.variacao_periodo(serie)
    assert pd.isna(resultado.iloc[0])
    assert resultado.iloc[1] == pytest.approx(10.0)
    assert resultado.iloc[2] == pytest.approx(-10.0)


def test_mix_etanol_acucar():
    etanol = pd.Series([200.0])
    acucar = pd.Series([100.0])
    resultado = indicators.mix_etanol_acucar(etanol, acucar)
    assert resultado.iloc[0] == pytest.approx(2.0)
