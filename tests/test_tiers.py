import numpy as np
import pandas as pd
import pytest

from canavis.domain import tiers


def test_cada_unidade_recebe_exatamente_um_tier():
    quantidade = pd.Series(
        {"a": 1e8, "b": 8e7, "c": 7e7, "d": 5e6, "e": 4e6, "f": 1e4, "g": 5e3}
    )
    rotulos = tiers.classificar_tiers(quantidade)
    assert rotulos.notna().all()
    assert set(rotulos) <= set(tiers.ROTULOS.values())
    assert rotulos.index.is_unique


def test_serie_sintetica_recupera_grupos_conhecidos():
    # Três ordens de grandeza bem separadas: a classificação deve isolá-las.
    grande = {f"g{i}": v for i, v in enumerate([5.0e8, 4.0e8, 3.0e8])}
    media = {f"m{i}": v for i, v in enumerate([2.0e6, 1.5e6, 1.0e6])}
    pequena = {f"p{i}": v for i, v in enumerate([3.0e3, 2.0e3, 1.0e3])}
    quantidade = pd.Series({**grande, **media, **pequena})
    rotulos = tiers.classificar_tiers(quantidade)
    assert rotulos[list(grande)].eq(tiers.ROTULOS[0]).all()
    assert rotulos[list(media)].eq(tiers.ROTULOS[1]).all()
    assert rotulos[list(pequena)].eq(tiers.ROTULOS[2]).all()


def test_dispersao_intra_tier_menor_que_global():
    quantidade = pd.Series(
        {"a": 4e8, "b": 7e7, "c": 7e7, "d": 5e7, "e": 4e7, "f": 2e7, "g": 1.7e7,
         "h": 1.5e7, "i": 5e6, "j": 3e6, "k": 1e6, "l": 3e5, "m": 4e4, "n": 1e4, "o": 2e3}
    )
    rotulos = tiers.classificar_tiers(quantidade)
    assert tiers.dispersao_intra_tier(quantidade, rotulos) < tiers.dispersao_log(quantidade)


def test_cortes_coincidem_com_ward_hierarquico():
    # Ward aglomerativo em 1D só funde segmentos adjacentes; deve convergir para
    # os mesmos cortes de variância mínima que classificar_tiers usa.
    rng = np.random.default_rng(0)
    log = np.concatenate([rng.normal(20, 0.3, 4), rng.normal(16, 0.3, 6), rng.normal(10, 0.3, 5)])
    quantidade = pd.Series(np.exp(log), index=[f"u{i}" for i in range(len(log))])
    rotulos = tiers.classificar_tiers(quantidade)

    def ward_1d(valores, k):
        ordenado = np.sort(valores)
        grupos = [[v] for v in ordenado]
        ess = lambda c: float(((np.array(c) - np.mean(c)) ** 2).sum())
        while len(grupos) > k:
            custos = [ess(grupos[i] + grupos[i + 1]) - ess(grupos[i]) - ess(grupos[i + 1])
                      for i in range(len(grupos) - 1)]
            i = int(np.argmin(custos))
            grupos[i:i + 2] = [grupos[i] + grupos[i + 1]]
        rotulo = {}
        for ordem, grupo in enumerate(reversed(grupos)):
            for v in grupo:
                rotulo[v] = ordem
        return {v: rotulo[v] for v in valores}

    ward = ward_1d(np.log(quantidade.to_numpy()), 3)
    tier_para_indice = {r: i for i, r in tiers.ROTULOS.items()}
    atribuido = {u: tier_para_indice[rotulos[u]] for u in quantidade.index}
    esperado = {u: ward[np.log(quantidade[u])] for u in quantidade.index}
    assert atribuido == esperado


def test_quantidade_ausente_ou_nao_positiva_fica_sem_tier():
    quantidade = pd.Series({"a": 1e8, "b": 5e6, "c": pd.NA, "d": 0.0, "e": -1.0})
    rotulos = tiers.classificar_tiers(quantidade)
    assert rotulos["a"] in tiers.ROTULOS.values()
    assert pd.isna(rotulos["c"])
    assert pd.isna(rotulos["d"])
    assert pd.isna(rotulos["e"])


def test_media_recente_usa_apenas_ultimos_anos():
    anos = pd.Series([2018, 2019, 2020, 2021, 2022, 2023] * 2)
    unidade = pd.Series(["x"] * 6 + ["y"] * 6)
    quantidade = pd.Series([100, 10, 20, 30, 40, 50, 1, 2, 3, 4, 5, 6], dtype="float64")
    media = tiers.media_recente(anos, quantidade, unidade, janela=5)
    # 2018 (valor 100 para x) fica de fora: média de 10,20,30,40,50 = 30.
    assert media["x"] == pytest.approx(30.0)
    assert media["y"] == pytest.approx(4.0)
