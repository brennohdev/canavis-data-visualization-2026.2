from __future__ import annotations

import numpy as np
import pandas as pd


def tendencia_anual(periodos: pd.Series, produtividade: pd.Series) -> float:
    """Ganho ou perda média de produtividade por ano (inclinação da reta).

    Positivo indica região que vem melhorando de forma consistente. Deve ser
    calculada sobre janela recente, pois a série longa contém inversão de regime.
    """
    mascara = periodos.notna() & produtividade.notna()
    if mascara.sum() < 3:
        return float("nan")
    x = periodos[mascara].to_numpy(dtype=float)
    y = produtividade[mascara].to_numpy(dtype=float)
    return float(np.polyfit(x, y, 1)[0])


def resiliencia_climatica(produtividade: pd.Series, pior_quantil: float = 0.2) -> float:
    """Quanto a produtividade nos piores anos se sustenta frente à mediana.

    Razão entre a média dos anos ruins (quantil inferior) e a mediana da série.
    Próximo de 1 indica região que sofre pouco na seca; bem abaixo de 1 indica
    região que despenca em anos ruins.
    """
    limpo = produtividade.dropna()
    if len(limpo) < 5:
        return float("nan")
    corte = limpo.quantile(pior_quantil)
    piores = limpo[limpo <= corte]
    mediana = limpo.median()
    if mediana == 0 or piores.empty:
        return float("nan")
    return float(piores.mean() / mediana)


def elasticidade_area_produtividade(
    area_colhida: pd.Series, produtividade: pd.Series
) -> float:
    """Relação entre expansão de área e produtividade, via correlação.

    Negativa sugere que crescer área veio junto de plantar em terra pior
    (retorno marginal caindo); positiva sugere expansão sem perda de qualidade.
    """
    pareado = pd.DataFrame({"area": area_colhida, "prod": produtividade}).dropna()
    if len(pareado) < 3 or pareado["area"].nunique() < 2:
        return float("nan")
    return float(pareado["area"].corr(pareado["prod"]))


def intensidade_industrial(acucar_mil_t: pd.Series, cana_mil_t: pd.Series) -> pd.Series:
    """Açúcar extraído por tonelada de cana processada (rendimento industrial).

    Cruza a produção industrial (CONAB) com a produção de cana. Maior indica
    matéria-prima ou processo que rende mais produto por tonelada.
    """
    cana = cana_mil_t.replace(0, pd.NA)
    return (acucar_mil_t / cana).astype("Float64")
