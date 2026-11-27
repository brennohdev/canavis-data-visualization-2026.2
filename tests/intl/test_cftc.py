from __future__ import annotations

from conftest import COLETADO_EM

from canavis.sources.registry import build_source


def _resposta(fixture_bytes):
    def responder(url: str) -> bytes:
        if url.endswith(".zip"):
            return fixture_bytes("cftc_historico.zip")
        return fixture_bytes("cftc_semana.txt")

    return responder


def test_filtra_acucar_une_semana_corrente_e_remove_duplicatas(cliente_falso, fixture_bytes):
    cliente = cliente_falso(_resposta(fixture_bytes))
    fonte = build_source("cftc", cliente)
    bruto = fonte.baixar()
    assert bruto.versao_fonte == "2026-11-17"
    quadro = fonte.normalizar(bruto, COLETADO_EM)
    assert set(quadro["serie_id"]) == {
        "cot_acucar_managed_money_long",
        "cot_acucar_managed_money_short",
        "cot_acucar_produtores_long",
        "cot_acucar_produtores_short",
        "cot_acucar_open_interest",
    }
    assert set(quadro["unidade"]) == {"contratos"}
    assert quadro["licenca"].str.contains("Domínio público").all()
    aberto = quadro[quadro["serie_id"] == "cot_acucar_open_interest"]
    assert len(aberto) == 4
    ultimo = aberto.iloc[-1]
    assert ultimo["data"].strftime("%Y-%m-%d") == "2026-11-17"
    assert ultimo["valor"] == 1144499
    assert ultimo["defasagem_dias"] == 10


def test_baixa_um_arquivo_por_ano_desde_a_data_configurada(cliente_falso, fixture_bytes):
    cliente = cliente_falso(_resposta(fixture_bytes))
    build_source("cftc", cliente).baixar()
    historicos = [u for u in cliente.urls if u.endswith(".zip")]
    assert historicos[0].endswith("fut_disagg_txt_2015.zip")
    assert cliente.urls[-1].endswith("f_disagg.txt")
