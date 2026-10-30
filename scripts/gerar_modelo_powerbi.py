"""Gera script TMDL importável no Power BI a partir do esquema da gold."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    linhas = ["createOrReplace", ""]
    for nome in ["fato_producao", "dim_territorio", "dim_calendario", "dim_fonte"]:
        frame = pd.read_parquet(ROOT / "data/processed" / f"{nome}.parquet")
        if nome == "dim_territorio" and "tier" not in frame:
            frame["tier"] = pd.Series(dtype="string")
        linhas += [f"\ttable {nome}"]
        if nome == "dim_calendario":
            linhas += ["\t\tdataCategory: Time"]
        for coluna, dtype in frame.dtypes.items():
            tipo = "dateTime" if "datetime" in str(dtype) else "int64" if "int" in str(dtype).lower() else "double" if "float" in str(dtype).lower() else "string"
            linhas += [f"\t\tcolumn {coluna}", f"\t\t\tdataType: {tipo}", "\t\t\tsummarizeBy: none", f"\t\t\tsourceColumn: {coluna}"]
            if coluna == "data_referencia" and nome == "dim_calendario":
                linhas += ["\t\t\tisKey", "\t\t\tformatString: yyyy-MM-dd"]
            linhas += [""]
        if nome == "fato_producao":
            for medida, dax, formato in [
                ("Produtividade", "IF(HASONEVALUE(dim_territorio[nivel_territorial]), DIVIDE(SUM(fato_producao[quantidade_produzida_t]), SUM(fato_producao[area_colhida_ha])))", "0.00"),
                ("Participação regional", "VAR Nivel = SELECTEDVALUE(dim_territorio[nivel_territorial]) VAR Total = CALCULATE(SUM(fato_producao[quantidade_produzida_t]), ALL(dim_territorio), dim_territorio[nivel_territorial] = Nivel) RETURN IF(NOT ISBLANK(Nivel), DIVIDE(SUM(fato_producao[quantidade_produzida_t]), Total))", "0.00%"),
                ("Desvio vs seleção", "VAR Referencia = CALCULATE([Produtividade], ALLSELECTED(dim_territorio)) RETURN DIVIDE([Produtividade] - Referencia, Referencia)", "0.00%"),
                ("Desvio vs grupo", "VAR Tier = SELECTEDVALUE(dim_territorio[tier]) VAR Referencia = CALCULATE([Produtividade], ALLSELECTED(dim_territorio), KEEPFILTERS(dim_territorio[tier] = Tier)) RETURN IF(NOT ISBLANK(Tier), DIVIDE([Produtividade] - Referencia, Referencia))", "0.00%"),
            ]:
                linhas += [f"\t\tmeasure '{medida}' = {dax}", f"\t\t\tformatString: {formato}", ""]
        arquivo = str(ROOT / "data/processed" / f"{nome}.parquet")
        m = f'Parquet.Document(File.Contents("{arquivo}"))'
        if nome == "dim_territorio":
            m = f'let Fonte = {m} in if Table.HasColumns(Fonte, "tier") then Fonte else Table.AddColumn(Fonte, "tier", each null, type text)'
        linhas += [f"\t\tpartition {nome} = m", "\t\t\tmode: import", "\t\t\tsource =", f'\t\t\t\t{m}', ""]
    for dim, chave in [("dim_territorio", "territorio_id"), ("dim_calendario", "data_referencia"), ("dim_fonte", "fonte_id")]:
        linhas += [f"\trelationship fato_{dim}", f"\t\tfromColumn: fato_producao.{chave}", f"\t\ttoColumn: {dim}.{chave}", "\t\tcrossFilteringBehavior: oneDirection", ""]
    (ROOT / "powerbi/modelo.tmdl").write_text("\n".join(linhas), encoding="utf-8")


if __name__ == "__main__":
    main()
