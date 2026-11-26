from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from canavis_api.main import create_app
from canavis_api.settings import get_settings

RAIZ = Path(__file__).resolve().parents[3]


@pytest.fixture
def cliente(monkeypatch):
    def _criar(data_dir: Path = RAIZ / "data" / "processed", static_dir: Path | None = None):
        monkeypatch.setenv("CANAVIS_DATA_DIR", str(data_dir))
        monkeypatch.setenv("CANAVIS_STATIC_DIR", str(static_dir or data_dir / "sem-static"))
        get_settings.cache_clear()
        return TestClient(create_app())

    yield _criar
    get_settings.cache_clear()


def test_saude_ok(cliente):
    r = cliente().get("/api/v1/saude")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "dados": True}


def test_producao_pb_2021(cliente):
    r = cliente().get("/api/v1/uf/PB/producao", params={"ano": 2021})
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["territorio_id"] == "uf:25"
    assert corpo["nome"] == "Paraíba"
    assert corpo["produtividade_t_ha"] == pytest.approx(55.653875)
    assert corpo["quantidade_produzida_t"] == 5630113.0


def test_sigla_desconhecida_404(cliente):
    assert cliente().get("/api/v1/uf/XX/producao?ano=2021").status_code == 404


def test_ano_fora_do_intervalo_404(cliente):
    assert cliente().get("/api/v1/uf/PB/producao?ano=1999").status_code == 404


def test_ano_invalido_422(cliente):
    assert cliente().get("/api/v1/uf/PB/producao?ano=abc").status_code == 422


def test_injecao_de_sql_na_sigla_404(cliente):
    r = cliente().get("/api/v1/uf/PB' OR '1'='1/producao?ano=2021")
    assert r.status_code == 404
    r = cliente().get("/api/v1/uf/{s}/producao".format(s="PB%27%20OR%20%271%27=%271"))
    assert r.status_code == 404


def test_dados_ausentes_503(cliente, tmp_path):
    c = cliente(data_dir=tmp_path)
    assert c.get("/api/v1/saude").status_code == 503
    r = c.get("/api/v1/uf/PB/producao?ano=2021")
    assert r.status_code == 503
    assert "indisponíveis" in r.json()["detail"]


def test_fallback_spa(cliente, tmp_path):
    (tmp_path / "index.html").write_text("<html>spa</html>")
    c = cliente(static_dir=tmp_path)
    r = c.get("/uf/PB?ano=2021")
    assert r.status_code == 200 and "spa" in r.text
    r = c.get("/api/v1/inexistente")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/json")
