from __future__ import annotations

import numpy as np
import pandas as pd

T95_BICAUDAL = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306,
    9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
    16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086, 21: 2.080, 22: 2.074,
    23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045,
    30: 2.042,
}
T95_ASSINTOTICO = 1.96
N_MINIMO = 4
JANELAS_PADRAO = (5, 10, 21)


def quantil_t95(graus_liberdade: int) -> float:
    return T95_BICAUDAL.get(graus_liberdade, T95_ASSINTOTICO)


def _resultado(status: str, n: int = 0, ano_inicial=None, ano_final=None) -> dict:
    nan = float("nan")
    return {
        "inclinacao_t_ha_ano": nan,
        "erro_padrao": nan,
        "ic95_inferior": nan,
        "ic95_superior": nan,
        "n": n,
        "ano_inicial": ano_inicial,
        "ano_final": ano_final,
        "classe": "indisponivel",
        "status": status,
    }


def _classificar(inferior: float, superior: float) -> str:
    if inferior > 0:
        return "sobe"
    if superior < 0:
        return "cai"
    return "estavel"


def tendencia_janela(anos, valores, janela: int, sem_ultimo: bool = False) -> dict:
    dados = pd.DataFrame({"ano": list(anos), "valor": list(valores)}).sort_values("ano")
    if sem_ultimo:
        dados = dados.iloc[:-1]
    dados = dados.iloc[-janela:]
    n = len(dados)
    if n == 0:
        return _resultado("serie_curta")
    ano_inicial, ano_final = int(dados["ano"].iloc[0]), int(dados["ano"].iloc[-1])
    if dados.isna().any().any() or dados["ano"].duplicated().any():
        return _resultado("serie_incompleta", n, ano_inicial, ano_final)
    x = dados["ano"].to_numpy(dtype=float)
    y = dados["valor"].to_numpy(dtype=float)
    if not np.isfinite(y).all() or not np.all(np.diff(x) == 1):
        return _resultado("serie_incompleta", n, ano_inicial, ano_final)
    if n < N_MINIMO:
        return _resultado("serie_curta", n, ano_inicial, ano_final)
    centrado = x - x.mean()
    soma_x2 = float((centrado**2).sum())
    inclinacao = float((centrado * (y - y.mean())).sum() / soma_x2)
    residuo = y - (y.mean() + inclinacao * centrado)
    erro_padrao = float(np.sqrt((residuo**2).sum() / (n - 2) / soma_x2))
    margem = quantil_t95(n - 2) * erro_padrao
    inferior, superior = inclinacao - margem, inclinacao + margem
    return {
        "inclinacao_t_ha_ano": inclinacao,
        "erro_padrao": erro_padrao,
        "ic95_inferior": inferior,
        "ic95_superior": superior,
        "n": n,
        "ano_inicial": ano_inicial,
        "ano_final": ano_final,
        "classe": _classificar(inferior, superior),
        "status": "ok",
    }


def tendencia_por_janelas(anos, valores, janelas=JANELAS_PADRAO) -> dict:
    resultado = {}
    for janela in janelas:
        resultado[(janela, False)] = tendencia_janela(anos, valores, janela)
        resultado[(janela, True)] = tendencia_janela(anos, valores, janela, sem_ultimo=True)
    return resultado
