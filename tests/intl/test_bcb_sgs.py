from __future__ import annotations

from conftest import COLETADO_EM

from canavis.sources.registry import build_source


def _fonte(cliente_falso, fixture_bytes):
    cliente = cliente_falso(lambda url: fixture_bytes("bcb_sgs.json"))
    return build_source("bcb_sgs", cliente), cliente


def test_normaliza_descarta_linha_sem_valor_e_preenche_metadados(cliente_falso, fixture_bytes):
    fonte, _ = _fonte(cliente_falso, fixture_bytes)
    quadro = fonte.normalizar(fonte.baixar(), COLETADO_EM)
    assert len(quadro) == 4
    assert set(quadro["serie_id"]) == {"cambio_usd_brl"}
    assert set(quadro["unidade"]) == {"BRL/USD"}
    assert set(quadro["fonte_id"]) == {"bcb_sgs"}
    assert quadro["licenca"].str.contains("Banco Central").all()
    primeira = quadro.iloc[0]
    assert primeira["data"].strftime("%Y-%m-%d") == "2024-01-02"
    assert primeira["valor"] == 4.8916
    assert primeira["defasagem_dias"] == 1060


def test_baixa_em_janelas_de_ate_nove_anos(cliente_falso, fixture_bytes):
    fonte, cliente = _fonte(cliente_falso, fixture_bytes)
    bruto = fonte.baixar()
    assert len(cliente.urls) >= 3
    assert "dataInicial=01/01/2000" in cliente.urls[0]
    assert "dataFinal=31/12/2008" in cliente.urls[0]
    assert bruto.versao_fonte == "2024-01-08"
    assert bruto.extensao == "json"
