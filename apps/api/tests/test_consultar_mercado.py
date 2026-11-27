from datetime import date

import pytest

from canavis_api.aplicacao.consultar_acucar import ConsultarAcucar
from canavis_api.aplicacao.consultar_cambio import ConsultarCambio
from canavis_api.aplicacao.consultar_cot import ConsultarCot
from canavis_api.aplicacao.consultar_paises import ConsultarPaises
from canavis_api.dominio.erros import MercadoIndisponivel, ParametroMercadoInvalido
from canavis_api.dominio.mercado import (
    FonteMercado,
    PontoSerie,
    agregar,
    ano_safra,
    fonte_da_serie,
    series_de_paises,
)


def _fonte(fonte_id: str, status: str = "ok") -> FonteMercado:
    return FonteMercado(
        fonte_id,
        fonte_id,
        status,
        "snapshot",
        None,
        None,
        "licenca",
        "atribuicao",
        "url",
        False,
        None,
    )


def _ponto(serie_id: str, dia: date, valor: float, fonte_id: str = "bcb_sgs") -> PontoSerie:
    return PontoSerie(serie_id, fonte_id, "un", dia, valor)


class RepositorioFalso:
    def __init__(self, pontos=(), status=None, disponivel=True):
        self._pontos = list(pontos)
        self._status = status or {}
        self._disponivel = disponivel
        self.consultas = []

    def disponivel(self):
        return self._disponivel

    def fontes(self, fonte_ids):
        return tuple(_fonte(i, self._status.get(i, "ok")) for i in fonte_ids)

    def pontos(self, serie_ids, desde, ate):
        self.consultas.append((serie_ids, desde, ate))
        return [
            p
            for p in self._pontos
            if p.serie_id in serie_ids and (desde is None or p.data >= desde)
        ]


@pytest.mark.parametrize(
    ("dia", "esperado"),
    [
        (date(2023, 3, 31), 2022),
        (date(2023, 4, 1), 2023),
        (date(2023, 12, 31), 2023),
        (date(2024, 1, 1), 2023),
    ],
)
def test_ano_safra_comeca_em_abril(dia, esperado):
    assert ano_safra(dia) == esperado


def test_agregar_mensal_faz_media_simples():
    pontos = [
        _ponto("s", date(2023, 5, 2), 4.0),
        _ponto("s", date(2023, 5, 20), 6.0),
        _ponto("s", date(2023, 6, 1), 10.0),
    ]
    resultado = agregar(pontos, "mensal")
    assert [(p.data, p.valor) for p in resultado] == [
        (date(2023, 5, 1), 5.0),
        (date(2023, 6, 1), 10.0),
    ]


def test_agregar_safra_une_abril_a_marco():
    pontos = [
        _ponto("s", date(2023, 3, 31), 1.0),
        _ponto("s", date(2023, 4, 1), 2.0),
        _ponto("s", date(2024, 3, 31), 4.0),
        _ponto("s", date(2024, 4, 1), 8.0),
    ]
    resultado = agregar(pontos, "safra")
    assert [(p.data, p.valor) for p in resultado] == [
        (date(2022, 4, 1), 1.0),
        (date(2023, 4, 1), 3.0),
        (date(2024, 4, 1), 8.0),
    ]


def test_lista_branca_de_series():
    assert fonte_da_serie("cambio_usd_brl") == "bcb_sgs"
    assert fonte_da_serie("psd_br_producao") == "usda_psd"
    assert fonte_da_serie("x; DROP TABLE") is None
    assert len(series_de_paises(None)) == 30
    assert series_de_paises("br")[0] == "psd_br_producao"


def test_cambio_devolve_serie_e_fonte():
    repo = RepositorioFalso([_ponto("cambio_usd_brl", date(2024, 1, 2), 4.9)])
    consulta = ConsultarCambio(repo).executar(None, "bruta")
    assert consulta.series[0].serie_id == "cambio_usd_brl"
    assert consulta.series[0].pontos[0].valor == 4.9
    assert consulta.fontes[0].origem == "snapshot"


def test_cambio_repassa_desde():
    repo = RepositorioFalso()
    ConsultarCambio(repo).executar(date(2020, 1, 1), "bruta")
    assert repo.consultas[0][1] == date(2020, 1, 1)


def test_agregacao_invalida():
    with pytest.raises(ParametroMercadoInvalido):
        ConsultarCambio(RepositorioFalso()).executar(None, "anual")


def test_sem_manifesto_levanta_indisponivel():
    repo = RepositorioFalso(disponivel=False)
    with pytest.raises(MercadoIndisponivel):
        ConsultarCambio(repo).executar(None, "bruta")
    with pytest.raises(MercadoIndisponivel):
        ConsultarAcucar(repo).executar(None, "bruta")
    with pytest.raises(MercadoIndisponivel):
        ConsultarCot(repo).executar(None)


def test_acucar_usa_fred_quando_ok():
    repo = RepositorioFalso()
    consulta = ConsultarAcucar(repo).executar(None, "bruta")
    assert [s.serie_id for s in consulta.series] == ["acucar_ny11_fechamento", "acucar_isa_fred"]
    assert consulta.observacoes == ()


@pytest.mark.parametrize("status", ["falha", "ausente"])
def test_acucar_troca_fred_pelo_banco_mundial_e_rotula(status):
    repo = RepositorioFalso(status={"fred": status})
    consulta = ConsultarAcucar(repo).executar(None, "mensal")
    assert [s.serie_id for s in consulta.series] == ["acucar_ny11_fechamento", "acucar_mundo_wb"]
    assert len(consulta.observacoes) == 1
    assert "Banco Mundial" in consulta.observacoes[0]


def test_paises_filtra_e_valida():
    repo = RepositorioFalso()
    consulta = ConsultarPaises(repo).executar("in", None)
    assert all(s.serie_id.startswith("psd_in_") for s in consulta.series)
    with pytest.raises(ParametroMercadoInvalido):
        ConsultarPaises(repo).executar("xx", None)


def test_cot_tem_cinco_series():
    consulta = ConsultarCot(RepositorioFalso()).executar(None)
    assert len(consulta.series) == 5
