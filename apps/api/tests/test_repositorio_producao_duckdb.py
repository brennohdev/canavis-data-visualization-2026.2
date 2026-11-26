from pathlib import Path

import pytest

from canavis_api.dominio.erros import DadosIndisponiveis
from canavis_api.dominio.territorio import Uf
from canavis_api.repositorios.producao_duckdb import ARQUIVOS_OBRIGATORIOS, ProducaoDuckDB

DADOS = Path(__file__).resolve().parents[3] / "data" / "processed"
PB = Uf("PB", "25")


def test_pb_2021():
    producao = ProducaoDuckDB(DADOS).buscar_uf(PB, 2021)
    assert producao is not None
    assert producao.produtividade_t_ha == pytest.approx(55.653875)
    assert producao.quantidade_produzida_t == 5630113.0


def test_ano_inexistente_devolve_none():
    assert ProducaoDuckDB(DADOS).buscar_uf(PB, 1999) is None


def test_sem_arquivos(tmp_path):
    repositorio = ProducaoDuckDB(tmp_path)
    assert repositorio.disponivel() is False
    with pytest.raises(DadosIndisponiveis):
        repositorio.buscar_uf(PB, 2021)


def test_parquet_corrompido(tmp_path):
    for nome in ARQUIVOS_OBRIGATORIOS:
        (tmp_path / nome).write_text("lixo")
    with pytest.raises(DadosIndisponiveis):
        ProducaoDuckDB(tmp_path).buscar_uf(PB, 2021)
