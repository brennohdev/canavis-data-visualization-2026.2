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


def test_produtividade_ponderada_e_razao_de_agregados():
    assert indicators.produtividade_ponderada([100.0, 50.0], [10.0, 20.0]) == pytest.approx(5.0)


def test_produtividade_ponderada_ausente_em_qualquer_parcela_devolve_na():
    assert pd.isna(indicators.produtividade_ponderada([100.0, pd.NA], [10.0, 20.0]))
    assert pd.isna(indicators.produtividade_ponderada([100.0, 50.0], [10.0, float("nan")]))


def test_produtividade_ponderada_preserva_zero_real_e_area_zero_devolve_na():
    assert indicators.produtividade_ponderada([0.0, 50.0], [10.0, 10.0]) == pytest.approx(2.5)
    assert indicators.produtividade_ponderada([0.0], [10.0]) == 0
    assert pd.isna(indicators.produtividade_ponderada([0.0], [0.0]))


def test_participacao_zero_real_e_ausencias():
    assert indicators.participacao(0.0, 50.0) == 0
    assert indicators.participacao(25.0, 100.0) == pytest.approx(25.0)
    assert pd.isna(indicators.participacao(pd.NA, 100.0))
    assert pd.isna(indicators.participacao(25.0, float("nan")))
    assert pd.isna(indicators.participacao(25.0, 0.0))


def test_desvio_percentual_ausencias_e_referencia_zero():
    assert indicators.desvio_percentual(90.0, 100.0) == pytest.approx(-10.0)
    assert pd.isna(indicators.desvio_percentual(pd.NA, 100.0))
    assert pd.isna(indicators.desvio_percentual(90.0, pd.NA))
    assert pd.isna(indicators.desvio_percentual(90.0, 0.0))


def test_desvio_vs_selecao_usa_produtividade_ponderada_da_selecao():
    resultado = indicators.desvio_vs_selecao(4.0, [100.0, 100.0], [20.0, 20.0])
    assert resultado == pytest.approx(-20.0)
    assert pd.isna(indicators.desvio_vs_selecao(4.0, [100.0, pd.NA], [20.0, 20.0]))


def test_desvio_vs_grupo_sem_tier_devolve_na():
    assert indicators.desvio_vs_grupo(6.0, "media escala", [100.0], [20.0]) == pytest.approx(20.0)
    assert pd.isna(indicators.desvio_vs_grupo(6.0, pd.NA, [100.0], [20.0]))
    assert pd.isna(indicators.desvio_vs_grupo(6.0, None, [100.0], [20.0]))


def test_atr_equivalente_aplica_fatores_e_unidades():
    assert indicators.atr_equivalente_acucar(2.0) == pytest.approx(2.0 * 1_000_000 * 1.0495)
    esperado = 1000 * 1.7651 + 2000 * 1.6913
    assert indicators.atr_equivalente_etanol(1.0, 2.0) == pytest.approx(esperado)
    assert pd.isna(indicators.atr_equivalente_acucar(pd.NA))
    assert pd.isna(indicators.atr_equivalente_etanol(1.0, pd.NA))
    assert pd.isna(indicators.atr_equivalente_etanol(float("nan"), 1.0))


def test_share_atr_complementares_e_zero_real():
    acucar = indicators.share_atr_acucar(1.0, 500.0, 500.0)
    etanol = indicators.share_atr_etanol(1.0, 500.0, 500.0)
    assert acucar + etanol == pytest.approx(100.0)
    assert indicators.share_atr_acucar(0.0, 100.0, 100.0) == 0
    assert indicators.share_atr_etanol(0.0, 100.0, 100.0) == pytest.approx(100.0)


def test_share_atr_ausente_ou_total_zero_devolve_na():
    assert pd.isna(indicators.share_atr_acucar(pd.NA, 100.0, 100.0))
    assert pd.isna(indicators.share_atr_acucar(1.0, pd.NA, 100.0))
    assert pd.isna(indicators.share_atr_acucar(1.0, 100.0, pd.NA))
    assert pd.isna(indicators.share_atr_acucar(0.0, 0.0, 0.0))
    assert pd.isna(indicators.share_atr_etanol(0.0, 0.0, 0.0))


def test_anidro_e_hidratado_entram_separados():
    so_anidro = indicators.share_atr_acucar(1.0, 1000.0, 0.0)
    so_hidratado = indicators.share_atr_acucar(1.0, 0.0, 1000.0)
    assert so_anidro != pytest.approx(so_hidratado)
