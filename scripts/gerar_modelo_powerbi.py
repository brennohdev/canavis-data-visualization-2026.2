"""Gera script TMDL importável no Power BI a partir do esquema da gold."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FATOS = ["fato_producao", "fato_industria", "fato_vendas_etanol_uf", "fato_vendas_etanol_municipio"]


def medidas_producao():
    """Mantém a mesma regra de completude das agregações da gold."""
    quantidade_completa = "IF(COUNTROWS(FILTER(fato_producao, ISBLANK(fato_producao[quantidade_produzida_t]))) = 0, SUM(fato_producao[quantidade_produzida_t]))"
    return [
        ("Produtividade", "IF(HASONEVALUE(dim_territorio[nivel_territorial]) && COUNTROWS(FILTER(fato_producao, ISBLANK(fato_producao[quantidade_produzida_t]) || ISBLANK(fato_producao[area_colhida_ha]))) = 0, DIVIDE(SUM(fato_producao[quantidade_produzida_t]), SUM(fato_producao[area_colhida_ha])))", "0.00"),
        ("Participação regional", f"VAR Nivel = SELECTEDVALUE(dim_territorio[nivel_territorial]) VAR Quantidade = {quantidade_completa} VAR Total = CALCULATE({quantidade_completa}, ALL(dim_territorio), dim_territorio[nivel_territorial] = Nivel) RETURN IF(NOT ISBLANK(Nivel) && NOT ISBLANK(Quantidade), DIVIDE(Quantidade, Total))", "0.00%"),
        ("Desvio vs seleção", "VAR Atual = [Produtividade] VAR Referencia = CALCULATE([Produtividade], ALLSELECTED(dim_territorio)) RETURN IF(NOT ISBLANK(Atual) && NOT ISBLANK(Referencia), DIVIDE(Atual - Referencia, Referencia))", "0.00%"),
        ("Desvio vs grupo", "VAR Tier = SELECTEDVALUE(dim_territorio[tier]) VAR Atual = [Produtividade] VAR Referencia = CALCULATE([Produtividade], ALLSELECTED(dim_territorio), KEEPFILTERS(dim_territorio[tier] = Tier)) RETURN IF(NOT ISBLANK(Tier) && NOT ISBLANK(Atual) && NOT ISBLANK(Referencia), DIVIDE(Atual - Referencia, Referencia))", "0.00%"),
    ]


def medidas_adicionais(nome):
    if nome == "fato_producao":
        return [("Tendência histórica (t por ha)", "IF(HASONEVALUE(dim_territorio[territorio_id]) && HASONEVALUE(dim_calendario[ano]), MAX(fato_producao[tendencia_t_ha]))", "0.00"),
                ("Oscilação histórica (t por ha)", "IF(HASONEVALUE(dim_territorio[territorio_id]) && HASONEVALUE(dim_calendario[ano]), MAX(fato_producao[oscilacao_t_ha]))", "0.00"),
                ("P Chow exploratório (2003-2023)", "IF(HASONEVALUE(dim_territorio[territorio_id]), MAX(fato_producao[p_chow]))", "0.000000")]
    if nome == "fato_industria":
        medidas = []
        for label, numerador, denominador in [
            ("Mix etanol açúcar (L por t)", "producao_etanol_total_mil_l", "producao_acucar_mil_t"),
            ("Intensidade açúcar (t por t)", "producao_acucar_mil_t", "cana_mil_t"),
        ]:
            dax = f'IF(SELECTEDVALUE(dim_territorio[nivel_territorial]) = "uf" && COUNTROWS(FILTER(fato_industria, ISBLANK(fato_industria[{numerador}]) || ISBLANK(fato_industria[{denominador}]))) = 0, DIVIDE(SUM(fato_industria[{numerador}]), SUM(fato_industria[{denominador}])))'
            medidas.append((label, dax, "0.0000"))
        medidas.append(("ATR ponderado (kg por t)", 'IF(SELECTEDVALUE(dim_territorio[nivel_territorial]) = "uf" && COUNTROWS(FILTER(fato_industria, ISBLANK(fato_industria[atr_kg_t]) || ISBLANK(fato_industria[cana_mil_t]))) = 0, DIVIDE(SUMX(fato_industria, fato_industria[atr_kg_t] * fato_industria[cana_mil_t]), SUM(fato_industria[cana_mil_t])))', "0.00"))
        return medidas
    if nome.startswith("fato_vendas"):
        nivel = "uf" if nome.endswith("_uf") else "municipio"
        label = "Vendas etanol UF (L)" if nivel == "uf" else "Vendas etanol municípios validados (L)"
        return [(label, f'IF(SELECTEDVALUE(dim_territorio[nivel_territorial]) = "{nivel}", SUM({nome}[vendas_etanol_hidratado_l]))', "#,0")]
    return []


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
            for medida, dax, formato in medidas_producao():
                linhas += [f"\t\tmeasure '{medida}' = {dax}", f"\t\t\tformatString: {formato}", ""]
        for medida, dax, formato in medidas_adicionais(nome):
            linhas += [f"\t\tmeasure '{medida}' = {dax}", f"\t\t\tformatString: {formato}", ""]
        arquivo = str(ROOT / "data/processed" / f"{nome}.parquet")
        m = f'Parquet.Document(File.Contents("{arquivo}"))'
        if nome == "dim_territorio":
            m = f'let Fonte = {m} in if Table.HasColumns(Fonte, "tier") then Fonte else Table.AddColumn(Fonte, "tier", each null, type text)'
        linhas += [f"\t\tpartition {nome} = m", "\t\t\tmode: import", "\t\t\tsource =", f'\t\t\t\t{m}', ""]
    for fato in FATOS:
        for dim, chave in [("dim_territorio", "territorio_id"), ("dim_calendario", "data_referencia"), ("dim_fonte", "fonte_id")]:
            # Preserva os identificadores das três relações já existentes da PAM.
            relacao = f"fato_{dim}" if fato == "fato_producao" else f"{fato}_{dim}"
            linhas += [f"\trelationship {relacao}", f"\t\tfromColumn: {fato}.{chave}", f"\t\ttoColumn: {dim}.{chave}", "\t\tfromCardinality: many", "\t\ttoCardinality: one", "\t\tcrossFilteringBehavior: oneDirection", ""]
    (ROOT / "powerbi/modelo.tmdl").write_text("\n".join(linhas), encoding="utf-8")
    # Correção incremental para PBIX já carregado: preserva tabelas e partições.
    correcao = ["createOrReplace", "\tref table fato_producao"]
    for medida, dax, formato in medidas_producao():
        correcao += [f"\t\tmeasure '{medida}' = {dax}", f"\t\t\tformatString: {formato}", ""]
    (ROOT / "powerbi/correcao-ausencias.tmdl").write_text("\n".join(correcao), encoding="utf-8")


if __name__ == "__main__":
    main()
