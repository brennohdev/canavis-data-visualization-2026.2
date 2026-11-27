from datetime import date

from canavis_api.aplicacao.portas import MercadoRepositorio
from canavis_api.dominio.erros import MercadoIndisponivel, ParametroMercadoInvalido
from canavis_api.dominio.mercado import AGREGACOES, ConsultaMercado, montar_series


def validar_agregacao(agregacao: str) -> None:
    if agregacao not in AGREGACOES:
        raise ParametroMercadoInvalido("agregacao", agregacao)


def consultar_mercado(
    repositorio: MercadoRepositorio,
    fonte_ids: tuple[str, ...],
    serie_ids: tuple[str, ...],
    desde: date | None,
    agregacao: str,
    observacoes: tuple[str, ...] = (),
) -> ConsultaMercado:
    if not repositorio.disponivel():
        raise MercadoIndisponivel()
    fontes = repositorio.fontes(fonte_ids)
    pontos = repositorio.pontos(serie_ids, desde, None)
    return ConsultaMercado(fontes, montar_series(pontos, serie_ids, agregacao), observacoes)
