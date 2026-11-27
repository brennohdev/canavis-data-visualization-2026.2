from __future__ import annotations

import pandas as pd

SITUACOES = ("presente", "sem_producao", "suprimido", "sem_registro")
COLUNAS_MATRIZ = ["fonte_id", "territorio_id", "nivel_territorial", "ano_referencia", "situacao"]
FONTE_PAM = "ibge_pam_1612"
FONTE_CONAB = "conab_cana"
FONTE_ANP = "anp_vendas_etanol"


def classificar_situacao(quantidade, situacao: str) -> str:
    if situacao == "sem_producao":
        return "sem_producao"
    if situacao == "suprimido":
        return "suprimido"
    if situacao == "presente":
        if pd.isna(quantidade):
            raise ValueError("Quantidade ausente com situação 'presente' é inconsistente")
        return "presente"
    raise ValueError(f"Situação desconhecida: {situacao!r}")


def _observadas_pam(fatos_pam: pd.DataFrame) -> pd.DataFrame:
    situacao = [
        classificar_situacao(q, s)
        for q, s in zip(fatos_pam["quantidade_produzida_t"], fatos_pam["situacao_quantidade"])
    ]
    return pd.DataFrame(
        {
            "fonte_id": FONTE_PAM,
            "territorio_id": fatos_pam["territorio_id"].to_numpy(),
            "ano_referencia": fatos_pam["ano_referencia"].to_numpy(),
            "situacao": situacao,
        }
    )


def _observadas_presentes(fonte_id: str, territorio_id, ano) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "fonte_id": fonte_id,
            "territorio_id": pd.Series(territorio_id).to_numpy(),
            "ano_referencia": pd.Series(ano).to_numpy(),
            "situacao": "presente",
        }
    )


def _com_grade(observadas: pd.DataFrame, dim_territorio: pd.DataFrame) -> pd.DataFrame:
    fonte_id = observadas["fonte_id"].iloc[0]
    niveis = set(observadas["territorio_id"].str.split(":").str[0])
    territorios = dim_territorio.loc[
        dim_territorio["nivel_territorial"].isin(niveis), "territorio_id"
    ].tolist()
    anos = sorted(observadas["ano_referencia"].unique())
    grade = pd.MultiIndex.from_product(
        [territorios, anos], names=["territorio_id", "ano_referencia"]
    ).to_frame(index=False)
    grade["fonte_id"] = fonte_id
    completa = grade.merge(
        observadas, on=["fonte_id", "territorio_id", "ano_referencia"], how="outer"
    )
    completa["situacao"] = completa["situacao"].fillna("sem_registro")
    return completa


def construir_matriz_cobertura(
    fatos_pam: pd.DataFrame,
    fato_industria: pd.DataFrame,
    fato_vendas_uf: pd.DataFrame,
    dim_territorio: pd.DataFrame,
) -> pd.DataFrame:
    partes = [
        _observadas_pam(fatos_pam),
        _observadas_presentes(
            FONTE_CONAB, fato_industria["territorio_id"], fato_industria["ano_alinhamento"]
        ),
        _observadas_presentes(
            FONTE_ANP, fato_vendas_uf["territorio_id"], fato_vendas_uf["ano_referencia"]
        ),
    ]
    matriz = pd.concat([_com_grade(parte, dim_territorio) for parte in partes], ignore_index=True)
    matriz["nivel_territorial"] = matriz["territorio_id"].str.split(":").str[0]
    matriz["ano_referencia"] = matriz["ano_referencia"].astype("int64")
    return (
        matriz[COLUNAS_MATRIZ]
        .sort_values(["fonte_id", "nivel_territorial", "territorio_id", "ano_referencia"])
        .reset_index(drop=True)
    )


def resumo_pb(matriz: pd.DataFrame, ano: int) -> dict[str, int]:
    recorte = matriz[
        (matriz["fonte_id"] == FONTE_PAM)
        & (matriz["nivel_territorial"] == "municipio")
        & (matriz["territorio_id"].str.startswith("municipio:25"))
        & (matriz["ano_referencia"] == ano)
    ]
    contagem = recorte["situacao"].value_counts()
    return {situacao: int(contagem.get(situacao, 0)) for situacao in SITUACOES}


def ultimo_ano_por_fonte(matriz: pd.DataFrame) -> dict[str, int]:
    presentes = matriz[matriz["situacao"] == "presente"]
    return {
        fonte: int(ano) for fonte, ano in presentes.groupby("fonte_id")["ano_referencia"].max().items()
    }
