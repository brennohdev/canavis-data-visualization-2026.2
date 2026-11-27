from pathlib import Path

import pandas as pd
import pytest

from canavis.domain import indicators

PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"
PB = "uf:25"


@pytest.fixture(scope="module")
def uf_2023():
    uf = pd.read_parquet(PROCESSED / "fato_producao_uf.parquet")
    dim = pd.read_parquet(PROCESSED / "dim_territorio.parquet")[["territorio_id", "tier"]]
    return uf[uf["ano_referencia"] == 2023].merge(dim, on="territorio_id", how="left")


@pytest.fixture(scope="module")
def pb(uf_2023):
    return uf_2023[uf_2023["territorio_id"] == PB].iloc[0]


def test_produtividade_pb_2023(pb):
    resultado = indicators.produtividade_ponderada([pb["quantidade_produzida_t"]], [pb["area_colhida_ha"]])
    assert resultado == pytest.approx(64.69, abs=0.01)


def test_desvio_vs_selecao_pb_2023(uf_2023, pb):
    resultado = indicators.desvio_vs_selecao(
        pb["produtividade_t_ha"], uf_2023["quantidade_produzida_t"], uf_2023["area_colhida_ha"]
    )
    assert resultado == pytest.approx(-16.96, abs=0.01)


def test_desvio_vs_grupo_pb_2023(uf_2023, pb):
    grupo = uf_2023[uf_2023["tier"] == pb["tier"]]
    assert len(grupo) == 14
    resultado = indicators.desvio_vs_grupo(
        pb["produtividade_t_ha"], pb["tier"],
        grupo["quantidade_produzida_t"], grupo["area_colhida_ha"],
    )
    assert resultado == pytest.approx(3.41, abs=0.01)


def test_participacao_pb_2023(uf_2023, pb):
    resultado = indicators.participacao(
        pb["quantidade_produzida_t"], uf_2023["quantidade_produzida_t"].sum()
    )
    assert resultado == pytest.approx(0.90, abs=0.01)


def test_share_atr_acucar_pb_safra_2023_24():
    industria = pd.read_parquet(PROCESSED / "fato_industria.parquet")
    linha = industria[(industria["territorio_id"] == PB) & (industria["ano_alinhamento"] == 2023)]
    assert linha["safra"].iloc[0] == "2023/24"
    r = linha.iloc[0]
    share = indicators.share_atr_acucar(
        r["producao_acucar_mil_t"],
        r["producao_etanol_anidro_mil_l"],
        r["producao_etanol_hidratado_mil_l"],
    )
    assert share == pytest.approx(27.54, abs=0.01)


def test_ponderacao_e_razao_de_agregados_e_nao_media_simples(uf_2023):
    ponderada = indicators.produtividade_ponderada(
        uf_2023["quantidade_produzida_t"], uf_2023["area_colhida_ha"]
    )
    assert ponderada == pytest.approx(77.90, abs=0.01)
    assert float(uf_2023["produtividade_t_ha"].astype(float).mean()) == pytest.approx(61.14, abs=0.01)


def test_participacao_dos_municipios_na_area_da_pb_soma_100():
    municipio = pd.read_parquet(PROCESSED / "fato_producao_municipio.parquet")
    uf = pd.read_parquet(PROCESSED / "fato_producao_uf.parquet")
    area_uf = uf[(uf["territorio_id"] == PB) & (uf["ano_referencia"] == 2023)]["area_colhida_ha"].iloc[0]
    presentes = municipio[
        (municipio["ano_referencia"] == 2023) & (municipio["situacao_area"] == "presente")
    ]
    assert len(presentes) == 82
    partes = [indicators.participacao(a, area_uf) for a in presentes["area_colhida_ha"]]
    assert sum(partes) == pytest.approx(100.0, abs=1e-6)
