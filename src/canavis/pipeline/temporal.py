from __future__ import annotations

import pandas as pd

from canavis.domain.features import decompor_serie_anual, teste_chow


def enriquecer_serie(fato: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta análise histórica apenas a microrregião/UF, sem alterar o grão."""
    resultado = fato.copy()
    for coluna in ["tendencia_t_ha", "oscilacao_t_ha", "f_chow", "p_chow"]:
        resultado[coluna] = float("nan")
    resultado["status_chow"] = "nao_aplicavel_municipio"
    resultado["ponto_candidato_quebra"] = pd.Series(pd.NA, index=fato.index, dtype="boolean")
    resultado["quebra_confirmada"] = pd.Series(pd.NA, index=fato.index, dtype="boolean")
    elegivel = fato["nivel_territorial"].isin(["microrregiao", "uf"])
    for _, grupo in fato.loc[elegivel].groupby("territorio_id"):
        componentes = decompor_serie_anual(grupo["ano_referencia"], grupo["produtividade_t_ha"])
        resultado.loc[grupo.index, componentes.columns] = componentes
        teste = teste_chow(grupo["ano_referencia"], grupo["produtividade_t_ha"])
        for coluna, valor in teste.items():
            resultado.loc[grupo.index, coluna] = valor
        resultado.loc[grupo.index, "ponto_candidato_quebra"] = grupo["ano_referencia"].eq(2013)
    return resultado
