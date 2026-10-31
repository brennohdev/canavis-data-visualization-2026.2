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


def test_perfil_valor_concentra_no_tier_de_maior_escala():
    # Valor descritivo: o tier grande deve concentrar a maior fatia, sem que o
    # valor tenha participado do agrupamento. Percentuais somam 100.
    quantidade = pd.Series(
        {"a": 4e8, "b": 7e7, "c": 5e7, "d": 5e6, "e": 3e6, "f": 2e3, "g": 1e3}
    )
    rotulos = tiers.classificar_tiers(quantidade)
    valor = pd.Series(
        {"a": 950.0, "b": 30.0, "c": 20.0, "d": 3.0, "e": 2.0, "f": 0.1, "g": 0.1}
    )
    perfil = tiers.perfil_valor_por_tier(valor, rotulos)
    assert perfil.sum() == pytest.approx(100.0)
    assert perfil.idxmax() == tiers.ROTULOS[0]
    assert perfil[tiers.ROTULOS[0]] > perfil[tiers.ROTULOS[1]] > perfil[tiers.ROTULOS[2]]


# --- Evidência reproduzível do gate sobre os dados reais da silver ---------
# Os números do gate do ADR 0006 (dispersão, concordância com Ward, perfil de
# valor) são recomputados aqui sobre a camada silver real, para que a evidência
# seja verificável e não apenas afirmada. Se a silver não estiver materializada
# no ambiente, o teste é pulado em vez de falhar.


def _ufs_reais():
    pytest.importorskip("pyarrow")
    from canavis import storage
    from canavis.config import load_settings

    settings = load_settings()
    if not storage.exists(settings.paths.interim, "ibge_pam"):
        pytest.skip("Silver ibge_pam não materializada neste ambiente")
    df = storage.read(settings.paths.interim, "ibge_pam")
    uf = df[df["extracao"] == "serie_ufs_brasil"].copy()
    uf["periodo"] = uf["periodo"].astype(int)
    qt = uf[uf["variavel"] == "Quantidade produzida"]
    quantidade = tiers.media_recente(qt["periodo"], qt["valor"], qt["local"])
    val = uf[uf["variavel"] == "Valor da produção"]
    valor = tiers.media_recente(val["periodo"], val["valor"], val["local"])
    return quantidade, valor


def test_gate_real_cobertura_e_dispersao_das_27_ufs():
    quantidade, _ = _ufs_reais()
    rotulos = tiers.classificar_tiers(quantidade)
    assert quantidade.index.nunique() == 27
    assert rotulos.notna().all()
    assert rotulos.index.is_unique
    assert tiers.dispersao_intra_tier(quantidade, rotulos) < tiers.dispersao_log(quantidade)


def test_gate_real_concordancia_com_ward_hierarquico():
    # Item (c) do gate recomputado sobre as 27 UFs reais: a partição de
    # classificar_tiers deve coincidir com Ward aglomerativo em 1D sobre o log.
    quantidade, _ = _ufs_reais()
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
        return rotulo

    log = np.log(quantidade.to_numpy(dtype="float64"))
    ward = ward_1d(log, 3)
    tier_para_indice = {r: i for i, r in tiers.ROTULOS.items()}
    atribuido = {u: tier_para_indice[rotulos[u]] for u in quantidade.index}
    esperado = {u: ward[np.log(quantidade[u])] for u in quantidade.index}
    assert atribuido == esperado


def test_gate_real_perfil_de_valor_concentra_no_tier_grande():
    # Item (e) do gate recomputado: ~94,8% / 5,1% / ~0,0% do valor por tier.
    quantidade, valor = _ufs_reais()
    rotulos = tiers.classificar_tiers(quantidade)
    perfil = tiers.perfil_valor_por_tier(valor, rotulos)
    assert perfil.sum() == pytest.approx(100.0)
    assert perfil[tiers.ROTULOS[0]] == pytest.approx(94.8, abs=1.0)
    assert perfil[tiers.ROTULOS[1]] == pytest.approx(5.1, abs=1.0)
    assert perfil[tiers.ROTULOS[2]] < 1.0
