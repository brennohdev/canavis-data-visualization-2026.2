import numpy as np
import pandas as pd
import pytest

from canavis.domain.features import decompor_serie_anual, teste_chow as chow
from canavis.pipeline.temporal import enriquecer_serie


def test_media_movel_recupera_tendencia_linear():
    anos = pd.Series(range(2003, 2024))
    valores = 2.0 * (anos - 2003) + 40
    resultado = decompor_serie_anual(anos, valores)
    assert resultado.tendencia_t_ha.iloc[1:-1].to_numpy() == pytest.approx(valores.iloc[1:-1])
    assert resultado.tendencia_t_ha.iloc[[0, -1]].isna().all()


def test_quebra_injetada_detectada_sem_falso_positivo_no_controle():
    anos = pd.Series(range(2003, 2024))
    ruido = np.random.default_rng(42).normal(0, 0.5, len(anos))
    controle = pd.Series(50 + 0.2 * (anos - 2003) + ruido)
    quebra = controle + (anos > 2012) * (20 + 2 * (anos - 2012))
    assert chow(anos, quebra)["p_chow"] < 0.001
    assert chow(anos, controle)["p_chow"] > 0.05


def test_lacunas_nao_interpoladas_e_teste_indisponivel():
    anos = pd.Series(range(2003, 2024))
    valores = pd.Series(np.arange(21, dtype=float))
    valores.iloc[10] = np.nan
    assert decompor_serie_anual(anos, valores).tendencia_t_ha.iloc[9:12].isna().all()
    assert np.isnan(chow(anos, valores)["p_chow"])
    assert np.isnan(chow(anos, 2.0 * anos)["p_chow"])


def test_materializacao_preserva_municipios_e_nao_confirma_quebra():
    fato = pd.DataFrame({"territorio_id": ["uf:25"] * 21 + ["municipio:1"],
                         "nivel_territorial": ["uf"] * 21 + ["municipio"],
                         "ano_referencia": list(range(2003, 2024)) + [2023],
                         "produtividade_t_ha": list(range(21)) + [50]})
    resultado = enriquecer_serie(fato)
    assert len(resultado) == len(fato)
    assert resultado.quebra_confirmada.isna().all()
    assert resultado.ponto_candidato_quebra.sum() == 1
    assert pd.isna(resultado.iloc[-1].tendencia_t_ha)
