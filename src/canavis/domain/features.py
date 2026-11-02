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


def varredura_supf(periodos: pd.Series, valores: pd.Series, aparagem: float = 0.15) -> dict:
    """Varredura supF: maior F de Chow sobre os cortes internos de uma janela aparada.

    Testa quebra de regime sem fixar o ano a priori. Em vez de um único corte
    (como teste_chow), avalia cada ano interno candidato dentro de uma janela que
    descarta ~15% dos pontos iniciais e finais (``aparagem``), calcula o F de Chow
    de intercepto e inclinação em cada corte e devolve o máximo (supF) e o ano que
    o maximiza. O F reutiliza a mesma estatística de teste_chow (F(2,n-4) sob erros
    iid homocedásticos); o resultado é exploratório e não corrige a seleção posterior
    do ponto nem comparações múltiplas (ver fdr_benjamini_hochberg).

    Guardas idênticas as de teste_chow: exige série anual completa, anos únicos e
    consecutivos, e pelo menos 5 pontos de cada lado de todo corte avaliado. Séries
    incompletas, curtas ou com variância residual degenerada devolvem sup_f NaN e
    status textual indisponível.

    Devolve dict com ``sup_f`` (F máximo), ``ano_sup`` (ano que maximiza), ``n_cortes``
    (número de cortes avaliados) e ``status`` ("endogeno" |
    "serie_incompleta_ou_curta" | "variancia_residual_degenerada").
    """
    dados = pd.DataFrame({"ano": periodos, "valor": valores}).sort_values("ano")
    indisponivel = {"sup_f": float("nan"), "ano_sup": float("nan"),
                    "n_cortes": 0, "status": "serie_incompleta_ou_curta"}
    if dados.isna().any().any() or dados["ano"].duplicated().any():
        return indisponivel
    x_anos = dados["ano"].to_numpy(dtype=float)
    y = dados["valor"].to_numpy(dtype=float)
    if not np.isfinite(y).all() or not np.isfinite(x_anos).all() or not np.all(np.diff(x_anos) == 1):
        return indisponivel

    n = len(y)
    minimo_segmento = 5
    inicio = max(minimo_segmento, int(np.ceil(aparagem * n)))
    fim = min(n - minimo_segmento, n - int(np.ceil(aparagem * n)))
    # Cada corte usa os anos <= ano_corte como segmento anterior; precisamos de
    # >= minimo_segmento pontos de cada lado, logo o corte vai de inicio-1 a fim-1.
    cortes = list(range(inicio - 1, fim))
    if not cortes:
        return indisponivel

    x = x_anos - x_anos.mean()

    def rss(a, b):
        matriz = np.column_stack([np.ones(len(a)), a])
        residuo = b - matriz @ np.linalg.lstsq(matriz, b, rcond=None)[0]
        return float(residuo @ residuo)

    restrito = rss(x, y)
    gl = n - 4
    tolerancia = np.finfo(float).eps * max(1.0, float(y @ y)) * 100
    sup_f = -np.inf
    ano_sup = float("nan")
    degenerado = False
    for corte in cortes:
        pre = np.arange(n) <= corte
        livre = rss(x[pre], y[pre]) + rss(x[~pre], y[~pre])
        if livre <= tolerancia:
            degenerado = True
            continue
        f = max(0.0, (restrito - livre) / 2 / (livre / gl))
        if f > sup_f:
            sup_f = f
            ano_sup = float(x_anos[corte])
    if not np.isfinite(sup_f):
        status = "variancia_residual_degenerada" if degenerado else "serie_incompleta_ou_curta"
        return {"sup_f": float("nan"), "ano_sup": float("nan"),
                "n_cortes": len(cortes), "status": status}
    return {"sup_f": float(sup_f), "ano_sup": ano_sup,
            "n_cortes": len(cortes), "status": "endogeno"}


def fdr_benjamini_hochberg(pvalores: pd.Series, alfa: float = 0.05) -> dict:
    """Controle de FDR de Benjamini-Hochberg sobre um conjunto de p-valores.

    Ao testar quebra em vários territórios, o p-valor nominal de cada teste
    (teste_chow / varredura_supf) ignora que estamos fazendo muitas comparações.
    O procedimento BH controla a taxa esperada de falsas descobertas: ordena os m
    p-valores, encontra o maior k tal que ``p(k) <= (k/m)*alfa`` e rejeita todas as
    hipóteses até esse k. Os p-ajustados BH são o mínimo cumulativo reverso de
    ``m/posto * p`` sobre os p ordenados, limitado a 1.

    Entradas NaN são tratadas como não testáveis: não entram na contagem m, nunca
    são rejeitadas e recebem p-ajustado NaN. Só numpy/pandas.

    Devolve dict com ``rejeitado`` (np.ndarray[bool] na ordem original),
    ``p_ajustado`` (np.ndarray na ordem original, NaN onde a entrada era NaN),
    ``n_rejeitado`` (int) e ``n_total`` (int, número de p-valores testáveis).
    """
    p = np.asarray(pd.Series(pvalores).to_numpy(), dtype=float)
    rejeitado = np.zeros(len(p), dtype=bool)
    p_ajustado = np.full(len(p), np.nan, dtype=float)

    validos = np.where(np.isfinite(p))[0]
    m = len(validos)
    if m == 0:
        return {"rejeitado": rejeitado, "p_ajustado": p_ajustado,
                "n_rejeitado": 0, "n_total": 0}

    p_validos = p[validos]
    ordem = np.argsort(p_validos, kind="mergesort")
    p_ordenado = p_validos[ordem]
    postos = np.arange(1, m + 1)

    # Limiar BH: maior posto k com p(k) <= (k/m)*alfa rejeita todos até k.
    abaixo = p_ordenado <= (postos / m) * alfa
    if abaixo.any():
        k = np.max(np.where(abaixo)[0])
        rejeita_ordenado = np.arange(m) <= k
    else:
        rejeita_ordenado = np.zeros(m, dtype=bool)

    # p-ajustados BH: mínimo cumulativo reverso de (m/posto)*p, limitado a 1.
    ajustado_ordenado = np.minimum.accumulate((m / postos * p_ordenado)[::-1])[::-1]
    ajustado_ordenado = np.minimum(ajustado_ordenado, 1.0)

    rejeita_validos = np.zeros(m, dtype=bool)
    ajustado_validos = np.empty(m, dtype=float)
    rejeita_validos[ordem] = rejeita_ordenado
    ajustado_validos[ordem] = ajustado_ordenado

    rejeitado[validos] = rejeita_validos
    p_ajustado[validos] = ajustado_validos
    return {"rejeitado": rejeitado, "p_ajustado": p_ajustado,
            "n_rejeitado": int(rejeitado.sum()), "n_total": m}


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
