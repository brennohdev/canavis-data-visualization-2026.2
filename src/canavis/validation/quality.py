from __future__ import annotations

import pandas as pd


def taxa_ausentes(frame: pd.DataFrame, valor: str, grupo: str) -> pd.DataFrame:
    """Fração de valores ausentes de uma coluna, quebrada por grupo."""
    presente = frame[valor].notna()
    resumo = (
        frame.assign(_ausente=~presente)
        .groupby(grupo)["_ausente"]
        .agg(total="size", ausentes="sum")
        .reset_index()
    )
    resumo["taxa_ausentes"] = resumo["ausentes"] / resumo["total"]
    return resumo.sort_values("taxa_ausentes", ascending=False)


def cobertura_por_periodo(
    frame: pd.DataFrame, valor: str, periodo: str, unidade: str
) -> pd.DataFrame:
    """Quantas unidades territoriais têm valor observado em cada período."""
    validos = frame[frame[valor].notna()]
    return (
        validos.groupby(periodo)[unidade]
        .nunique()
        .reset_index(name="unidades_com_dado")
        .sort_values(periodo)
    )


def completude_serie(
    frame: pd.DataFrame, valor: str, periodo: str, unidade: str
) -> pd.DataFrame:
    """Proporção de períodos com dado observado, por unidade territorial."""
    total_periodos = frame[periodo].nunique()
    validos = frame[frame[valor].notna()]
    contagem = (
        validos.groupby(unidade)[periodo]
        .nunique()
        .reset_index(name="periodos_com_dado")
    )
    contagem["completude"] = contagem["periodos_com_dado"] / total_periodos
    return contagem.sort_values("completude", ascending=False)
