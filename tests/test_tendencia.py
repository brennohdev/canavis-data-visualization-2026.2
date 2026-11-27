import math

import pandas as pd
import pytest

from canavis.domain import tendencia

GOLD = "data/processed/fato_producao_uf.parquet"


@pytest.fixture(scope="module")
def serie_pb():
    uf = pd.read_parquet(GOLD)
    pb = uf[uf["territorio_id"] == "uf:25"].sort_values("ano_referencia")
    return pb["ano_referencia"].tolist(), pb["produtividade_t_ha"].astype(float).tolist()


@pytest.mark.parametrize(
    "janela, sem_ultimo, inclinacao, erro, inferior, superior, classe",
    [
        (10, False, 0.490, 0.316, -0.24, 1.22, "estavel"),
        (5, False, 1.808, 0.975, -1.29, 4.91, "estavel"),
        (21, False, 0.396, 0.126, 0.13, 0.66, "sobe"),
        (5, True, 0.555, None, None, None, "estavel"),
        (10, True, 0.302, None, None, None, "estavel"),
    ],
)
def test_paridade_pb(serie_pb, janela, sem_ultimo, inclinacao, erro, inferior, superior, classe):
    anos, valores = serie_pb
    r = tendencia.tendencia_janela(anos, valores, janela, sem_ultimo=sem_ultimo)
    assert r["status"] == "ok"
    assert r["inclinacao_t_ha_ano"] == pytest.approx(inclinacao, abs=0.001)
    if erro is not None:
        assert r["erro_padrao"] == pytest.approx(erro, abs=0.001)
        assert r["ic95_inferior"] == pytest.approx(inferior, abs=0.01)
        assert r["ic95_superior"] == pytest.approx(superior, abs=0.01)
    assert r["classe"] == classe


def test_janela_sem_ultimo_termina_no_penultimo_ano(serie_pb):
    anos, valores = serie_pb
    r = tendencia.tendencia_janela(anos, valores, 10, sem_ultimo=True)
    assert (r["ano_inicial"], r["ano_final"], r["n"]) == (2013, 2022, 10)


def test_serie_crescente_exata_sobe_com_ic_estreito():
    anos = list(range(2010, 2020))
    valores = [50.0 + 2.0 * i for i in range(10)]
    r = tendencia.tendencia_janela(anos, valores, 10)
    assert r["inclinacao_t_ha_ano"] == pytest.approx(2.0)
    assert r["ic95_superior"] - r["ic95_inferior"] == pytest.approx(0.0, abs=1e-9)
    assert r["classe"] == "sobe"


def test_serie_decrescente_cai():
    anos = list(range(2010, 2020))
    valores = [80.0 - 1.5 * i + (0.1 if i % 2 else -0.1) for i in range(10)]
    r = tendencia.tendencia_janela(anos, valores, 10)
    assert r["inclinacao_t_ha_ano"] < 0
    assert r["classe"] == "cai"


def test_lacuna_de_anos_e_serie_incompleta_sem_interpolar():
    anos = [2010, 2011, 2013, 2014, 2015]
    r = tendencia.tendencia_janela(anos, [1.0, 2.0, 3.0, 4.0, 5.0], 5)
    assert r["status"] == "serie_incompleta"
    assert r["classe"] == "indisponivel"
    assert math.isnan(r["inclinacao_t_ha_ano"])


def test_valor_ausente_e_serie_incompleta():
    anos = [2010, 2011, 2012, 2013, 2014]
    r = tendencia.tendencia_janela(anos, [1.0, float("nan"), 3.0, 4.0, 5.0], 5)
    assert r["status"] == "serie_incompleta"
    assert math.isnan(r["ic95_inferior"])


def test_menos_de_quatro_pontos_e_serie_curta():
    r = tendencia.tendencia_janela([2021, 2022, 2023], [1.0, 2.0, 4.0], 5)
    assert r["status"] == "serie_curta"
    assert r["classe"] == "indisponivel"
    assert r["n"] == 3


def test_serie_vazia_apos_descartar_ultimo_e_curta():
    r = tendencia.tendencia_janela([2023], [1.0], 5, sem_ultimo=True)
    assert r["status"] == "serie_curta"


def test_quantil_t_acima_de_30_graus_usa_normal():
    assert tendencia.quantil_t95(2) == pytest.approx(4.303)
    assert tendencia.quantil_t95(30) == pytest.approx(2.042)
    assert tendencia.quantil_t95(31) == pytest.approx(1.96)


def test_por_janelas_devolve_com_e_sem_ultimo_ano(serie_pb):
    anos, valores = serie_pb
    resultado = tendencia.tendencia_por_janelas(anos, valores)
    assert set(resultado) == {(j, s) for j in (5, 10, 21) for s in (False, True)}
    assert resultado[(10, False)]["inclinacao_t_ha_ano"] == pytest.approx(0.490, abs=0.001)
