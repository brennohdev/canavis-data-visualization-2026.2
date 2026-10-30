from __future__ import annotations

import numpy as np
import pandas as pd


def decompor_serie_anual(periodos: pd.Series, valores: pd.Series) -> pd.DataFrame:
    """Média móvel centrada de três anos; sem interpolar lacunas ou bordas."""
    dados = pd.DataFrame({"ano": periodos, "valor": valores.astype("float64")}).sort_values("ano")
    if dados["ano"].isna().any() or dados["ano"].duplicated().any():
        raise ValueError("Anos devem ser únicos e não ausentes")
    consecutivo = dados["ano"].diff().eq(1) & dados["ano"].diff(-1).eq(-1)
    tendencia = dados["valor"].rolling(3, center=True, min_periods=3).mean().where(consecutivo)
    return pd.DataFrame({"tendencia_t_ha": tendencia,
                         "oscilacao_t_ha": dados["valor"] - tendencia}).reindex(periodos.index)


def teste_chow(periodos: pd.Series, valores: pd.Series, ultimo_ano_pre: int = 2012) -> dict:
    """Chow de intercepto e inclinação, F(2,n-4), sob erros iid homocedásticos.

    Exige série anual completa, >= 5 pontos por segmento. O p-valor é nominal,
    não corrige seleção posterior do ponto nem múltiplas comparações.
    """
    dados = pd.DataFrame({"ano": periodos, "valor": valores}).sort_values("ano")
    indisponivel = {"f_chow": float("nan"), "p_chow": float("nan"),
                    "status_chow": "serie_incompleta_ou_curta"}
    if dados.isna().any().any() or dados["ano"].duplicated().any():
        return indisponivel
    x = dados["ano"].to_numpy(dtype=float)
    y = dados["valor"].to_numpy(dtype=float)
    if not np.isfinite(y).all() or not np.isfinite(x).all() or not np.all(np.diff(x) == 1):
        return indisponivel
    pre = x <= ultimo_ano_pre
    if min(pre.sum(), (~pre).sum()) < 5:
        return indisponivel
    x = x - x.mean()

    def rss(a, b):
        matriz = np.column_stack([np.ones(len(a)), a])
        residuo = b - matriz @ np.linalg.lstsq(matriz, b, rcond=None)[0]
        return float(residuo @ residuo)

    restrito = rss(x, y)
    livre = rss(x[pre], y[pre]) + rss(x[~pre], y[~pre])
    tolerancia = np.finfo(float).eps * max(1.0, float(y @ y)) * 100
    if livre <= tolerancia:
        return {"f_chow": float("nan"), "p_chow": float("nan"),
                "status_chow": "variancia_residual_degenerada"}
    gl = len(y) - 4
    f = max(0.0, (restrito - livre) / 2 / (livre / gl))
    # Sobrevivência exata da distribuição F quando o numerador tem 2 graus.
    p = (gl / (gl + 2 * f)) ** (gl / 2)
    return {"f_chow": float(f), "p_chow": float(p), "status_chow": "exploratorio"}


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
