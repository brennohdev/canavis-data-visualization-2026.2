"""Gera script TMDL importável no Power BI a partir do esquema da gold."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FATOS = [
    "fato_producao",
    "fato_producao_uf",
    "fato_producao_microrregiao",
    "fato_producao_municipio",
    "fato_industria",
    "fato_vendas_etanol_uf",
    "fato_vendas_etanol_municipio",
]
# Base da URL raw do GitHub para os Parquet da gold. Trocar de branch (main -> SHA)
# ou de repositório é uma edição de uma linha aqui.
URL_BASE = "https://raw.githubusercontent.com/brennohdev/canavis-data-visualization-2026.2/main/data/processed"


def medidas_producao():
    """Mantém a mesma regra de completude das agregações da gold.

    Cada tupla é (label, dax, formato, descricao). A descricao, quando
    presente, vira uma linha '/// <descricao>' antes da medida no TMDL.
    """
    quantidade_completa = "IF(COUNTROWS(FILTER(fato_producao, ISBLANK(fato_producao[quantidade_produzida_t]))) = 0, SUM(fato_producao[quantidade_produzida_t]))"
    return [
        ("Produtividade", "IF(HASONEVALUE(dim_territorio[nivel_territorial]) && COUNTROWS(FILTER(fato_producao, ISBLANK(fato_producao[quantidade_produzida_t]) || ISBLANK(fato_producao[area_colhida_ha]))) = 0, DIVIDE(SUM(fato_producao[quantidade_produzida_t]), SUM(fato_producao[area_colhida_ha])))", "0.00", "Rendimento medio ponderado pela area (razao de agregados: soma da quantidade / soma da area), nao a media simples das produtividades. Exige nivel unico."),
        ("Participação regional", f"VAR Nivel = SELECTEDVALUE(dim_territorio[nivel_territorial]) VAR Quantidade = {quantidade_completa} VAR Total = CALCULATE({quantidade_completa}, ALL(dim_territorio), dim_territorio[nivel_territorial] = Nivel) RETURN IF(NOT ISBLANK(Nivel) && NOT ISBLANK(Quantidade), DIVIDE(Quantidade, Total))", "0.00%", "Participacao do territorio no total do SEU nivel (denominador por nivel). So e valida com nivel fixado; nunca em ranking multinivel."),
        ("Desvio vs seleção", "VAR Atual = [Produtividade] VAR Referencia = CALCULATE([Produtividade], ALLSELECTED(dim_territorio)) RETURN IF(NOT ISBLANK(Atual) && NOT ISBLANK(Referencia), DIVIDE(Atual - Referencia, Referencia))", "0.00%", "Desvio percentual da produtividade frente a referencia = a selecao visivel no visual (nao o Brasil, nao uma media fixa). Fixar nivel."),
        ("Desvio vs grupo", "VAR Tier = SELECTEDVALUE(dim_territorio[tier]) VAR Atual = [Produtividade] VAR Referencia = CALCULATE([Produtividade], ALLSELECTED(dim_territorio), KEEPFILTERS(dim_territorio[tier] = Tier)) RETURN IF(NOT ISBLANK(Tier) && NOT ISBLANK(Atual) && NOT ISBLANK(Referencia), DIVIDE(Atual - Referencia, Referencia))", "0.00%", "Desvio frente as UFs do mesmo tier (ADR 0006). Exclusiva do nivel UF; retorna vazio fora dele por construcao, nao e erro."),
    ]


def medidas_adicionais(nome):
    if nome == "fato_producao":
        return [("Tendência histórica (t por ha)", "IF(HASONEVALUE(dim_territorio[territorio_id]) && HASONEVALUE(dim_calendario[ano]), MAX(fato_producao[tendencia_t_ha]))", "0.00", None),
                ("Oscilação histórica (t por ha)", "IF(HASONEVALUE(dim_territorio[territorio_id]) && HASONEVALUE(dim_calendario[ano]), MAX(fato_producao[oscilacao_t_ha]))", "0.00", None),
                ("P Chow exploratório (2003-2023)", "IF(HASONEVALUE(dim_territorio[territorio_id]), MAX(fato_producao[p_chow]))", "0.000000", None)]
    if nome == "fato_industria":
        medidas = []
        for label, numerador, denominador in [
            ("Mix etanol açúcar (L por t)", "producao_etanol_total_mil_l", "producao_acucar_mil_t"),
            ("Intensidade açúcar (t por t)", "producao_acucar_mil_t", "cana_mil_t"),
        ]:
            dax = f'IF(SELECTEDVALUE(dim_territorio[nivel_territorial]) = "uf" && COUNTROWS(FILTER(fato_industria, ISBLANK(fato_industria[{numerador}]) || ISBLANK(fato_industria[{denominador}]))) = 0, DIVIDE(SUM(fato_industria[{numerador}]), SUM(fato_industria[{denominador}])))'
            medidas.append((label, dax, "0.0000", None))
        medidas.append(("ATR ponderado (kg por t)", 'IF(SELECTEDVALUE(dim_territorio[nivel_territorial]) = "uf" && COUNTROWS(FILTER(fato_industria, ISBLANK(fato_industria[atr_kg_t]) || ISBLANK(fato_industria[cana_mil_t]))) = 0, DIVIDE(SUMX(fato_industria, fato_industria[atr_kg_t] * fato_industria[cana_mil_t]), SUM(fato_industria[cana_mil_t])))', "0.00", None))
        # Bloco B — volume/mix em ATR-equivalente (exclusivas do nível UF).
        medidas.append(("ATR equivalente açúcar (kg)", 'IF(SELECTEDVALUE(dim_territorio[nivel_territorial]) = "uf" && NOT ISBLANK(SUM(fato_industria[producao_acucar_mil_t])), SUM(fato_industria[producao_acucar_mil_t]) * 1000000 * 1.0495)', "#,0", "ATR-equivalente do acucar produzido (kg). Premissa CONSECANA: acucar branco 1,0495 kg ATR/kg (CONAB generico; VHP 1,0453 e alternativa a confirmar). Exclusiva do nivel UF."))
        medidas.append(("ATR equivalente etanol (kg)", 'IF(SELECTEDVALUE(dim_territorio[nivel_territorial]) = "uf" && NOT ISBLANK(SUM(fato_industria[producao_etanol_anidro_mil_l])) && NOT ISBLANK(SUM(fato_industria[producao_etanol_hidratado_mil_l])), SUM(fato_industria[producao_etanol_anidro_mil_l]) * 1000 * 1.7651 + SUM(fato_industria[producao_etanol_hidratado_mil_l]) * 1000 * 1.6913)', "#,0", "ATR-equivalente do etanol produzido (kg), anidro (1,7651) e hidratado (1,6913) somados SEPARADAMENTE, nunca pelo total. Exclusiva do nivel UF."))
        medidas.append(("Share açúcar (ATR)", "VAR AtrAcucar = [ATR equivalente açúcar (kg)] VAR AtrEtanol = [ATR equivalente etanol (kg)] VAR AtrTotal = AtrAcucar + AtrEtanol RETURN IF(NOT ISBLANK(AtrAcucar) && NOT ISBLANK(AtrEtanol) && AtrTotal > 0, DIVIDE(AtrAcucar, AtrTotal))", "0.00%", "Fatia do acucar no ATR total (ATR acucar / ATR total). DIVIDE protegido; denominador 0/nulo retorna BLANK, nunca 0% nem 50/50. Exclusiva do nivel UF."))
        medidas.append(("Share etanol (ATR)", "VAR AtrAcucar = [ATR equivalente açúcar (kg)] VAR AtrEtanol = [ATR equivalente etanol (kg)] VAR AtrTotal = AtrAcucar + AtrEtanol RETURN IF(NOT ISBLANK(AtrAcucar) && NOT ISBLANK(AtrEtanol) && AtrTotal > 0, DIVIDE(AtrEtanol, AtrTotal))", "0.00%", "Fatia do etanol no ATR total (ATR etanol / ATR total). DIVIDE protegido; denominador 0/nulo retorna BLANK, nunca 0% nem 50/50. Exclusiva do nivel UF."))
        medidas.append(("Situação mix (UF/safra)", 'VAR Cana = SUM(fato_industria[cana_mil_t]) VAR Acucar = SUM(fato_industria[producao_acucar_mil_t]) VAR Etanol = SUM(fato_industria[producao_etanol_total_mil_l]) RETURN SWITCH(TRUE(), ISBLANK(Cana) || Cana = 0, "sem dado", ISBLANK(Acucar) || ISBLANK(Etanol), "sem dado", (Acucar = 0 || Etanol = 0), "mix real", "presente")', None, "Rotulo textual de cobertura: distingue 'sem dado' (cinza/hachura no visual) de 'mix real' (fatia zero legitima) e 'presente'. Medida textual, sem formatString numerico. Exclusiva do nivel UF."))
        return medidas
    if nome.startswith("fato_vendas"):
        nivel = "uf" if nome.endswith("_uf") else "municipio"
        label = "Vendas etanol UF (L)" if nivel == "uf" else "Vendas etanol municípios validados (L)"
        descricao = None if nivel == "uf" else "Vendas de etanol hidratado (L). A versao municipal so e confiavel dentro da PB (chave conferida)."
        return [(label, f'IF(SELECTEDVALUE(dim_territorio[nivel_territorial]) = "{nivel}", SUM({nome}[vendas_etanol_hidratado_l]))', "#,0", descricao)]
    return []


def _emitir_medida(medida, dax, formato, descricao):
    """Emite as linhas TMDL de uma medida.

    Emite '/// <descricao>' antes da medida quando descricao estiver presente e
    a linha 'formatString' apenas quando formato nao for None (medidas textuais,
    como 'Situação mix (UF/safra)', nao recebem formatString numerico).
    """
    linhas = []
    if descricao:
        linhas += [f"\t\t/// {descricao}"]
    linhas += [f"\t\tmeasure '{medida}' = {dax}"]
    if formato is not None:
        linhas += [f"\t\t\tformatString: {formato}"]
    linhas += [""]
    return linhas


def main():
    linhas = ["createOrReplace", ""]
    for nome in FATOS + ["dim_territorio", "dim_calendario", "dim_fonte"]:
        frame = pd.read_parquet(ROOT / "data/processed" / f"{nome}.parquet")
        if nome == "dim_territorio" and "tier" not in frame:
            frame["tier"] = pd.Series(dtype="string")
        linhas += [f"\ttable {nome}"]
        if nome == "dim_calendario":
            linhas += ["\t\tdataCategory: Time"]
        for coluna, dtype in frame.dtypes.items():
            tipo = "boolean" if pd.api.types.is_bool_dtype(dtype) else "dateTime" if pd.api.types.is_datetime64_any_dtype(dtype) else "int64" if pd.api.types.is_integer_dtype(dtype) else "double" if pd.api.types.is_float_dtype(dtype) else "string"
            linhas += [f"\t\tcolumn {coluna}", f"\t\t\tdataType: {tipo}", "\t\t\tsummarizeBy: none", f"\t\t\tsourceColumn: {coluna}"]
            if coluna == "data_referencia" and nome == "dim_calendario":
                linhas += ["\t\t\tisKey", "\t\t\tformatString: yyyy-MM-dd"]
            linhas += [""]
        if nome == "fato_producao":
            for medida, dax, formato, descricao in medidas_producao():
                linhas += _emitir_medida(medida, dax, formato, descricao)
        for medida, dax, formato, descricao in medidas_adicionais(nome):
            linhas += _emitir_medida(medida, dax, formato, descricao)
        url = f"{URL_BASE}/{nome}.parquet"
        m = f'Parquet.Document(Web.Contents("{url}"))'
        linhas += [f"\t\tpartition {nome} = m", "\t\t\tmode: import", "\t\t\tsource =", f'\t\t\t\t{m}', ""]
    for fato in FATOS:
        for dim, chave in [("dim_territorio", "territorio_id"), ("dim_calendario", "data_referencia"), ("dim_fonte", "fonte_id")]:
            # Preserva os identificadores das três relações já existentes da PAM.
            relacao = f"fato_{dim}" if fato == "fato_producao" else f"{fato}_{dim}"
            linhas += [f"\trelationship {relacao}", f"\t\tfromColumn: {fato}.{chave}", f"\t\ttoColumn: {dim}.{chave}", "\t\tfromCardinality: many", "\t\ttoCardinality: one", "\t\tcrossFilteringBehavior: oneDirection", ""]
    (ROOT / "powerbi/modelo.tmdl").write_text("\n".join(linhas), encoding="utf-8")
    # Correção incremental para PBIX já carregado: preserva tabelas e partições.
    correcao = ["createOrReplace", "\tref table fato_producao"]
    for medida, dax, formato, descricao in medidas_producao():
        correcao += _emitir_medida(medida, dax, formato, descricao)
    (ROOT / "powerbi/correcao-ausencias.tmdl").write_text("\n".join(correcao), encoding="utf-8")


if __name__ == "__main__":
    main()
