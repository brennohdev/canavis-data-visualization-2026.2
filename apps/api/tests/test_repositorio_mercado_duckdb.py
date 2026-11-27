import json
from datetime import date

import pandas as pd
import pytest

from canavis_api.dominio.erros import MercadoIndisponivel
from canavis_api.repositorios.mercado_duckdb import MercadoDuckDB


def _quadro() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "serie_id": ["cambio_usd_brl"] * 3 + ["outra_serie"],
            "data": pd.to_datetime(["2024-01-02", "2024-01-03", "2024-02-01", "2024-01-02"]),
            "valor": [4.9, 4.95, 5.0, 1.0],
            "unidade": ["BRL/USD"] * 4,
            "fonte_id": ["bcb_sgs"] * 4,
        }
    )


def _manifesto(tmp_path, entrada: dict) -> None:
    (tmp_path / "manifest.json").write_text(
        json.dumps({"versao_manifesto": 1, "fontes": {"bcb_sgs": entrada}}), encoding="utf-8"
    )


@pytest.fixture
def pasta(tmp_path):
    _quadro().to_parquet(tmp_path / "bcb_sgs.parquet")
    pd.DataFrame(
        {
            "fonte_id": ["bcb_sgs"],
            "fonte": ["Banco Central"],
            "url": ["https://exemplo"],
            "periodicidade": ["diaria"],
            "licenca": ["aberta"],
            "atribuicao": ["BCB"],
            "nao_oficial": [False],
        }
    ).to_parquet(tmp_path / "dim_fonte_intl.parquet")
    _manifesto(
        tmp_path,
        {
            "arquivo": "bcb_sgs.parquet",
            "status": "ok",
            "erro": None,
            "coletado_em": "2024-02-11T10:00:00Z",
            "periodo_fim": "2024-02-01",
        },
    )
    return tmp_path


def test_disponivel_depende_do_manifesto(pasta, tmp_path_factory):
    assert MercadoDuckDB(pasta).disponivel()
    assert not MercadoDuckDB(tmp_path_factory.mktemp("vazia")).disponivel()


def test_pontos_so_das_series_pedidas(pasta):
    pontos = MercadoDuckDB(pasta).pontos(("cambio_usd_brl",), None, None)
    assert [p.valor for p in pontos] == [4.9, 4.95, 5.0]
    assert pontos[0].data == date(2024, 1, 2)
    assert pontos[0].unidade == "BRL/USD"


def test_pontos_filtra_por_periodo(pasta):
    pontos = MercadoDuckDB(pasta).pontos(("cambio_usd_brl",), date(2024, 1, 3), date(2024, 1, 31))
    assert [p.valor for p in pontos] == [4.95]


def test_serie_fora_da_lista_branca_e_ignorada(pasta):
    assert MercadoDuckDB(pasta).pontos(("outra_serie", "' OR 1=1 --"), None, None) == []


def test_fonte_ok_traz_licenca_e_defasagem(pasta):
    fonte = MercadoDuckDB(pasta).fontes(("bcb_sgs",))[0]
    assert (fonte.status, fonte.origem, fonte.nome) == ("ok", "snapshot", "Banco Central")
    assert fonte.licenca == "aberta"
    assert fonte.atribuicao == "BCB"
    assert fonte.defasagem_dias == 10


def test_fonte_fora_do_manifesto_e_ausente(pasta):
    fonte = MercadoDuckDB(pasta).fontes(("cftc",))[0]
    assert fonte.status == "ausente"
    assert fonte.nome == "cftc"


def test_parquet_apagado_vira_ausente_e_sem_pontos(pasta):
    (pasta / "bcb_sgs.parquet").unlink()
    repo = MercadoDuckDB(pasta)
    assert repo.fontes(("bcb_sgs",))[0].status == "ausente"
    assert repo.pontos(("cambio_usd_brl",), None, None) == []


def test_falha_mantem_pontos_do_snapshot_anterior(pasta):
    _manifesto(
        pasta,
        {"arquivo": "bcb_sgs.parquet", "status": "falha", "erro": "ReadTimeout"},
    )
    repo = MercadoDuckDB(pasta)
    fonte = repo.fontes(("bcb_sgs",))[0]
    assert (fonte.status, fonte.erro) == ("falha", "ReadTimeout")
    assert len(repo.pontos(("cambio_usd_brl",), None, None)) == 3


def test_manifesto_corrompido_e_indisponivel(pasta):
    (pasta / "manifest.json").write_text("{nao e json", encoding="utf-8")
    with pytest.raises(MercadoIndisponivel):
        MercadoDuckDB(pasta).fontes(("bcb_sgs",))
