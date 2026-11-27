from __future__ import annotations

import json
from datetime import timedelta

import pandas as pd
import pytest

from canavis.sources.intl import cli, job

FONTES = ["bcb_sgs", "fred", "yahoo"]


def _resposta(fixture_bytes, quebrar: set[str] | None = None):
    quebrar = quebrar or set()

    def responder(url: str) -> bytes:
        if "stlouisfed" in url:
            if "fred" in quebrar:
                raise TimeoutError("tempo esgotado")
            return fixture_bytes("fred.csv")
        if "yahoo" in url:
            return fixture_bytes("yahoo.json")
        return fixture_bytes("bcb_sgs.json")

    return responder


@pytest.fixture
def pastas(tmp_path):
    return tmp_path / "external", tmp_path / "raw"


def _refresh(pastas, cliente, fontes=None, tentativas=1):
    saida, bruto = pastas
    return job.refresh(
        fontes=fontes or FONTES,
        saida=saida,
        raiz_bruto=bruto,
        client=cliente,
        tentativas=tentativas,
        pausa=lambda segundos: None,
    )


def _preparar_cli(monkeypatch, bruto, cliente):
    original_refresh = job.refresh
    original_reprocess = job.reprocess
    monkeypatch.setattr(
        job,
        "refresh",
        lambda **kw: original_refresh(
            **kw, raiz_bruto=bruto, client=cliente, pausa=lambda segundos: None
        ),
    )
    monkeypatch.setattr(job, "reprocess", lambda **kw: original_reprocess(**kw, raiz_bruto=bruto))


def test_refresh_grava_snapshot_dimensao_e_manifesto(pastas, cliente_falso, fixture_bytes):
    manifesto = _refresh(pastas, cliente_falso(_resposta(fixture_bytes)))
    saida, _ = pastas
    for fonte_id in FONTES:
        assert (saida / f"{fonte_id}.parquet").exists()
        entrada = manifesto["fontes"][fonte_id]
        assert entrada["status"] == "ok"
        assert entrada["erro"] is None
        assert len(entrada["sha256"]) == 64
        assert entrada["linhas"] > 0
    dimensao = pd.read_parquet(saida / "dim_fonte_intl.parquet")
    assert "yahoo" in set(dimensao["fonte_id"])
    assert bool(dimensao.set_index("fonte_id").loc["yahoo", "nao_oficial"]) is True
    em_disco = json.loads((saida / "manifest.json").read_text(encoding="utf-8"))
    assert em_disco["fontes"]["fred"]["sha256"] == manifesto["fontes"]["fred"]["sha256"]


def test_falha_de_uma_fonte_mantem_snapshot_e_marca_falha(pastas, cliente_falso, fixture_bytes):
    primeira = _refresh(pastas, cliente_falso(_resposta(fixture_bytes)))
    saida, _ = pastas
    antes = (saida / "fred.parquet").read_bytes()
    segunda = _refresh(pastas, cliente_falso(_resposta(fixture_bytes, {"fred"})))
    assert segunda["fontes"]["fred"]["status"] == "falha"
    assert "TimeoutError" in segunda["fontes"]["fred"]["erro"]
    assert segunda["fontes"]["fred"]["sha256"] == primeira["fontes"]["fred"]["sha256"]
    assert (saida / "fred.parquet").read_bytes() == antes
    assert segunda["fontes"]["bcb_sgs"]["status"] == "ok"
    assert segunda["fontes"]["yahoo"]["status"] == "ok"


def test_fonte_que_nunca_funcionou_fica_no_manifesto_com_falha(
    pastas, cliente_falso, fixture_bytes
):
    manifesto = _refresh(pastas, cliente_falso(_resposta(fixture_bytes, {"fred"})))
    entrada = manifesto["fontes"]["fred"]
    assert entrada["status"] == "falha"
    assert entrada["arquivo"] is None
    assert entrada["sha256"] is None
    assert entrada["erro"]
    saida, _ = pastas
    assert "fred" in set(pd.read_parquet(saida / "dim_fonte_intl.parquet")["fonte_id"])


def _arquivos(saida):
    return {p.name: p.read_bytes() for p in sorted(saida.iterdir())}


def test_refresh_sem_mudanca_nos_dados_nao_altera_nenhum_arquivo(
    pastas, cliente_falso, fixture_bytes, monkeypatch
):
    _refresh(pastas, cliente_falso(_resposta(fixture_bytes)))
    saida, _ = pastas
    antes = _arquivos(saida)
    agora = job.datetime.now
    monkeypatch.setattr(
        job,
        "datetime",
        type("D", (), {"now": staticmethod(lambda tz=None: agora(tz) + timedelta(days=1)),
                       "strptime": job.datetime.strptime}),
    )
    segunda = _refresh(pastas, cliente_falso(_resposta(fixture_bytes)))
    assert _arquivos(saida) == antes
    assert segunda["fontes"]["bcb_sgs"]["status"] == "ok"


def test_refresh_com_dado_novo_regrava_so_a_fonte_que_mudou(pastas, cliente_falso, fixture_bytes):
    _refresh(pastas, cliente_falso(_resposta(fixture_bytes)))
    saida, _ = pastas
    antes = _arquivos(saida)
    novo = fixture_bytes("bcb_sgs.json").replace(b"4.8916", b"4.9999")

    def responder(url: str) -> bytes:
        return novo if "bcb" in url else _resposta(fixture_bytes)(url)

    _refresh(pastas, cliente_falso(responder))
    depois = _arquivos(saida)
    assert depois["bcb_sgs.parquet"] != antes["bcb_sgs.parquet"]
    assert depois["fred.parquet"] == antes["fred.parquet"]
    assert depois["yahoo.parquet"] == antes["yahoo.parquet"]
    assert depois["manifest.json"] != antes["manifest.json"]


def test_tentativas_repetem_a_fonte_que_falha(pastas, cliente_falso, fixture_bytes):
    cliente = cliente_falso(_resposta(fixture_bytes, {"fred"}))
    _refresh(pastas, cliente, fontes=["fred"], tentativas=3)
    assert len([u for u in cliente.urls if "stlouisfed" in u]) == 3


def test_reprocess_reproduz_o_mesmo_sha256_do_refresh(pastas, cliente_falso, fixture_bytes):
    manifesto = _refresh(pastas, cliente_falso(_resposta(fixture_bytes)))
    saida, bruto = pastas
    comparacao = job.reprocess(fontes=FONTES, saida=saida, raiz_bruto=bruto)
    for fonte_id in FONTES:
        assert comparacao[fonte_id]["igual"] is True
        assert comparacao[fonte_id]["novo"] == manifesto["fontes"][fonte_id]["sha256"]


def test_reprocess_de_fonte_sem_snapshot_ok_nao_inventa_dado(pastas, cliente_falso, fixture_bytes):
    _refresh(pastas, cliente_falso(_resposta(fixture_bytes, {"fred"})))
    saida, bruto = pastas
    comparacao = job.reprocess(fontes=["fred"], saida=saida, raiz_bruto=bruto)
    assert comparacao["fred"]["novo"] is None
    assert not (saida / "fred.parquet").exists()


def test_fonte_desconhecida_e_rejeitada(pastas):
    with pytest.raises(KeyError):
        _refresh(pastas, None, fontes=["inexistente"])


def test_cli_refresh_e_reprocess(pastas, cliente_falso, fixture_bytes, monkeypatch, capsys):
    saida, bruto = pastas
    _preparar_cli(monkeypatch, bruto, cliente_falso(_resposta(fixture_bytes)))
    argumentos = ["--fonte", "bcb_sgs", "--fonte", "fred", "--saida", str(saida)]
    assert cli.main(["refresh", *argumentos, "--tentativas", "1"]) == 0
    assert "status=ok" in capsys.readouterr().out
    assert cli.main(["reprocess", *argumentos]) == 0
    assert "igual" in capsys.readouterr().out


def test_cli_retorna_1_quando_todas_as_fontes_falham(
    pastas, cliente_falso, fixture_bytes, monkeypatch
):
    saida, bruto = pastas
    _preparar_cli(monkeypatch, bruto, cliente_falso(_resposta(fixture_bytes, {"fred"})))
    argumentos = ["--fonte", "fred", "--saida", str(saida), "--tentativas", "1"]
    assert cli.main(["refresh", *argumentos]) == 1
