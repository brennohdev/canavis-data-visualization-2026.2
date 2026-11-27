from __future__ import annotations

from conftest import COLETADO_EM

from canavis.sources.registry import build_source


def test_filtra_acucar_centrifugo_paises_e_atributos(cliente_falso, fixture_bytes):
    cliente = cliente_falso(lambda url: fixture_bytes("usda_psd.zip"))
    fonte = build_source("usda_psd", cliente)
    bruto = fonte.baixar()
    assert bruto.extensao == "zip"
    quadro = fonte.normalizar(bruto, COLETADO_EM)
    assert set(quadro["serie_id"]) == {
        "psd_br_producao",
        "psd_br_estoque_final",
        "psd_cn_producao",
        "psd_cn_estoque_final",
        "psd_ue_producao",
        "psd_ue_estoque_final",
    }
    assert len(quadro) == 12
    assert set(quadro["unidade"]) == {"mil t"}
    assert quadro["licenca"].str.contains("USDA").all()
    producao = quadro[quadro["serie_id"] == "psd_br_producao"]
    assert producao["valor"].tolist() == [43700.0, 43295.0]
    assert producao["data"].dt.strftime("%Y-%m-%d").tolist() == ["2024-01-01", "2025-01-01"]
    assert producao["defasagem_dias"].tolist() == [1061, 695]
