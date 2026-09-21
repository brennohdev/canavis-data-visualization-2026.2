import numpy as np
import pandas as pd
import pytest

from canavis.domain import features


def test_tendencia_anual_crescente():
    periodos = pd.Series([2019, 2020, 2021, 2022, 2023])
    prod = pd.Series([50.0, 52.0, 54.0, 56.0, 58.0])
    assert features.tendencia_anual(periodos, prod) == pytest.approx(2.0)


def test_tendencia_serie_curta_retorna_nan():
    periodos = pd.Series([2022, 2023])
    prod = pd.Series([50.0, 52.0])
    assert np.isnan(features.tendencia_anual(periodos, prod))


def test_resiliencia_entre_zero_e_um():
    prod = pd.Series([40.0, 55.0, 60.0, 58.0, 62.0, 30.0, 59.0])
    resultado = features.resiliencia_climatica(prod)
    assert 0.0 < resultado <= 1.0


def test_elasticidade_area_produtividade_positiva():
    area = pd.Series([100.0, 110.0, 120.0, 130.0])
    prod = pd.Series([50.0, 52.0, 54.0, 56.0])
    assert features.elasticidade_area_produtividade(area, prod) == pytest.approx(1.0, abs=0.01)


def test_intensidade_industrial():
    acucar = pd.Series([100.0, 0.0])
    cana = pd.Series([1000.0, 500.0])
    resultado = features.intensidade_industrial(acucar, cana)
    assert resultado.iloc[0] == pytest.approx(0.1)
    assert resultado.iloc[1] == pytest.approx(0.0)
