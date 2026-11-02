import pandas as pd
import pytest

from canavis.domain import texto


def test_sem_acento_preserva_caixa_e_separadores():
    assert texto.sem_acento("João Pessoa") == "Joao Pessoa"
    assert texto.sem_acento("Água Branca - PB") == "Agua Branca - PB"
    assert texto.sem_acento("Rondônia") == "Rondonia"
    assert texto.sem_acento("Pará") == "Para"


def test_sem_acento_sem_acento_e_idempotente():
    assert texto.sem_acento("Acre") == "Acre"
    assert texto.sem_acento(texto.sem_acento("Pará")) == "Para"


def test_sem_acento_trata_ausencia_como_none():
    assert texto.sem_acento(None) is None
    assert texto.sem_acento(pd.NA) is None
    assert texto.sem_acento(float("nan")) is None
    assert texto.sem_acento("   ") is None
    assert texto.sem_acento("") is None


def test_sem_acento_series_preserva_na():
    serie = pd.Series(["João Pessoa", None, "Pará"])
    resultado = texto.sem_acento_series(serie)
    assert resultado.iloc[0] == "Joao Pessoa"
    assert pd.isna(resultado.iloc[1])
    assert resultado.iloc[2] == "Para"


def test_chave_nome_para_juncao():
    assert texto.chave_nome("Água Branca") == "AGUABRANCA"
    assert texto.chave_nome("Alta Floresta D'Oeste") == "ALTAFLORESTADOESTE"
    assert texto.chave_nome(None) is None


def test_chave_nome_casa_grafias_divergentes():
    # Mesma localidade em grafias diferentes converge para a mesma chave.
    assert texto.chave_nome("SÃO JOÃO") == texto.chave_nome("São João")
