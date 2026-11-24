"""Evidência para a revisão dos passos 3 e 5 da jornada (Etapa 3).

Uso: python scripts/analise_tendencia_base_municipal.py
Lê data/processed/*.parquet. Só numpy e pandas.

Parte 1: inclinação da produtividade da PB por janela, com erro-padrão, IC 95%,
         Theil-Sen e sensibilidade ao ano de 2023.
Parte 2: cobertura e variação da produtividade municipal da PAM.
"""
from __future__ import annotations

import itertools
import math
from pathlib import Path

import numpy as np
import pandas as pd

GOLD = Path(__file__).resolve().parents[1] / "data" / "processed"
PB = "uf:25"
# t de Student bicaudal 95% por graus de liberdade (n - 2)
T95 = {3: 3.182, 4: 2.776, 8: 2.306, 19: 2.093}


def ols(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    xm = x.mean()
    b = ((x - xm) * (y - y.mean())).sum() / ((x - xm) ** 2).sum()
    res = y - (y.mean() + b * (x - xm))
    se = math.sqrt((res**2).sum() / (len(x) - 2) / ((x - xm) ** 2).sum())
    return float(b), float(se)


def theil_sen(x: np.ndarray, y: np.ndarray) -> float:
    return float(np.median([(y[j] - y[i]) / (x[j] - x[i]) for i, j in itertools.combinations(range(len(x)), 2)]))


def janela(y: pd.Series, n: int, sem_ultimo: bool = False) -> str:
    s = y.iloc[:-1] if sem_ultimo else y
    s = s.iloc[-n:]
    x, v = s.index.to_numpy(float), s.to_numpy(float)
    b, se = ols(x, v)
    t = T95[len(s) - 2]
    return (f"{s.index[0]}-{s.index[-1]} (n={len(s)}): MQO {b:+.3f} t/ha/ano, EP {se:.3f}, "
            f"IC95 [{b - t * se:+.2f}; {b + t * se:+.2f}], Theil-Sen {theil_sen(x, v):+.3f}")


def parte1() -> None:
    uf = pd.read_parquet(GOLD / "fato_producao_uf.parquet")
    y = uf[uf.territorio_id == PB].set_index("ano_referencia")["produtividade_t_ha"].astype(float).sort_index()
    print("## Parte 1 — tendência da PB")
    for n in (5, 10, 21):
        print("com 2023   ", janela(y, n))
    for n in (5, 10):
        print("sem 2023   ", janela(y, n, sem_ultimo=True))
    pre, pos = y.loc[2003:2012], y.loc[2013:2022]
    print(f"média 2003-12: {pre.mean():.1f} | média 2013-22: {pos.mean():.1f} | 2023: {y.loc[2023]:.1f}")
    dif = y.diff().dropna()
    print(f"desvio-padrão da variação anual: {dif.std():.2f} t/ha | variação de 2023: {dif.loc[2023]:+.2f}")
    for a, b in ((2013, 2023), (2013, 2022)):
        s = y.loc[a:b]
        print(f"inclinação {a}-{b}: {ols(s.index.to_numpy(float), s.to_numpy(float))[0]:+.3f}")


def parte2() -> None:
    m = pd.read_parquet(GOLD / "fato_producao_municipio.parquet")
    print("\n## Parte 2 — base municipal da PAM")
    print("situação das linhas:", m.situacao_quantidade.value_counts().to_dict())
    a = m[m.ano_referencia == 2023]
    com = a[a.produtividade_t_ha.notna()]
    print(f"2023: {len(a)} municípios; {len(com)} com produtividade; "
          f"{(a.situacao_quantidade == 'sem_producao').sum()} sem produção; "
          f"{(a.situacao_quantidade == 'suprimido').sum()} suprimidos")
    modal = com.produtividade_t_ha.mode().iloc[0]
    print(f"2023: {com.produtividade_t_ha.nunique()} valores distintos de produtividade; "
          f"{(com.produtividade_t_ha == modal).mean():.0%} em {modal} t/ha")
    todas = m[m.produtividade_t_ha.notna()]
    print(f"geral: {todas.produtividade_t_ha.round(2).nunique()} valores distintos em {len(todas)} linhas")
    q = a.quantidade_produzida_t.dropna().sort_values(ascending=False)
    print(f"2023: 5 maiores municípios concentram {q.head(5).sum() / q.sum():.0%} da quantidade")
    area = a.area_colhida_ha.dropna().sort_values(ascending=False)
    print(f"2023: 5 maiores municípios concentram {area.head(5).sum() / area.sum():.0%} da área colhida")
    print("suprimidos por ano:", m[m.situacao_quantidade == "suprimido"].ano_referencia.value_counts().sort_index().to_dict())


if __name__ == "__main__":
    parte1()
    parte2()
