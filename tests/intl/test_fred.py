from __future__ import annotations

from conftest import COLETADO_EM

from canavis.sources.registry import build_source


def test_normaliza_trata_ponto_como_nulo(cliente_falso, fixture_bytes):
    cliente = cliente_falso(lambda url: fixture_bytes("fred.csv"))
    fonte = build_source("fred", cliente)
    bruto = fonte.baixar()
    quadro = fonte.normalizar(bruto, COLETADO_EM)
    assert len(quadro) == 4
    assert set(quadro["serie_id"]) == {"acucar_isa_fred"}
    assert set(quadro["unidade"]) == {"USc/lb"}
    assert quadro["licenca"].str.contains("FRED").all()
    assert bruto.versao_fonte == "2026-09-01"
    ultima = quadro.iloc[-1]
    assert ultima["data"].strftime("%Y-%m-%d") == "2026-09-01"
    assert ultima["defasagem_dias"] == 87


def test_envia_user_agent_configurado(cliente_falso, fixture_bytes):
    cliente = cliente_falso(lambda url: fixture_bytes("fred.csv"))
    build_source("fred", cliente).baixar()
    assert cliente.headers[0] == {"User-Agent": "python-requests/2.34"}
