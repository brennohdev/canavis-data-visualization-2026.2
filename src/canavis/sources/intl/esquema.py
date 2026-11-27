from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd

COLUNAS = [
    "serie_id",
    "data",
    "valor",
    "unidade",
    "fonte_id",
    "coletado_em",
    "defasagem_dias",
    "licenca",
]

FORMATO_COLETA = "%Y-%m-%dT%H:%M:%SZ"


def calcular_defasagem(datas: pd.Series, coletado_em: datetime) -> pd.Series:
    referencia = pd.Timestamp(coletado_em).tz_localize(None).normalize()
    return (referencia - datas.dt.normalize()).dt.days.astype("int64")


def validar(frame: pd.DataFrame) -> pd.DataFrame:
    if list(frame.columns) != COLUNAS:
        raise ValueError(f"Colunas fora do esquema: {list(frame.columns)}")
    if frame.empty:
        raise ValueError("Quadro sem linhas")
    if frame[["serie_id", "data", "valor", "unidade", "fonte_id", "coletado_em"]].isna().any().any():
        raise ValueError("Valores nulos em colunas obrigatórias")
    if not np.isfinite(frame["valor"].astype("float64")).all():
        raise ValueError("Valores não finitos")
    if frame.duplicated(["serie_id", "data"]).any():
        raise ValueError("Pares (serie_id, data) duplicados")
    return frame
