import pandas as pd
import pytest

from canavis import storage
from canavis.pipeline.build import agregar_producao, construir_estrela


def _dados():
    linhas = []
    for codigo, nome, quantidade, area, situacao in [
        ("2500106", "Água Branca - PB", 100.0, 10.0, "presente"),
        ("2500205", "Aguiar - PB", 300.0, 20.0, "presente"),
        ("2500304", "Alagoa Grande - PB", pd.NA, pd.NA, "suprimido"),
        ("2500403", "Alagoa Nova - PB", 0.0, 0.0, "sem_producao"),
    ]:
        for variavel, valor in [("Quantidade produzida", quantidade), ("Área colhida", area)]:
            linhas.append({"extracao": "serie_municipios_pb", "cod_local": codigo,
                           "local": nome, "periodo": 2023, "variavel": variavel,
                           "valor": valor, "situacao_valor": situacao})
    pam = pd.DataFrame(linhas)
    referencia = pd.DataFrame({
        "cod_municipio": ["2500106", "2500205", "2500304", "2500403"],
        "cod_microrregiao": ["25007"] * 4,
        "cod_regiao_imediata": ["250009"] * 4,
        "nome_regiao_imediata": ["Patos"] * 4,
        "cod_regiao_intermediaria": ["2503"] * 4,
        "nome_regiao_intermediaria": ["Patos"] * 4,
        "cod_uf": ["25"] * 4,
    })
    return pam, referencia


def test_estrela_preserva_zero_suprimido_e_chaves():
    tabelas = construir_estrela(*_dados())
    fato = tabelas["fato_producao"].set_index("territorio_id")
    dim = tabelas["dim_territorio"]
    calendario = tabelas["dim_calendario"]
    assert len(fato) == 4
    assert dim["territorio_id"].is_unique
    assert calendario["data_referencia"].is_unique
    assert set(fato.index) <= set(dim["territorio_id"])
    assert set(fato["data_referencia"]) <= set(calendario["data_referencia"])
    assert fato.loc["municipio:2500304", "situacao_quantidade"] == "suprimido"
    assert pd.isna(fato.loc["municipio:2500304", "quantidade_produzida_t"])
    assert fato.loc["municipio:2500403", "quantidade_produzida_t"] == 0
    assert pd.isna(fato.loc["municipio:2500403", "produtividade_t_ha"])


def test_agregacao_recalcula_razao_e_nao_mede_media_de_razoes():
    fato = construir_estrela(*_dados())["fato_producao"]
    conhecido = fato[fato["situacao_quantidade"] == "presente"].copy()
    conhecido["grupo"] = "A"
    agregado = agregar_producao(conhecido, ["grupo"])
    assert agregado.loc[0, "quantidade_produzida_t"] == 400
    assert agregado.loc[0, "area_colhida_ha"] == 30
    assert agregado.loc[0, "produtividade_t_ha"] == pytest.approx(400 / 30)


def test_agregacao_com_suprimido_nao_subestima_total():
    fato = construir_estrela(*_dados())["fato_producao"].copy()
    fato["grupo"] = "A"
    agregado = agregar_producao(fato, ["grupo"])
    assert pd.isna(agregado.loc[0, "quantidade_produzida_t"])
    assert pd.isna(agregado.loc[0, "produtividade_t_ha"])


def test_microrregiao_que_cruza_divisao_nova_nao_recebe_regiao_unica():
    pam, referencia = _dados()
    referencia.loc[1, ["cod_regiao_imediata", "nome_regiao_imediata"]] = ["250013", "Princesa Isabel"]
    for variavel, valor in [("Quantidade produzida", 400), ("Área colhida", 30)]:
        pam.loc[len(pam)] = ["serie_microrregioes_pb", "25007", "Serra do Teixeira - PB",
                             2023, variavel, valor, "presente"]
    dim = construir_estrela(pam, referencia)["dim_territorio"].set_index("territorio_id")
    micro = dim.loc["microrregiao:25007"]
    assert micro["mapeamento_regiao_2017"] == "multiplas_regioes"
    assert pd.isna(micro["cod_regiao_imediata"])
    assert micro["cod_regiao_intermediaria"] == "2503"


def test_celula_pam_duplicada_falha():
    pam, referencia = _dados()
    duplicado = pd.concat([pam, pam.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicadas"):
        construir_estrela(duplicado, referencia)


def test_niveis_diferentes_nao_sao_somados_juntos():
    frame = pd.DataFrame({"nivel_territorial": ["municipio", "uf"],
                          "ano_referencia": [2023, 2023],
                          "quantidade_produzida_t": [1, 1], "area_colhida_ha": [1, 1]})
    with pytest.raises(ValueError, match="nível territorial"):
        agregar_producao(frame, ["ano_referencia"])


def _dados_com_ufs():
    """Município (PB) mais três UFs de escalas distintas, para exercitar tier."""
    pam, referencia = _dados()
    ufs = [
        ("35", "São Paulo", 4.0e8, 5.0e6),
        ("52", "Goiás", 7.0e7, 1.0e6),
        ("14", "Roraima", 2.0e3, 1.0e2),
    ]
    linhas = []
    for codigo, nome, quantidade, area in ufs:
        for variavel, valor in [("Quantidade produzida", quantidade), ("Área colhida", area)]:
            linhas.append({"extracao": "serie_ufs_brasil", "cod_local": codigo,
                           "local": nome, "periodo": 2023, "variavel": variavel,
                           "valor": valor, "situacao_valor": "presente"})
    pam = pd.concat([pam, pd.DataFrame(linhas)], ignore_index=True)
    return pam, referencia


def test_tier_preenchido_para_ufs_e_nulo_para_outros_niveis():
    tabelas = construir_estrela(*_dados_com_ufs())
    dim = tabelas["dim_territorio"].set_index("territorio_id")
    assert "tier" in dim.columns
    ufs = dim[dim["nivel_territorial"] == "uf"]
    assert ufs["tier"].notna().all()
    assert dim.loc[dim["nivel_territorial"] == "municipio", "tier"].isna().all()
    # São Paulo (maior escala) deve cair no tier grande; Roraima no pequeno.
    assert "grande" in dim.loc["uf:35", "tier"]
    assert "pequena" in dim.loc["uf:14", "tier"]


def test_tier_preserva_integridade_referencial_da_estrela():
    tabelas = construir_estrela(*_dados_com_ufs())
    fato = tabelas["fato_producao"]
    dim = tabelas["dim_territorio"]
    assert fato["territorio_id"].isin(dim["territorio_id"]).all()
    assert dim["territorio_id"].is_unique


@pytest.mark.parametrize("formato", ["parquet", "csv", "xlsx"])
def test_formatos_de_exportacao_preservam_nulo_e_zero(tmp_path, monkeypatch, formato):
    from types import SimpleNamespace

    monkeypatch.setattr(storage, "load_settings", lambda: SimpleNamespace(
        storage=SimpleNamespace(format=formato, compression="zstd")
    ))
    exemplo = pd.DataFrame({"valor": [0.0, float("nan"), 2.5]})
    caminho = storage.write(exemplo, tmp_path, "exemplo")
    assert caminho.suffix == f".{formato}"
    lido = storage.read(tmp_path, "exemplo")
    assert lido["valor"].iloc[0] == 0
    assert pd.isna(lido["valor"].iloc[1])
    assert lido["valor"].iloc[2] == 2.5
