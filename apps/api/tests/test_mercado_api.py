import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from canavis_api.composicao import create_app
from canavis_api.settings import Settings

RAIZ = Path(__file__).resolve().parents[3]
EXTERNO = RAIZ / "data" / "external"
ENDPOINTS = ("cambio", "acucar", "paises", "cot")


@pytest.fixture
def cliente():
    def _criar(external_dir: Path = EXTERNO):
        settings = Settings(
            data_dir=RAIZ / "data" / "processed",
            static_dir=external_dir / "sem-static",
            external_dir=external_dir,
        )
        return TestClient(create_app(settings))

    return _criar


@pytest.fixture
def copia(tmp_path):
    destino = tmp_path / "external"
    shutil.copytree(EXTERNO, destino)
    return destino


def _marcar_falha(pasta: Path, fonte_id: str, apagar: bool) -> None:
    caminho = pasta / "manifest.json"
    manifesto = json.loads(caminho.read_text(encoding="utf-8"))
    manifesto["fontes"][fonte_id]["status"] = "falha"
    manifesto["fontes"][fonte_id]["erro"] = "ReadTimeout simulado"
    caminho.write_text(json.dumps(manifesto), encoding="utf-8")
    if apagar:
        (pasta / f"{fonte_id}.parquet").unlink()


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_endpoints_respondem_com_fontes_e_series(cliente, endpoint):
    r = cliente().get(f"/api/v1/mercado/{endpoint}")
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["fontes"]
    assert corpo["series"]
    assert all(f["origem"] == "snapshot" for f in corpo["fontes"])
    assert all(f["licenca"] and f["atribuicao"] for f in corpo["fontes"])
    assert any(s["pontos"] for s in corpo["series"])


def test_cambio_traz_status_ok_e_licenca(cliente):
    corpo = cliente().get("/api/v1/mercado/cambio").json()
    fonte = corpo["fontes"][0]
    assert fonte["fonte_id"] == "bcb_sgs"
    assert fonte["status"] == "ok"
    assert corpo["series"][0]["unidade"] == "BRL/USD"


def test_yahoo_e_marcado_nao_oficial(cliente):
    corpo = cliente().get("/api/v1/mercado/acucar").json()
    por_id = {f["fonte_id"]: f for f in corpo["fontes"]}
    assert por_id["yahoo"]["nao_oficial"] is True
    assert por_id["fred"]["nao_oficial"] is False


def test_desde_corta_a_serie(cliente):
    corpo = cliente().get("/api/v1/mercado/cambio", params={"desde": "2025-01-01"}).json()
    assert corpo["series"][0]["pontos"][0]["data"] >= "2025-01-01"


def test_agregacao_safra_gera_um_ponto_por_safra(cliente):
    corpo = cliente().get("/api/v1/mercado/cambio", params={"agregacao": "safra"}).json()
    datas = [p["data"] for p in corpo["series"][0]["pontos"]]
    assert datas[0] == "1999-04-01"
    assert all(d.endswith("-04-01") for d in datas)
    assert len(datas) < 40


def test_agregacao_mensal_usa_dia_um(cliente):
    corpo = cliente().get("/api/v1/mercado/cambio", params={"agregacao": "mensal"}).json()
    assert all(p["data"].endswith("-01") for p in corpo["series"][0]["pontos"])


def test_agregacao_invalida_422(cliente):
    assert cliente().get("/api/v1/mercado/cambio?agregacao=anual").status_code == 422


def test_pais_filtra_e_pais_invalido_422(cliente):
    c = cliente()
    corpo = c.get("/api/v1/mercado/paises", params={"pais": "in"}).json()
    assert corpo["series"]
    assert all(s["serie_id"].startswith("psd_in_") for s in corpo["series"])
    r = c.get("/api/v1/mercado/paises", params={"pais": "xx"})
    assert r.status_code == 422
    assert "pais" in r.json()["detail"]


def test_fonte_com_falha_e_parquet_apagado_responde_200(cliente, copia):
    _marcar_falha(copia, "cftc", apagar=True)
    c = cliente(copia)
    r = c.get("/api/v1/mercado/cot")
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["fontes"][0]["status"] == "falha"
    assert corpo["fontes"][0]["erro"] == "ReadTimeout simulado"
    assert all(s["pontos"] == [] for s in corpo["series"])
    assert c.get("/api/v1/uf/PB/producao?ano=2021").status_code == 200
    assert c.get("/api/v1/saude").status_code == 200


def test_fred_em_falha_cai_para_banco_mundial(cliente, copia):
    _marcar_falha(copia, "fred", apagar=True)
    c = cliente(copia)
    r = c.get("/api/v1/mercado/acucar")
    assert r.status_code == 200
    corpo = r.json()
    assert [s["serie_id"] for s in corpo["series"]] == ["acucar_ny11_fechamento", "acucar_mundo_wb"]
    assert corpo["series"][1]["pontos"]
    assert corpo["observacoes"]
    por_id = {f["fonte_id"]: f for f in corpo["fontes"]}
    assert por_id["fred"]["status"] == "falha"
    assert por_id["yahoo"]["status"] == "ok"


def test_falha_com_snapshot_anterior_mantem_pontos(cliente, copia):
    _marcar_falha(copia, "bcb_sgs", apagar=False)
    corpo = cliente(copia).get("/api/v1/mercado/cambio").json()
    assert corpo["fontes"][0]["status"] == "falha"
    assert corpo["series"][0]["pontos"]


def test_sem_manifesto_503_e_pam_intacta(cliente, tmp_path):
    c = cliente(tmp_path)
    for endpoint in ENDPOINTS:
        r = c.get(f"/api/v1/mercado/{endpoint}")
        assert r.status_code == 503
        assert "detail" in r.json()
    assert c.get("/api/v1/uf/PB/producao?ano=2021").status_code == 200
    assert c.get("/api/v1/saude").status_code == 200
