import numpy as np
import pandas as pd
import pytest

from canavis.domain import features


def test_tendencia_anual_crescente():
    periodos = pd.Series([2019, 2020, 2021, 2022, 2023])
    prod = pd.Series([50.0, 52.0, 54.0, 56.0, 58.0])
    assert features.tendencia_anual(periodos, prod) == pytest.approx(2.0)


def test_tendencia_serie_curta_retorna_nan():
    periodos = pd.Series([2022, 2023])
    prod = pd.Series([50.0, 52.0])
    assert np.isnan(features.tendencia_anual(periodos, prod))


def test_resiliencia_entre_zero_e_um():
    prod = pd.Series([40.0, 55.0, 60.0, 58.0, 62.0, 30.0, 59.0])
    resultado = features.resiliencia_climatica(prod)
    assert 0.0 < resultado <= 1.0


def test_elasticidade_area_produtividade_positiva():
    area = pd.Series([100.0, 110.0, 120.0, 130.0])
    prod = pd.Series([50.0, 52.0, 54.0, 56.0])
    assert features.elasticidade_area_produtividade(area, prod) == pytest.approx(1.0, abs=0.01)


def test_intensidade_industrial():
    acucar = pd.Series([100.0, 0.0])
    cana = pd.Series([1000.0, 500.0])
    resultado = features.intensidade_industrial(acucar, cana)
    assert resultado.iloc[0] == pytest.approx(0.1)
    assert resultado.iloc[1] == pytest.approx(0.0)


def test_decompor_recupera_tendencia_linear():
    anos = pd.Series(range(2003, 2024))
    valores = 2.0 * (anos - 2003) + 40
    resultado = features.decompor_serie_anual(anos, valores)
    assert resultado.tendencia_t_ha.iloc[1:-1].to_numpy() == pytest.approx(valores.iloc[1:-1])
    assert resultado.tendencia_t_ha.iloc[[0, -1]].isna().all()


def test_varredura_supf_detecta_quebra_injetada():
    anos = pd.Series(range(2003, 2024))
    ruido = np.random.default_rng(42).normal(0, 0.5, len(anos))
    quebra = pd.Series(50 + 0.2 * (anos - 2003) + ruido + (anos > 2012) * (20 + 2 * (anos - 2012)))
    chow = features.teste_chow(anos, quebra)
    sup = features.varredura_supf(anos, quebra)
    assert chow["p_chow"] < 0.05
    assert sup["status"] == "endogeno"
    assert sup["sup_f"] > chow["f_chow"] or sup["sup_f"] == pytest.approx(chow["f_chow"])
    assert 2010 <= sup["ano_sup"] <= 2015


def test_varredura_supf_controle_sem_falso_positivo():
    anos = pd.Series(range(2003, 2024))
    ruido = np.random.default_rng(42).normal(0, 0.5, len(anos))
    controle = pd.Series(50 + 0.2 * (anos - 2003) + ruido)
    chow = features.teste_chow(anos, controle)
    sup = features.varredura_supf(anos, controle)
    assert chow["p_chow"] > 0.05
    assert sup["status"] == "endogeno"
    assert sup["sup_f"] < 10.0


def test_varredura_supf_serie_curta_indisponivel():
    anos = pd.Series(range(2003, 2024))
    valores = pd.Series(np.arange(21, dtype=float))
    valores.iloc[10] = np.nan
    resultado = features.varredura_supf(anos, valores)
    assert resultado["status"] == "serie_incompleta_ou_curta"
    assert np.isnan(resultado["sup_f"])


def test_fdr_bh_mais_conservador_que_alfa_bruto():
    # Todos abaixo de 0.05 bruto, mas sob BH com alfa=0.01 so o sinal forte (0.001)
    # cruza o limiar escalonado; o BH inflaciona os p-ajustados e rejeita menos.
    pvals = pd.Series([0.001, 0.045, 0.046, 0.047, 0.048])
    resultado = features.fdr_benjamini_hochberg(pvals, alfa=0.01)
    rejeicoes_brutas = int((pvals < 0.05).sum())
    assert rejeicoes_brutas == 5
    assert resultado["n_rejeitado"] < rejeicoes_brutas
    assert resultado["rejeitado"][0]
    assert resultado["n_total"] == 5
    assert np.all(resultado["p_ajustado"] >= pvals.to_numpy() - 1e-12)


def test_fdr_bh_mantem_p_muito_baixo_e_ignora_nan():
    pvals = pd.Series([0.0001, 0.04, 0.5, np.nan])
    resultado = features.fdr_benjamini_hochberg(pvals, alfa=0.05)
    assert resultado["n_total"] == 3
    assert resultado["rejeitado"][0]
    assert not resultado["rejeitado"][3]
    assert np.isnan(resultado["p_ajustado"][3])
    assert resultado["p_ajustado"][0] >= pvals.iloc[0]
