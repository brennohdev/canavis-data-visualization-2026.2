import importlib.util
from pathlib import Path

import pandas as pd
import pytest

from canavis.domain import cobertura

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def _carregar_script():
    spec = importlib.util.spec_from_file_location(
        "gerar_matriz_cobertura", ROOT / "scripts" / "gerar_matriz_cobertura.py"
    )
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture(scope="module")
def matriz_versionada():
    return pd.read_parquet(PROCESSED / "matriz_cobertura.parquet")


def test_pb_2023_distingue_produtor_zero_registrado_e_suprimido(matriz_versionada):
    resumo = cobertura.resumo_pb(matriz_versionada, 2023)
    assert resumo == {"presente": 82, "sem_producao": 140, "suprimido": 1, "sem_registro": 0}


def test_ultimo_ano_por_fonte(matriz_versionada):
    assert cobertura.ultimo_ano_por_fonte(matriz_versionada) == {
        "anp_vendas_etanol": 2024,
        "conab_cana": 2026,
        "ibge_pam_1612": 2023,
    }


def test_matriz_versionada_esta_em_dia():
    gerada = _carregar_script().carregar_matriz()
    versionada = pd.read_parquet(PROCESSED / "matriz_cobertura.parquet")
    pd.testing.assert_frame_equal(gerada, versionada, check_dtype=False)


def test_markdown_versionado_esta_em_dia():
    script = _carregar_script()
    esperado = script.renderizar_markdown(script.carregar_matriz())
    assert script.SAIDA_MD.read_text(encoding="utf-8") == esperado


def test_sem_registro_nunca_aparece_como_sem_producao(matriz_versionada):
    sem_registro = matriz_versionada[matriz_versionada["situacao"] == "sem_registro"]
    assert not sem_registro.empty
    assert set(sem_registro["fonte_id"]) == {"conab_cana"}
    assert set(matriz_versionada["situacao"]) <= set(cobertura.SITUACOES)


def test_classificar_situacao():
    assert cobertura.classificar_situacao(10.0, "presente") == "presente"
    assert cobertura.classificar_situacao(0.0, "sem_producao") == "sem_producao"
    assert cobertura.classificar_situacao(float("nan"), "suprimido") == "suprimido"


def test_nan_com_presente_levanta_erro():
    with pytest.raises(ValueError):
        cobertura.classificar_situacao(float("nan"), "presente")


def test_situacao_desconhecida_levanta_erro():
    with pytest.raises(ValueError):
        cobertura.classificar_situacao(1.0, "outra")


def test_matriz_sintetica_marca_sem_registro_e_nao_zero():
    dim = pd.DataFrame(
        {
            "territorio_id": ["uf:11", "uf:12"],
            "nivel_territorial": ["uf", "uf"],
        }
    )
    pam = pd.DataFrame(
        {
            "territorio_id": ["uf:11", "uf:11", "uf:12"],
            "ano_referencia": [2022, 2023, 2023],
            "quantidade_produzida_t": [5.0, 0.0, float("nan")],
            "situacao_quantidade": ["presente", "sem_producao", "suprimido"],
        }
    )
    industria = pd.DataFrame({"territorio_id": ["uf:11"], "ano_alinhamento": [2023]})
    vendas = pd.DataFrame({"territorio_id": ["uf:12"], "ano_referencia": [2024]})
    matriz = cobertura.construir_matriz_cobertura(pam, industria, vendas, dim)
    pam_m = matriz[matriz["fonte_id"] == cobertura.FONTE_PAM].set_index(
        ["territorio_id", "ano_referencia"]
    )["situacao"]
    assert pam_m[("uf:11", 2022)] == "presente"
    assert pam_m[("uf:11", 2023)] == "sem_producao"
    assert pam_m[("uf:12", 2023)] == "suprimido"
    assert pam_m[("uf:12", 2022)] == "sem_registro"
    conab = matriz[matriz["fonte_id"] == cobertura.FONTE_CONAB].set_index("territorio_id")
    assert conab.loc["uf:12", "situacao"] == "sem_registro"
    assert conab.loc["uf:11", "situacao"] == "presente"
