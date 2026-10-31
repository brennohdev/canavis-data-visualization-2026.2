"""Gold industrial: fatos separados para safra CONAB e ano civil ANP."""
from __future__ import annotations

import re
import unicodedata

import pandas as pd

from canavis.domain.features import intensidade_industrial
from canavis.domain.indicators import mix_etanol_acucar

COD_UF = dict(zip(
    "RO AC AM RR PA AP TO MA PI CE RN PB PE AL SE BA MG ES RJ SP PR SC RS MS MT GO DF".split(),
    "11 12 13 14 15 16 17 21 22 23 24 25 26 27 28 29 31 32 33 35 41 42 43 50 51 52 53".split(),
))


def ano_inicio_safra(safras: pd.Series) -> pd.Series:
    """Convenção de alinhamento: 2023/24 recebe 2023, sem converter o período."""
    def inicio(valor):
        match = re.fullmatch(r"(\d{4})/(\d{2}|\d{4})", str(valor).strip())
        if not match:
            raise ValueError(f"Safra inválida: {valor}")
        ano, fim = match.groups()
        if int(fim) != (int(ano) + 1) % (100 if len(fim) == 2 else 10000):
            raise ValueError(f"Safra não consecutiva: {valor}")
        return int(ano)
    return safras.map(inicio).astype("Int64")


def construir_industria(conab: pd.DataFrame) -> pd.DataFrame:
    frame = conab.copy()
    frame["safra"] = frame["ano_agricola"].astype("string").str.strip()
    frame["uf"] = frame["uf"].astype("string").str.strip()
    if frame.duplicated(["uf", "safra"]).any():
        raise ValueError("CONAB tem mais de um levantamento por UF/safra; seleção explícita necessária")
    frame["territorio_id"] = _chave_uf(frame["uf"])
    frame["ano_alinhamento"] = ano_inicio_safra(frame["safra"])
    frame["data_referencia"] = pd.to_datetime(frame["ano_alinhamento"].astype(str) + "-12-31")
    frame["regra_alinhamento"] = "ano_inicial_safra"
    frame["fonte_id"] = "conab_cana"
    frame["situacao_levantamento"] = frame["dsc_situacao_levantamento"].astype("string").str.strip()
    frame = frame.rename(columns={"producao_mil_t": "cana_mil_t", "produtcao_atr_kg_t": "atr_kg_t"})
    frame["mix_etanol_acucar_l_t"] = mix_etanol_acucar(
        frame["producao_etanol_total_mil_l"], frame["producao_acucar_mil_t"]
    )
    frame["intensidade_acucar_t_t"] = intensidade_industrial(
        frame["producao_acucar_mil_t"], frame["cana_mil_t"]
    )
    return frame[[
        "territorio_id", "uf", "safra", "ano_alinhamento", "data_referencia", "fonte_id",
        "regra_alinhamento", "situacao_levantamento", "cana_mil_t", "area_plantada_mil_ha",
        "producao_acucar_mil_t", "producao_etanol_anidro_mil_l", "producao_etanol_hidratado_mil_l",
        "producao_etanol_total_mil_l", "atr_kg_t", "mix_etanol_acucar_l_t", "intensidade_acucar_t_t",
    ]].sort_values(["territorio_id", "safra"]).reset_index(drop=True)


def _chave_uf(ufs: pd.Series) -> pd.Series:
    codigos = ufs.map(COD_UF)
    if codigos.isna().any():
        raise ValueError(f"UF não reconhecida: {ufs[codigos.isna()].unique().tolist()}")
    return "uf:" + codigos


def _nome(valor: str) -> str:
    texto = unicodedata.normalize("NFKD", str(valor).split(" - ")[0])
    return re.sub(r"[^A-Z0-9]", "", texto.encode("ascii", "ignore").decode().upper())


def construir_vendas(anp: pd.DataFrame, territorios: pd.DataFrame) -> dict[str, pd.DataFrame]:
    # Apenas repetições de todas as colunas são removidas. Conflitos não são somados.
    frame = anp.drop_duplicates().copy()
    frame["ano"] = pd.to_numeric(frame["ano"], errors="raise").astype("int64")
    frame["uf"] = frame["uf"].astype("string").str.strip()
    frame["codigo_municipio_origem"] = frame["código_ibge"].astype("string")
    frame["nome_municipio_origem"] = frame["município"].astype("string")
    if frame.duplicated(["uf", "ano", "codigo_municipio_origem"]).any():
        raise ValueError("ANP tem registros conflitantes para UF/município/ano")
    frame["uf_id"] = _chave_uf(frame["uf"])
    frame["data_referencia"] = pd.to_datetime(frame["ano"].astype(str) + "-12-31")
    frame["fonte_id"] = "anp_vendas_etanol"
    frame["escopo_vendas"] = frame["ano"].map(
        lambda ano: "vendas_e_consumo_proprio" if ano <= 2006 else "vendas"
    )
    pb = territorios[territorios["nivel_territorial"] == "municipio"].set_index("cod_local")
    nomes = frame["codigo_municipio_origem"].map(pb["nome_territorio"].map(_nome))
    valida = frame["uf"].eq("PB") & nomes.notna() & nomes.eq(frame["nome_municipio_origem"].map(_nome))
    frame["territorio_id"] = ("municipio:" + frame["codigo_municipio_origem"]).where(valida)
    frame["status_chave"] = "nao_validada_fora_pb"
    frame.loc[frame["uf"].eq("PB"), "status_chave"] = "divergente_ou_sem_correspondencia"
    frame.loc[valida, "status_chave"] = "codigo_nome_conferidos_pb"
    frame = frame.rename(columns={"vendas": "vendas_etanol_hidratado_l", "ano": "ano_referencia"})
    cols = ["uf_id", "uf", "ano_referencia", "data_referencia", "fonte_id", "escopo_vendas"]
    totais = frame.groupby(cols, dropna=False)["vendas_etanol_hidratado_l"].agg(
        lambda serie: serie.sum() if serie.notna().all() else pd.NA
    ).reset_index().rename(columns={"uf_id": "territorio_id"})
    detalhe = frame[cols + ["codigo_municipio_origem", "nome_municipio_origem", "territorio_id",
                            "status_chave", "vendas_etanol_hidratado_l"]]
    return {"fato_vendas_etanol_uf": totais, "fato_vendas_etanol_municipio": detalhe}
