import logging
from pathlib import Path

import duckdb

from canavis_api.dominio.erros import DadosIndisponiveis
from canavis_api.dominio.producao import ProducaoUF
from canavis_api.dominio.territorio import Uf

ARQUIVOS_OBRIGATORIOS = ("fato_producao_uf.parquet", "dim_territorio.parquet")

_SQL = """
SELECT f.territorio_id, d.nome_territorio, f.ano_referencia,
       f.produtividade_t_ha, f.quantidade_produzida_t, f.area_colhida_ha
FROM read_parquet(?) AS f
JOIN read_parquet(?) AS d ON d.territorio_id = f.territorio_id
WHERE d.nivel_territorial = 'uf' AND d.cod_uf = ? AND f.ano_referencia = ?
"""

_log = logging.getLogger(__name__)


class ProducaoDuckDB:
    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir

    def disponivel(self) -> bool:
        return all((self._data_dir / nome).is_file() for nome in ARQUIVOS_OBRIGATORIOS)

    def buscar_uf(self, uf: Uf, ano: int) -> ProducaoUF | None:
        if not self.disponivel():
            raise DadosIndisponiveis()
        fato, dim = (str(self._data_dir / nome) for nome in ARQUIVOS_OBRIGATORIOS)
        con = duckdb.connect(":memory:")
        try:
            linha = con.execute(_SQL, [fato, dim, uf.cod_ibge, ano]).fetchone()
        except duckdb.Error as erro:
            _log.warning("Falha ao ler os parquet em %s", self._data_dir)
            raise DadosIndisponiveis() from erro
        finally:
            con.close()
        if linha is None:
            return None
        return ProducaoUF(uf.sigla, linha[0], linha[1], int(linha[2]), linha[3], linha[4], linha[5])
