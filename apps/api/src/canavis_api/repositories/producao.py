"""Consultas DuckDB sobre os parquet da camada gold (somente leitura)."""

from dataclasses import dataclass
from pathlib import Path

import duckdb

ARQUIVOS_OBRIGATORIOS = ("fato_producao_uf.parquet", "dim_territorio.parquet")

# A dim_territorio não tem sigla; o código IBGE da UF (cod_uf) é a chave de ligação.
SIGLA_PARA_COD_UF: dict[str, str] = {
    "RO": "11", "AC": "12", "AM": "13", "RR": "14", "PA": "15", "AP": "16", "TO": "17",
    "MA": "21", "PI": "22", "CE": "23", "RN": "24", "PB": "25", "PE": "26", "AL": "27",
    "SE": "28", "BA": "29", "MG": "31", "ES": "32", "RJ": "33", "SP": "35",
    "PR": "41", "SC": "42", "RS": "43", "MS": "50", "MT": "51", "GO": "52", "DF": "53",
}  # fmt: skip

ANO_MIN, ANO_MAX = 2003, 2023

_SQL = """
SELECT f.territorio_id, d.nome_territorio, f.ano_referencia,
       f.produtividade_t_ha, f.quantidade_produzida_t, f.area_colhida_ha
FROM read_parquet(?) AS f
JOIN read_parquet(?) AS d ON d.territorio_id = f.territorio_id
WHERE d.nivel_territorial = 'uf' AND d.cod_uf = ? AND f.ano_referencia = ?
"""


class DadosIndisponiveis(Exception):
    """Os parquet da gold não foram encontrados em CANAVIS_DATA_DIR."""


@dataclass(frozen=True)
class ProducaoUF:
    sigla: str
    territorio_id: str
    nome: str
    ano: int
    produtividade_t_ha: float | None
    quantidade_produzida_t: float | None
    area_colhida_ha: float | None


def dados_disponiveis(data_dir: Path) -> bool:
    return all((data_dir / nome).is_file() for nome in ARQUIVOS_OBRIGATORIOS)


def buscar_producao_uf(data_dir: Path, sigla: str, ano: int) -> ProducaoUF | None:
    """Devolve a produção da UF no ano, ou None se a sigla ou o ano não existirem."""
    cod_uf = SIGLA_PARA_COD_UF.get(sigla)
    if cod_uf is None:
        return None
    if not dados_disponiveis(data_dir):
        raise DadosIndisponiveis(str(data_dir))
    fato, dim = (str(data_dir / nome) for nome in ARQUIVOS_OBRIGATORIOS)
    con = duckdb.connect(":memory:")
    try:
        linha = con.execute(_SQL, [fato, dim, cod_uf, ano]).fetchone()
    finally:
        con.close()
    if linha is None:
        return None
    return ProducaoUF(sigla, linha[0], linha[1], int(linha[2]), linha[3], linha[4], linha[5])
