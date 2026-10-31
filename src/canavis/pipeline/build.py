from __future__ import annotations

from pathlib import Path

import pandas as pd

from canavis import storage
from canavis.config import load_settings
from canavis.domain import indicators
from canavis.logging import get_logger
from canavis.pipeline.industrial import construir_industria, construir_vendas

_log = get_logger(__name__)
_NIVEIS = {
    "serie_municipios_pb": "municipio",
    "serie_microrregioes_pb": "microrregiao",
    "serie_ufs_brasil": "uf",
}
_FONTE_ID = "ibge_pam_1612"
_ORIGEM = {"extracao", "cod_local", "local", "periodo", "variavel", "valor", "situacao_valor"}
_REFERENCIA = Path(__file__).resolve().parents[3] / "data/reference/municipios_pb_ibge.parquet"


def build_all() -> dict[str, Path]:
    """Materializa a estrela anual da PAM na camada gold."""
    settings = load_settings()
    tabelas = construir_estrela(
        storage.read(settings.paths.interim, "ibge_pam"), pd.read_parquet(_REFERENCIA)
    )
    fontes = []
    if storage.exists(settings.paths.interim, "conab_cana"):
        tabelas["fato_industria"] = construir_industria(storage.read(settings.paths.interim, "conab_cana"))
        fontes.append({"fonte_id": "conab_cana", "fonte": "CONAB", "tabela": "Série Histórica da Cana",
                       "periodicidade": "safra", "unidade_quantidade": "mil toneladas / mil litros",
                       "unidade_area": "mil hectares", "url": "https://portaldeinformacoes.conab.gov.br/downloads/arquivos/SerieHistoricaCana.txt"})
    if storage.exists(settings.paths.interim, "anp_vendas_etanol"):
        tabelas.update(construir_vendas(storage.read(settings.paths.interim, "anp_vendas_etanol"), tabelas["dim_territorio"]))
        fontes.append({"fonte_id": "anp_vendas_etanol", "fonte": "ANP", "tabela": "Vendas anuais de etanol hidratado por município",
                       "periodicidade": "anual", "unidade_quantidade": "litros", "unidade_area": None,
                       "url": "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/vendas-de-derivados-de-petroleo-e-biocombustiveis"})
    if fontes:
        tabelas["dim_fonte"] = pd.concat([tabelas["dim_fonte"], pd.DataFrame(fontes)], ignore_index=True)
    datas = pd.concat([f["data_referencia"] for nome, f in tabelas.items() if nome.startswith("fato_")])
    tabelas["dim_calendario"] = _dim_calendario(datas.dt.year.min(), datas.dt.year.max())
    for nome, frame in tabelas.items():
        if not nome.startswith("fato_"):
            continue
        for coluna in ["territorio_id", "uf_id"]:
            if coluna in frame and not frame[coluna].dropna().isin(tabelas["dim_territorio"]["territorio_id"]).all():
                raise ValueError(f"{nome}: chave territorial sem dimensão")
        if not frame["fonte_id"].isin(tabelas["dim_fonte"]["fonte_id"]).all():
            raise ValueError(f"{nome}: fonte sem dimensão")
    escritos = {}
    for nome, frame in tabelas.items():
        destino = storage.write(frame, settings.paths.processed, nome)
        _log.info("gold | %s | %d linhas | %s", nome, len(frame), destino.name)
        escritos[nome] = destino
    return escritos


def construir_estrela(ibge: pd.DataFrame, referencia: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Constrói fato e dimensões sem misturar grãos territoriais."""
    faltantes = _ORIGEM - set(ibge.columns)
    if faltantes:
        raise ValueError(
            f"Silver PAM incompleta ({sorted(faltantes)}). Execute --stage transform antes de build."
        )
    ibge = ibge.copy()
    ibge["cod_local"] = ibge["cod_local"].astype("string")
    ibge["periodo"] = pd.to_numeric(ibge["periodo"], errors="raise").astype("int64")
    desconhecidas = set(ibge["extracao"]) - set(_NIVEIS)
    if desconhecidas:
        raise ValueError(f"Extrações territoriais desconhecidas: {sorted(desconhecidas)}")
    chave = ["extracao", "cod_local", "periodo", "variavel"]
    if ibge.duplicated(chave).any():
        raise ValueError("PAM contém células territoriais/anuais/variáveis duplicadas")
    if (ibge.groupby(["extracao", "cod_local"])["local"].nunique() != 1).any():
        raise ValueError("Código territorial com mais de um nome na PAM")

    indice = ["extracao", "cod_local", "local", "periodo"]
    valores = ibge.set_index(indice + ["variavel"])["valor"].unstack("variavel")
    situacoes = ibge.set_index(indice + ["variavel"])["situacao_valor"].unstack("variavel")
    exigidas = {"Quantidade produzida", "Área colhida"}
    if not exigidas.issubset(valores.columns):
        raise ValueError(f"Variáveis PAM ausentes: {sorted(exigidas - set(valores.columns))}")
    fato = pd.DataFrame(index=valores.index)
    fato["quantidade_produzida_t"] = valores["Quantidade produzida"]
    fato["area_colhida_ha"] = valores["Área colhida"]
    fato["situacao_quantidade"] = situacoes["Quantidade produzida"]
    fato["situacao_area"] = situacoes["Área colhida"]
    fato = fato.reset_index()
    fato["nivel_territorial"] = fato["extracao"].map(_NIVEIS)
    fato["territorio_id"] = fato["nivel_territorial"] + ":" + fato["cod_local"]
    fato["data_referencia"] = pd.to_datetime(fato["periodo"].astype(str) + "-12-31")
    fato["fonte_id"] = _FONTE_ID
    fato["produtividade_t_ha"] = indicators.produtividade(
        fato["quantidade_produzida_t"], fato["area_colhida_ha"]
    )
    fato = fato.rename(columns={"periodo": "ano_referencia"}).drop(
        columns=["extracao", "cod_local", "local"]
    )
    fato = fato[
        ["territorio_id", "data_referencia", "fonte_id", "nivel_territorial", "ano_referencia",
         "quantidade_produzida_t", "area_colhida_ha", "produtividade_t_ha",
         "situacao_quantidade", "situacao_area"]
    ].sort_values(["nivel_territorial", "territorio_id", "ano_referencia"]).reset_index(drop=True)

    territorio = _dim_territorio(ibge, referencia)
    calendario = _dim_calendario(fato["ano_referencia"].min(), fato["ano_referencia"].max())
    fonte = pd.DataFrame([{
        "fonte_id": _FONTE_ID,
        "fonte": "IBGE PAM",
        "tabela": "SIDRA 1612",
        "periodicidade": "anual",
        "unidade_quantidade": "toneladas",
        "unidade_area": "hectares",
        "url": "https://sidra.ibge.gov.br/tabela/1612",
    }])
    if not fato["territorio_id"].isin(territorio["territorio_id"]).all():
        raise ValueError("Fato contém território sem dimensão")
    if not fato["data_referencia"].isin(calendario["data_referencia"]).all():
        raise ValueError("Fato contém data sem calendário")
    return {"fato_producao": fato, "dim_territorio": territorio,
            "dim_calendario": calendario, "dim_fonte": fonte}


def _dim_territorio(ibge: pd.DataFrame, referencia: pd.DataFrame) -> pd.DataFrame:
    colunas = [
        "cod_municipio", "cod_microrregiao", "cod_regiao_imediata", "nome_regiao_imediata",
        "cod_regiao_intermediaria", "nome_regiao_intermediaria", "cod_uf",
    ]
    if set(colunas) - set(referencia.columns):
        raise ValueError("Referência territorial do IBGE incompleta")
    ref = referencia[colunas].astype("string")
    if ref["cod_municipio"].duplicated().any():
        raise ValueError("Referência territorial possui municípios duplicados")
    dim = ibge[["extracao", "cod_local", "local"]].drop_duplicates().copy()
    dim["nivel_territorial"] = dim["extracao"].map(_NIVEIS)
    dim["territorio_id"] = dim["nivel_territorial"] + ":" + dim["cod_local"]
    dim = dim.rename(columns={"local": "nome_territorio"})
    dim["cod_municipio"] = dim["cod_local"].where(dim["nivel_territorial"] == "municipio")
    dim = dim.merge(ref, on="cod_municipio", how="left", validate="many_to_one")
    municipios = dim["nivel_territorial"] == "municipio"
    if dim.loc[municipios, "cod_microrregiao"].isna().any():
        raise ValueError("Município da PAM sem correspondência na referência oficial")

    # A divisão de 2017 pode cortar a microrregião antiga. Só propagamos
    # uma região imediata/intermediária quando a associação é unívoca.
    micro = ref[["cod_microrregiao", "cod_uf"]].drop_duplicates("cod_microrregiao")
    for codigo, nome in [
        ("cod_regiao_imediata", "nome_regiao_imediata"),
        ("cod_regiao_intermediaria", "nome_regiao_intermediaria"),
    ]:
        univoco = ref.groupby("cod_microrregiao")[codigo].nunique().eq(1)
        nomes = ref[["cod_microrregiao", codigo, nome]].drop_duplicates("cod_microrregiao").copy()
        nomes.loc[~nomes["cod_microrregiao"].map(univoco), [codigo, nome]] = pd.NA
        micro = micro.merge(nomes, on="cod_microrregiao", validate="one_to_one")
    micro = micro.rename(columns={"cod_microrregiao": "cod_local"})
    micros = dim["nivel_territorial"] == "microrregiao"
    micro_rows = dim.loc[micros, ["territorio_id", "cod_local"]].merge(
        micro, on="cod_local", how="left", validate="one_to_one"
    ).set_index("territorio_id")
    if micro_rows["cod_uf"].isna().any():
        raise ValueError("Microrregião da PAM sem referência oficial")
    dim = dim.set_index("territorio_id")
    for coluna in ["cod_uf", "cod_regiao_imediata", "nome_regiao_imediata",
                   "cod_regiao_intermediaria", "nome_regiao_intermediaria"]:
        dim.loc[micro_rows.index, coluna] = micro_rows[coluna]
    dim.loc[micro_rows.index, "cod_microrregiao"] = micro_rows["cod_local"]
    ufs = dim["nivel_territorial"] == "uf"
    dim.loc[ufs, "cod_uf"] = dim.loc[ufs, "cod_local"]
    dim["mapeamento_regiao_2017"] = "nao_aplicavel"
    dim.loc[dim["nivel_territorial"] == "municipio", "mapeamento_regiao_2017"] = "direto_ibge"
    dim.loc[dim["nivel_territorial"] == "microrregiao", "mapeamento_regiao_2017"] = "unico_ibge"
    dim.loc[(dim["nivel_territorial"] == "microrregiao") &
            dim["cod_regiao_imediata"].isna(), "mapeamento_regiao_2017"] = "multiplas_regioes"
    return dim.reset_index().drop(columns=["extracao"]).sort_values(
        ["nivel_territorial", "cod_local"]
    ).reset_index(drop=True)


def _dim_calendario(ano_inicial: int, ano_final: int) -> pd.DataFrame:
    datas = pd.date_range(f"{ano_inicial}-01-01", f"{ano_final}-12-31", freq="D")
    return pd.DataFrame({"data_referencia": datas, "ano": datas.year,
                         "mes": datas.month, "trimestre": datas.quarter, "dia": datas.day})


def agregar_producao(fato: pd.DataFrame, por: list[str]) -> pd.DataFrame:
    """Soma medidas aditivas e recalcula a taxa; parcela ausente mantém NA."""
    if "nivel_territorial" in fato and "nivel_territorial" not in por:
        if fato["nivel_territorial"].nunique() > 1:
            raise ValueError("Filtre um nível territorial ou inclua-o no agrupamento")
    medidas = ["quantidade_produzida_t", "area_colhida_ha"]
    agregado = fato.groupby(por, dropna=False)[medidas].agg(
        lambda serie: serie.sum() if serie.notna().all() else pd.NA
    ).reset_index()
    agregado["produtividade_t_ha"] = indicators.produtividade(
        agregado[medidas[0]], agregado[medidas[1]]
    )
    return agregado
