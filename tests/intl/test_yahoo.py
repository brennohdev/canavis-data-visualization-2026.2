from __future__ import annotations

from conftest import COLETADO_EM

from canavis.sources.registry import build_source


def test_normaliza_fechamento_e_descarta_nulo(cliente_falso, fixture_bytes):
    cliente = cliente_falso(lambda url: fixture_bytes("yahoo.json"))
    fonte = build_source("yahoo", cliente)
    quadro = fonte.normalizar(fonte.baixar(), COLETADO_EM)
    assert len(quadro) == 4
    assert set(quadro["serie_id"]) == {"acucar_ny11_fechamento"}
    assert set(quadro["unidade"]) == {"USc/lb"}
    assert quadro["licenca"].str.contains("não oficial").all()
    assert quadro["data"].is_monotonic_increasing
    assert quadro["valor"].iloc[-1] == 18.34000015258789


def test_fonte_marcada_como_nao_oficial_na_configuracao(cliente_falso, fixture_bytes):
    cliente = cliente_falso(lambda url: fixture_bytes("yahoo.json"))
    fonte = build_source("yahoo", cliente)
    assert fonte._config["unofficial"] is True
    assert fonte.baixar().versao_fonte is not None
