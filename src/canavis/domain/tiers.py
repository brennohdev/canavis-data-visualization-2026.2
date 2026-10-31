from __future__ import annotations

import numpy as np
import pandas as pd

ROTULOS = {0: "grande escala industrial", 1: "media escala", 2: "pequena/marginal"}


def media_recente(
    anos: pd.Series, quantidade: pd.Series, por: pd.Series, janela: int = 5
) -> pd.Series:
    """Média da quantidade produzida por unidade nos últimos ``janela`` anos.

    Estabiliza a escala de cada unidade contra o ruído de um ano isolado. Só
    entram anos com valor conhecido; uma unidade sem nenhum valor na janela é
    omitida do resultado.
    """
    dados = pd.DataFrame({"ano": anos, "quantidade": quantidade, "unidade": por}).dropna(
        subset=["ano", "quantidade"]
    )
    if dados.empty:
        return pd.Series(dtype="float64")
    recentes = sorted(dados["ano"].unique())[-janela:]
    dados = dados[dados["ano"].isin(recentes)]
    return dados.groupby("unidade")["quantidade"].mean()


def _cortes_otimos(log_ordenado: np.ndarray, n_grupos: int) -> list[int]:
    """Fronteiras (índices) que minimizam a variância intra-grupo do log.

    Em uma dimensão, a partição que minimiza a soma dos quadrados dentro dos
    grupos coincide com os *natural breaks* de Fisher-Jenks e com a solução de
    Ward aglomerativo. Ancorada nos maiores saltos (gaps) da série ordenada, é
    reprodutível e defensável para uma escala log-normal como a da produção.
    """
    n = len(log_ordenado)
    if n_grupos < 1 or n_grupos > n:
        raise ValueError("Número de grupos fora do intervalo possível")

    prefixo = np.concatenate([[0.0], np.cumsum(log_ordenado)])
    prefixo_quad = np.concatenate([[0.0], np.cumsum(log_ordenado**2)])

    def sse(ini: int, fim: int) -> float:
        tamanho = fim - ini
        if tamanho <= 1:
            return 0.0
        soma = prefixo[fim] - prefixo[ini]
        soma_quad = prefixo_quad[fim] - prefixo_quad[ini]
        return float(soma_quad - soma**2 / tamanho)

    # Programação dinâmica: custo[k][i] = menor SSE para agrupar os primeiros i
    # pontos em k segmentos. Reconstrói as fronteiras ao final.
    inf = float("inf")
    custo = [[inf] * (n + 1) for _ in range(n_grupos + 1)]
    corte = [[0] * (n + 1) for _ in range(n_grupos + 1)]
    custo[0][0] = 0.0
    for k in range(1, n_grupos + 1):
        for i in range(k, n + 1):
            for j in range(k - 1, i):
                candidato = custo[k - 1][j] + sse(j, i)
                if candidato < custo[k][i]:
                    custo[k][i] = candidato
                    corte[k][i] = j
    fronteiras: list[int] = []
    i = n
    for k in range(n_grupos, 0, -1):
        j = corte[k][i]
        if j > 0:
            fronteiras.append(j)
        i = j
    return sorted(fronteiras)


def classificar_tiers(quantidade_por_unidade: pd.Series, n_grupos: int = 3) -> pd.Series:
    """Rotula cada unidade em um tier de escala por cortes em log(quantidade).

    Recebe a quantidade produzida (t) por unidade — de preferência estabilizada
    pela média recente — e devolve o rótulo de negócio de cada tier. Os cortes
    são os *natural breaks* do log (mínima variância intra-grupo), ancorados nos
    gaps naturais da distribuição. Unidades com quantidade ausente ou não
    positiva não recebem tier (NA), pois não têm escala observável.
    """
    serie = quantidade_por_unidade.dropna()
    serie = serie[serie > 0]
    resultado = pd.Series(pd.NA, index=quantidade_por_unidade.index, dtype="object")
    if serie.empty:
        return resultado
    ordenada = serie.sort_values(ascending=False)
    log = np.log(ordenada.to_numpy(dtype="float64"))
    grupos = min(n_grupos, len(ordenada))
    fronteiras = _cortes_otimos(log, grupos)
    rotulos = np.zeros(len(log), dtype=int)
    for tier, inicio in enumerate(fronteiras):
        rotulos[inicio:] = tier + 1
    resultado.loc[ordenada.index] = [ROTULOS.get(r, ROTULOS[max(ROTULOS)]) for r in rotulos]
    return resultado


def dispersao_log(quantidade_por_unidade: pd.Series) -> float:
    """Desvio-padrão do log da quantidade; a dispersão de escala da base."""
    serie = quantidade_por_unidade.dropna()
    serie = serie[serie > 0]
    if len(serie) < 2:
        return float("nan")
    return float(np.log(serie.to_numpy(dtype="float64")).std())


def dispersao_intra_tier(quantidade_por_unidade: pd.Series, tiers: pd.Series) -> float:
    """Dispersão de escala residual após agrupar por tier (raiz do SSE médio).

    É o critério do gate do ADR 0006: precisa ficar abaixo da dispersão global
    para provar que comparar dentro do tier é mais justo que na base inteira.
    """
    dados = pd.DataFrame({"quantidade": quantidade_por_unidade, "tier": tiers}).dropna()
    dados = dados[dados["quantidade"] > 0]
    if len(dados) < 2:
        return float("nan")
    log = np.log(dados["quantidade"].to_numpy(dtype="float64"))
    rotulos = dados["tier"].to_numpy()
    sse = 0.0
    for tier in np.unique(rotulos):
        grupo = log[rotulos == tier]
        sse += ((grupo - grupo.mean()) ** 2).sum()
    return float(np.sqrt(sse / len(log)))
