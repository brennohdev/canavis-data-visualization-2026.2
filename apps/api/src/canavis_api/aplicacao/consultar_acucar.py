from datetime import date

from canavis_api.aplicacao.consulta_mercado import consultar_mercado, validar_agregacao
from canavis_api.aplicacao.portas import MercadoRepositorio
from canavis_api.dominio.erros import MercadoIndisponivel
from canavis_api.dominio.mercado import (
    SERIES_ACUCAR_DIARIO,
    SERIES_ACUCAR_MENSAL,
    SERIES_ACUCAR_MENSAL_ALTERNATIVA,
    ConsultaMercado,
)

_FONTES = ("yahoo", "fred", "worldbank")
_AVISO_FRED = (
    "Série mensal do FRED indisponível na última coleta (status diferente de ok); "
    "preço mensal substituído pelo açúcar mundial do Banco Mundial (acucar_mundo_wb), "
    "que usa o mesmo preço do FMI, em USD/kg."
)


class ConsultarAcucar:
    def __init__(self, repositorio: MercadoRepositorio) -> None:
        self._repositorio = repositorio

    def executar(self, desde: date | None, agregacao: str) -> ConsultaMercado:
        validar_agregacao(agregacao)
        if not self._repositorio.disponivel():
            raise MercadoIndisponivel()
        fred = self._repositorio.fontes(("fred",))[0]
        if fred.status == "ok":
            mensal, observacoes = SERIES_ACUCAR_MENSAL, ()
        else:
            mensal, observacoes = SERIES_ACUCAR_MENSAL_ALTERNATIVA, (_AVISO_FRED,)
        return consultar_mercado(
            self._repositorio,
            _FONTES,
            SERIES_ACUCAR_DIARIO + mensal,
            desde,
            agregacao,
            observacoes,
        )
