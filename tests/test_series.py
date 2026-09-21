import numpy as np
import pandas as pd
import pytest

from canavis.validation import series


def test_inclinacao_positiva():
    periodos = pd.Series([2020, 2021, 2022, 2023])
    valores = pd.Series([100.0, 110.0, 120.0, 130.0])
    assert series.inclinacao(periodos, valores) == pytest.approx(10.0)


def test_inclinacao_ignora_ausentes():
    periodos = pd.Series([2020, 2021, 2022])
    valores = pd.Series([100.0, np.nan, 120.0])
    assert series.inclinacao(periodos, valores) == pytest.approx(10.0)


def test_inclinacao_serie_curta_retorna_nan():
    periodos = pd.Series([2020])
    valores = pd.Series([100.0])
    assert np.isnan(series.inclinacao(periodos, valores))


def test_coeficiente_variacao():
    valores = pd.Series([100.0, 100.0, 100.0])
    assert series.coeficiente_variacao(valores) == pytest.approx(0.0)


def test_compara_janelas_detecta_inversao():
    periodos = pd.Series([2003, 2007, 2012, 2016, 2020, 2023])
    valores = pd.Series([120.0, 100.0, 80.0, 100.0, 130.0, 160.0])
    resultado = series.compara_janelas(periodos, valores, corte=2012)
    assert resultado["inclinacao_antes"] < 0
    assert resultado["inclinacao_depois"] > 0
