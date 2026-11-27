from pathlib import Path

import pandas as pd

from canavis import storage
from canavis.domain.cobertura import (
    SITUACOES,
    construir_matriz_cobertura,
    resumo_pb,
    ultimo_ano_por_fonte,
)

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
SAIDA_MD = ROOT / "docs" / "entrega-etapa3" / "matriz-cobertura.md"
ANO_PB = 2023


def carregar_matriz() -> pd.DataFrame:
    fatos_pam = pd.concat(
        [
            pd.read_parquet(PROCESSED / f"fato_producao_{nivel}.parquet")
            for nivel in ("uf", "microrregiao", "municipio")
        ],
        ignore_index=True,
    )
    return construir_matriz_cobertura(
        fatos_pam,
        pd.read_parquet(PROCESSED / "fato_industria.parquet"),
        pd.read_parquet(PROCESSED / "fato_vendas_etanol_uf.parquet"),
        pd.read_parquet(PROCESSED / "dim_territorio.parquet"),
    )


def renderizar_markdown(matriz: pd.DataFrame) -> str:
    fontes = pd.read_parquet(PROCESSED / "dim_fonte.parquet").set_index("fonte_id")["fonte"]
    ultimos = ultimo_ano_por_fonte(matriz)
    linhas = [
        "# Matriz de cobertura",
        "",
        "> Gerado por `scripts/gerar_matriz_cobertura.py`. Não editar à mão. "
        "A tabela completa está em `data/processed/matriz_cobertura.parquet`.",
        "",
        "## Último ano com dado presente por fonte",
        "",
        "| fonte_id | Fonte | Último ano |",
        "|---|---|---|",
    ]
    for fonte_id, ano in ultimos.items():
        linhas.append(f"| `{fonte_id}` | {fontes.get(fonte_id, fonte_id)} | {ano} |")
    linhas += [
        "",
        "## Linhas por fonte, nível e situação",
        "",
        "| fonte_id | nível | " + " | ".join(SITUACOES) + " |",
        "|---|---|" + "---|" * len(SITUACOES),
    ]
    contagem = matriz.groupby(["fonte_id", "nivel_territorial", "situacao"]).size()
    for (fonte_id, nivel), _ in matriz.groupby(["fonte_id", "nivel_territorial"]):
        valores = [str(int(contagem.get((fonte_id, nivel, s), 0))) for s in SITUACOES]
        linhas.append(f"| `{fonte_id}` | {nivel} | " + " | ".join(valores) + " |")
    resumo = resumo_pb(matriz, ANO_PB)
    linhas += [
        "",
        f"## Municípios da Paraíba em {ANO_PB} (PAM)",
        "",
        "| Situação | Municípios |",
        "|---|---|",
    ]
    linhas += [f"| {situacao} | {resumo[situacao]} |" for situacao in SITUACOES]
    linhas += [
        "",
        "`sem_producao` é zero registrado pela fonte. `suprimido` é valor omitido por sigilo. "
        "`sem_registro` é combinação sem linha na fonte e nunca vira zero.",
        "",
    ]
    return "\n".join(linhas)


def main() -> None:
    matriz = carregar_matriz()
    destino = storage.write(matriz, PROCESSED, "matriz_cobertura")
    SAIDA_MD.write_text(renderizar_markdown(matriz), encoding="utf-8")
    print(f"{destino.relative_to(ROOT)} | {len(matriz)} linhas")
    print(SAIDA_MD.relative_to(ROOT))


if __name__ == "__main__":
    main()
