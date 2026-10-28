import pandas as pd
import pytest

from canavis.domain import territorio
from canavis.pipeline import transform


# --- Classificação de ausência -------------------------------------------------

def test_classificar_valor_numerico_presente():
    assert transform.classificar_ausencia("123") == "presente"
    assert transform.classificar_ausencia("1.234,5") == "presente"
    assert transform.classificar_ausencia("0") == "presente"


def test_classificar_token_sem_producao():
    assert transform.classificar_ausencia("-") == "sem_producao"


def test_classificar_tokens_suprimido():
    assert transform.classificar_ausencia("...") == "suprimido"
    assert transform.classificar_ausencia("X") == "suprimido"


def test_classificar_token_outra_condicao():
    assert transform.classificar_ausencia("..") == "outra_condicao"


def test_classificar_ausencia_sem_token_semantico():
    assert transform.classificar_ausencia("   ") == "outra_condicao"
    assert transform.classificar_ausencia("") == "outra_condicao"
    assert transform.classificar_ausencia(None) == "outra_condicao"
    assert transform.classificar_ausencia(pd.NA) == "outra_condicao"
    assert transform.classificar_ausencia(float("nan")) == "outra_condicao"


# --- _transform_ibge ------------------------------------------------------------

def _frame_sintetico() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "extracao": ["serie_municipios_pb"] * 4,
            "cod_local": ["1", "2", "3", "4"],
            "local": ["A", "B", "C", "D"],
            "variavel": ["Quantidade produzida"] * 4,
            "periodo": ["2023", "2023", "2023", "2023"],
            "valor": ["1.234", "-", "...", "X"],
        }
    )


def test_transform_ibge_cria_situacao_e_preserva_linhas():
    resultado = transform._transform_ibge(_frame_sintetico())
    assert "situacao_valor" in resultado.columns
    # Nenhuma linha descartada.
    assert len(resultado) == 4


def test_transform_ibge_sem_producao_vira_zero_real():
    resultado = transform._transform_ibge(_frame_sintetico())
    linha = resultado.loc[resultado["local"] == "B"].iloc[0]
    assert linha["situacao_valor"] == "sem_producao"
    assert linha["valor"] == 0.0


def test_transform_ibge_suprimido_fica_na():
    resultado = transform._transform_ibge(_frame_sintetico())
    suprimidos = resultado.loc[resultado["local"].isin(["C", "D"])]
    assert (suprimidos["situacao_valor"] == "suprimido").all()
    assert suprimidos["valor"].isna().all()


def test_transform_ibge_presente_mantem_numero():
    resultado = transform._transform_ibge(_frame_sintetico())
    linha = resultado.loc[resultado["local"] == "A"].iloc[0]
    assert linha["situacao_valor"] == "presente"
    assert linha["valor"] == pytest.approx(1234.0)


# --- Mapeamento territorial -----------------------------------------------------

def test_cinco_microrregioes_canavieiras():
    assert len(territorio.MICRORREGIOES_CANAVIEIRAS) == 5


def test_regiao_de_resolve_as_cinco_microrregioes():
    esperado = {
        "Litoral Norte - PB": ("Mamanguape", "João Pessoa"),
        "Litoral Sul - PB": ("João Pessoa", "João Pessoa"),
        "Sapé - PB": ("João Pessoa", "João Pessoa"),
        "João Pessoa - PB": ("João Pessoa", "João Pessoa"),
        "Brejo Paraibano - PB": ("Guarabira", "João Pessoa"),
    }
    for micro, (imediata, intermediaria) in esperado.items():
        regiao = territorio.regiao_de(micro)
        assert regiao["imediata"] == imediata
        assert regiao["intermediaria"] == intermediaria


def test_regiao_de_microrregiao_desconhecida_levanta():
    with pytest.raises(KeyError):
        territorio.regiao_de("Cariri Ocidental - PB")
