import importlib

import pytest
import yaml

from canavis import config
from canavis.domain import indicators


@pytest.fixture(scope="module")
def catalogo():
    return config.load_indicadores()


def test_todo_indicador_tem_definicao_unidade_sentido_e_limitacao(catalogo):
    assert catalogo["indicadores"]
    for item in catalogo["indicadores"]:
        assert item["definicao"].strip()
        assert item["unidade"].strip()
        assert item["sentido"] in {"maior_melhor", "menor_melhor", "neutro"}
        assert len(item["limitacoes"]) >= 1


def test_ids_unicos(catalogo):
    ids = [item["id"] for item in catalogo["indicadores"]]
    assert len(ids) == len(set(ids))


def test_ids_obrigatorios_presentes(catalogo):
    ids = {item["id"] for item in catalogo["indicadores"]}
    assert {
        "produtividade_ponderada", "participacao_regional", "participacao_municipio_area_pb",
        "desvio_vs_selecao", "desvio_vs_grupo", "share_atr_acucar", "nivel_suavizado",
        "oscilacao", "tendencia_inclinacao_5a", "tendencia_inclinacao_10a",
        "tendencia_inclinacao_21a", "tendencia_inclinacao_sem_ultimo_ano", "situacao_cobertura",
    } <= ids


def test_toda_funcao_resolve_no_dominio(catalogo):
    for item in catalogo["indicadores"]:
        modulo, _, nome = item["funcao"].rpartition(".")
        assert modulo.startswith("canavis.domain")
        assert callable(getattr(importlib.import_module(modulo), nome))


def test_fatores_do_yaml_coincidem_com_constantes_do_dominio(catalogo):
    parametros = catalogo["parametros"]
    assert parametros["fator_atr_acucar"]["valor"] == indicators.FATOR_ATR_ACUCAR
    assert parametros["fator_atr_etanol_anidro"]["valor"] == indicators.FATOR_ATR_ETANOL_ANIDRO
    assert (
        parametros["fator_atr_etanol_hidratado"]["valor"] == indicators.FATOR_ATR_ETANOL_HIDRATADO
    )


def test_fatores_consecana_sao_premissa(catalogo):
    for parametro in catalogo["parametros"].values():
        assert parametro["status"] == "premissa"


def test_limitacoes_obrigatorias_de_desvio_grupo_e_share_atr(catalogo):
    por_id = {item["id"]: item for item in catalogo["indicadores"]}
    assert "UF" in " ".join(por_id["desvio_vs_grupo"]["limitacoes"])
    assert por_id["desvio_vs_grupo"]["niveis"] == ["uf"]
    texto_share = " ".join(por_id["share_atr_acucar"]["limitacoes"])
    assert "premissa" in texto_share and "previsão" in texto_share


def _escrever(tmp_path, mutar):
    bruto = yaml.safe_load((config._CONFIG_DIR / "indicadores.yaml").read_text(encoding="utf-8"))
    mutar(bruto)
    destino = tmp_path / "indicadores.yaml"
    destino.write_text(yaml.safe_dump(bruto, allow_unicode=True), encoding="utf-8")
    return destino


def test_entrada_sem_limitacoes_falha(tmp_path):
    destino = _escrever(tmp_path, lambda b: b["indicadores"][0].update(limitacoes=[]))
    with pytest.raises(ValueError, match="limitações"):
        config.carregar_indicadores_de(destino)


def test_chave_obrigatoria_ausente_falha(tmp_path):
    destino = _escrever(tmp_path, lambda b: b["indicadores"][0].pop("definicao"))
    with pytest.raises(ValueError, match="definicao"):
        config.carregar_indicadores_de(destino)


def test_sentido_invalido_falha(tmp_path):
    destino = _escrever(tmp_path, lambda b: b["indicadores"][0].update(sentido="sobe"))
    with pytest.raises(ValueError, match="sentido"):
        config.carregar_indicadores_de(destino)


def test_id_duplicado_falha(tmp_path):
    destino = _escrever(
        tmp_path, lambda b: b["indicadores"][1].update(id=b["indicadores"][0]["id"])
    )
    with pytest.raises(ValueError, match="duplicado"):
        config.carregar_indicadores_de(destino)
