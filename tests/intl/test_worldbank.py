from __future__ import annotations

import pytest
from conftest import COLETADO_EM

from canavis.sources.registry import build_source


def _resposta(fixture_bytes, pagina="worldbank_pagina.html"):
    def responder(url: str) -> bytes:
        if url.endswith(".xlsx"):
            return fixture_bytes("worldbank_pink_sheet.xlsx")
        return fixture_bytes(pagina)

    return responder


def test_descobre_link_e_normaliza_tres_series(cliente_falso, fixture_bytes):
    cliente = cliente_falso(_resposta(fixture_bytes))
    fonte = build_source("worldbank", cliente)
    bruto = fonte.baixar()
    assert bruto.url.endswith("CMO-Historical-Data-Monthly.xlsx")
    assert bruto.versao_fonte == "November 03, 2026"
    quadro = fonte.normalizar(bruto, COLETADO_EM)
    assert set(quadro["serie_id"]) == {"acucar_mundo_wb", "acucar_ue_wb", "acucar_eua_wb"}
    assert set(quadro["unidade"]) == {"USD/kg"}
    assert quadro["licenca"].str.contains("CC BY").all()
    assert len(quadro[quadro["serie_id"] == "acucar_mundo_wb"]) == 3
    assert len(quadro[quadro["serie_id"] == "acucar_ue_wb"]) == 2
    mundo = quadro[quadro["serie_id"] == "acucar_mundo_wb"].iloc[-1]
    assert mundo["data"].strftime("%Y-%m-%d") == "2026-10-01"
    assert mundo["valor"] == 0.43
    assert mundo["defasagem_dias"] == 57


def test_falha_quando_pagina_nao_tem_link(cliente_falso):
    cliente = cliente_falso(lambda url: b"<html></html>")
    with pytest.raises(ValueError):
        build_source("worldbank", cliente).baixar()
