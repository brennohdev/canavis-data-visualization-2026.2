import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest
import requests
from fastapi.testclient import TestClient

from canavis_api.composicao import create_app
from canavis_api.dominio.mercado import FonteMercado, PontoSerie
from canavis_api.repositorios import mercado_ao_vivo
from canavis_api.repositorios.mercado_ao_vivo import (
    ClienteHttpCurto,
    Coleta,
    MercadoAoVivo,
    criar_fontes_ao_vivo,
)
from canavis_api.settings import Settings

RAIZ = Path(__file__).resolve().parents[3]
EXTERNO = RAIZ / "data" / "external"
FIXTURES = RAIZ / "tests" / "fixtures" / "intl"
HOJE = date.today()
REGISTROS_BCB = [
    {"data": (HOJE - timedelta(days=2)).strftime("%d/%m/%Y"), "valor": "5.10"},
    {"data": HOJE.strftime("%d/%m/%Y"), "valor": "5.20"},
]
INICIO = datetime(2026, 12, 1, 12, 0, tzinfo=timezone.utc)


class Relogio:
    def __init__(self):
        self.agora = INICIO

    def __call__(self):
        return self.agora

    def avancar(self, **kwargs):
        self.agora += timedelta(**kwargs)


class BaseFalsa:
    def __init__(self):
        self.pontos_base = [
            PontoSerie("cambio_usd_brl", "bcb_sgs", "BRL/USD", date(2026, 11, 20), 5.0),
            PontoSerie("cambio_usd_brl", "bcb_sgs", "BRL/USD", date(2026, 11, 30), 5.1),
        ]

    def disponivel(self):
        return True

    def fontes(self, fonte_ids):
        return tuple(
            FonteMercado(
                i,
                i,
                "ok",
                "snapshot",
                "2026-11-27T02:17:49Z",
                1,
                "l",
                "a",
                "u",
                False,
                None,
                "2026-11-26",
            )
            for i in fonte_ids
        )

    def pontos(self, serie_ids, desde, ate):
        return [p for p in self.pontos_base if p.serie_id in serie_ids]


class Coletor:
    def __init__(self, erro=None):
        self.chamadas = 0
        self.erro = erro

    def __call__(self, agora):
        self.chamadas += 1
        if self.erro:
            raise self.erro
        pontos = (
            PontoSerie("cambio_usd_brl", "bcb_sgs", "BRL/USD", date(2026, 11, 30), 5.5),
            PontoSerie("cambio_usd_brl", "bcb_sgs", "BRL/USD", date(2026, 12, 1), 5.6),
        )
        return Coleta(pontos, agora, date(2026, 12, 1))


def _repo(coletor, relogio=None):
    return MercadoAoVivo(BaseFalsa(), {"bcb_sgs": coletor}, relogio or Relogio())


def test_sucesso_ao_vivo_marca_origem_data_e_mescla_pontos():
    coletor = Coletor()
    repo = _repo(coletor)
    fonte = repo.fontes(("bcb_sgs",))[0]
    assert fonte.origem == "ao_vivo"
    assert fonte.status == "ok"
    assert fonte.dado_ate == "2026-12-01"
    assert fonte.coletado_em == "2026-12-01T12:00:00Z"
    assert fonte.defasagem_dias == 0
    pontos = repo.pontos(("cambio_usd_brl",), None, None)
    assert [(p.data, p.valor) for p in pontos] == [
        (date(2026, 11, 20), 5.0),
        (date(2026, 11, 30), 5.5),
        (date(2026, 12, 1), 5.6),
    ]


def test_cache_valido_nao_busca_de_novo():
    relogio = Relogio()
    coletor = Coletor()
    repo = _repo(coletor, relogio)
    repo.fontes(("bcb_sgs",))
    relogio.avancar(hours=5, minutes=59)
    repo.fontes(("bcb_sgs",))
    repo.pontos(("cambio_usd_brl",), None, None)
    assert coletor.chamadas == 1


def test_cache_expirado_busca_de_novo():
    relogio = Relogio()
    coletor = Coletor()
    repo = _repo(coletor, relogio)
    repo.fontes(("bcb_sgs",))
    relogio.avancar(hours=6, seconds=1)
    fonte = repo.fontes(("bcb_sgs",))[0]
    assert coletor.chamadas == 2
    assert fonte.coletado_em == "2026-12-01T18:00:01Z"


@pytest.mark.parametrize("erro", [RuntimeError("falha"), requests.Timeout("lento"), TimeoutError()])
def test_falha_ou_timeout_cai_para_o_snapshot(erro):
    repo = _repo(Coletor(erro))
    fonte = repo.fontes(("bcb_sgs",))[0]
    assert fonte.origem == "snapshot"
    assert fonte.dado_ate == "2026-11-26"
    assert fonte.coletado_em == "2026-11-27T02:17:49Z"
    pontos = repo.pontos(("cambio_usd_brl",), None, None)
    assert [p.valor for p in pontos] == [5.0, 5.1]


def test_falha_fica_em_cache_curto_e_depois_tenta_de_novo():
    relogio = Relogio()
    coletor = Coletor(requests.Timeout("lento"))
    repo = _repo(coletor, relogio)
    repo.fontes(("bcb_sgs",))
    repo.pontos(("cambio_usd_brl",), None, None)
    assert coletor.chamadas == 1
    relogio.avancar(minutes=5, seconds=1)
    repo.fontes(("bcb_sgs",))
    assert coletor.chamadas == 2


def test_cache_expirado_seguido_de_falha_volta_ao_snapshot():
    relogio = Relogio()
    coletor = Coletor()
    repo = _repo(coletor, relogio)
    assert repo.fontes(("bcb_sgs",))[0].origem == "ao_vivo"
    relogio.avancar(hours=6, seconds=1)
    coletor.erro = requests.Timeout("lento")
    fonte = repo.fontes(("bcb_sgs",))[0]
    assert fonte.origem == "snapshot"
    assert fonte.dado_ate == "2026-11-26"
    pontos = repo.pontos(("cambio_usd_brl",), None, None)
    assert [p.valor for p in pontos] == [5.0, 5.1]


def test_fonte_sem_coletor_e_series_nao_pedidas_ficam_no_snapshot():
    coletor = Coletor()
    repo = _repo(coletor)
    assert repo.fontes(("fred",))[0].origem == "snapshot"
    repo.pontos(("cot_acucar_managed_money_long",), None, None)
    assert coletor.chamadas == 0


def test_cliente_http_usa_timeout_curto(monkeypatch):
    recebido = {}

    def falso(url, headers, timeout):
        recebido.update(url=url, headers=headers, timeout=timeout)
        raise requests.Timeout()

    monkeypatch.setattr(mercado_ao_vivo.requests, "get", falso)
    with pytest.raises(requests.Timeout):
        ClienteHttpCurto().get_bytes("https://exemplo.test")
    assert recebido["timeout"] == (4.0, 4.0)
    assert "User-Agent" in recebido["headers"]


def test_configuracao_ilegivel_desliga_o_ao_vivo(tmp_path):
    assert criar_fontes_ao_vivo(tmp_path / "nao-existe.yaml") == {}


class RespostaFalsa:
    def __init__(self, conteudo):
        self.content = conteudo

    def raise_for_status(self):
        return None


def _cliente_api(monkeypatch, resposta):
    urls = []

    def falso(url, headers, timeout):
        urls.append(url)
        return resposta(url)

    monkeypatch.setattr(mercado_ao_vivo.requests, "get", falso)
    settings = Settings(
        data_dir=RAIZ / "data" / "processed",
        static_dir=EXTERNO / "sem-static",
        external_dir=EXTERNO,
        sources_file=RAIZ / "config" / "sources.yaml",
        intl_live=True,
    )
    return TestClient(create_app(settings)), urls


def test_api_ao_vivo_usa_adapters_reais_e_cache(monkeypatch):
    def resposta(url):
        if "bcb.gov.br" in url:
            return RespostaFalsa(json.dumps(REGISTROS_BCB).encode())
        return RespostaFalsa((FIXTURES / "yahoo.json").read_bytes())

    cliente, urls = _cliente_api(monkeypatch, resposta)
    corpo = cliente.get("/api/v1/mercado/cambio").json()
    fonte = corpo["fontes"][0]
    assert fonte["origem"] == "ao_vivo"
    assert fonte["dado_ate"] == HOJE.isoformat()
    cliente.get("/api/v1/mercado/cambio")
    assert len(urls) == 1
    assert "dataInicial=" in urls[0]
    acucar = cliente.get("/api/v1/mercado/acucar").json()
    origens = {f["fonte_id"]: f["origem"] for f in acucar["fontes"]}
    assert origens == {"yahoo": "ao_vivo", "fred": "snapshot", "worldbank": "snapshot"}
    assert "range=3mo" in urls[-1]


def test_api_com_falha_ao_vivo_responde_200_com_snapshot(monkeypatch):
    def resposta(url):
        raise requests.Timeout("lento")

    cliente, _ = _cliente_api(monkeypatch, resposta)
    for endpoint in ("cambio", "acucar", "paises", "cot"):
        r = cliente.get(f"/api/v1/mercado/{endpoint}")
        assert r.status_code == 200
        assert all(f["origem"] == "snapshot" for f in r.json()["fontes"])
    assert cliente.get("/api/v1/uf/PB/producao?ano=2021").status_code == 200


def test_settings_do_ambiente_liga_o_ao_vivo_so_quando_pedido():
    assert Settings.from_env({}).intl_live is False
    assert Settings.from_env({"CANAVIS_INTL_LIVE": "1"}).intl_live is True
    assert Settings.from_env({"CANAVIS_INTL_LIVE": "0"}).intl_live is False
