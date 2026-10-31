import pandas as pd
import pytest

from canavis.pipeline.industrial import ano_inicio_safra, construir_industria, construir_vendas
from canavis.pipeline.transform import _transform_conab


def _conab():
    return pd.DataFrame({
        "ano_agricola": ["2023/24  "], "uf": ["PB"], "dsc_situacao_levantamento": ["PREVISAO "],
        "dsc_safra_previsao": ["UNICA"], "produto": ["CANA"], "id_produto": [4238],
        "area_plantada_mil_ha": ["10,5"], "producao_mil_t": [1000.5],
        "producao_acucar_mil_t": [100.5], "producao_etanol_anidro_mil_l": [150.5],
        "producao_etanol_hidratado_mil_l": [50.5], "producao_etanol_total_mil_l": [201.0],
        "produtcao_atr_kg_t": [137.2],
    })


def test_conab_preserva_decimais_numericos_e_alinha_inicio_safra():
    silver = _transform_conab(_conab())
    fato = construir_industria(silver).iloc[0]
    assert fato["cana_mil_t"] == 1000.5
    assert fato["area_plantada_mil_ha"] == 10.5
    assert fato["atr_kg_t"] == 137.2
    assert fato["mix_etanol_acucar_l_t"] == pytest.approx(201 / 100.5)
    assert fato["intensidade_acucar_t_t"] == pytest.approx(100.5 / 1000.5)
    assert fato["ano_alinhamento"] == 2023
    assert fato["safra"] == "2023/24"
    assert fato["situacao_levantamento"] == "PREVISAO"


def test_alinhamento_mudanca_de_seculo_e_safra_invalida():
    assert ano_inicio_safra(pd.Series(["1999/00", "2023/2024"])).tolist() == [1999, 2023]
    with pytest.raises(ValueError):
        ano_inicio_safra(pd.Series(["2023/25"]))


def test_mix_sem_acucar_ou_dado_suprimido_nao_vira_zero():
    silver = _transform_conab(_conab())
    silver.loc[0, "producao_acucar_mil_t"] = 0
    assert pd.isna(construir_industria(silver).loc[0, "mix_etanol_acucar_l_t"])
    silver.loc[0, "producao_acucar_mil_t"] = float("nan")
    assert pd.isna(construir_industria(silver).loc[0, "mix_etanol_acucar_l_t"])


def test_nao_soma_dois_levantamentos_da_mesma_safra():
    silver = _transform_conab(_conab())
    with pytest.raises(ValueError, match="levantamento"):
        construir_industria(pd.concat([silver, silver]))


def _vendas():
    return pd.DataFrame({"ano": [2006, 2007], "uf": ["PB", "PB"],
                         "código_ibge": [2500106, 2500106], "município": ["AGUA BRANCA", "OUTRO"],
                         "vendas": [100, 200]})


def _territorios():
    return pd.DataFrame({"nivel_territorial": ["municipio"], "cod_local": ["2500106"],
                         "nome_territorio": ["Água Branca - PB"]})


def test_vendas_deduplica_repeticao_exata_e_nao_junta_codigo_com_nome_divergente():
    vendas = _vendas()
    tabelas = construir_vendas(pd.concat([vendas, vendas.iloc[[0]]]), _territorios())
    detalhe = tabelas["fato_vendas_etanol_municipio"]
    assert len(detalhe) == 2
    assert detalhe.iloc[0]["territorio_id"] == "municipio:2500106"
    assert pd.isna(detalhe.iloc[1]["territorio_id"])
    assert detalhe.iloc[0]["escopo_vendas"] == "vendas_e_consumo_proprio"
    assert detalhe.iloc[1]["escopo_vendas"] == "vendas"
    assert tabelas["fato_vendas_etanol_uf"]["vendas_etanol_hidratado_l"].sum() == 300


def test_vendas_conflitantes_nao_sao_somadas_silenciosamente():
    vendas = _vendas()
    conflito = vendas.iloc[[0]].assign(vendas=999)
    with pytest.raises(ValueError, match="conflitantes"):
        construir_vendas(pd.concat([vendas, conflito]), _territorios())
