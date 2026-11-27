from datetime import date
from typing import Annotated, Literal

from fastapi import Query

from canavis_api.aplicacao.consultar_acucar import ConsultarAcucar
from canavis_api.aplicacao.consultar_cambio import ConsultarCambio
from canavis_api.aplicacao.consultar_cot import ConsultarCot
from canavis_api.aplicacao.consultar_paises import ConsultarPaises
from canavis_api.apresentacao.controladores.base import ControladorBase
from canavis_api.apresentacao.esquemas import ErroResposta, MercadoResposta
from canavis_api.dominio.mercado import ConsultaMercado

Agregacao = Literal["bruta", "mensal", "safra"]
Desde = Annotated[date | None, Query()]


def _resposta(consulta: ConsultaMercado) -> MercadoResposta:
    return MercadoResposta.model_validate(consulta, from_attributes=True)


class MercadoControlador(ControladorBase):
    def __init__(
        self,
        cambio: ConsultarCambio,
        acucar: ConsultarAcucar,
        paises: ConsultarPaises,
        cot: ConsultarCot,
    ) -> None:
        self._cambio = cambio
        self._acucar = acucar
        self._paises = paises
        self._cot = cot
        super().__init__()

    def _registrar_rotas(self) -> None:
        respostas = {422: {"model": ErroResposta}, 503: {"model": ErroResposta}}
        for caminho, funcao in (
            ("/mercado/cambio", self.cambio),
            ("/mercado/acucar", self.acucar),
            ("/mercado/paises", self.paises),
            ("/mercado/cot", self.cot),
        ):
            self.router.add_api_route(
                caminho,
                funcao,
                methods=["GET"],
                response_model=MercadoResposta,
                responses=respostas,
            )

    def cambio(self, desde: Desde = None, agregacao: Agregacao = "bruta") -> MercadoResposta:
        return _resposta(self._cambio.executar(desde, agregacao))

    def acucar(self, desde: Desde = None, agregacao: Agregacao = "bruta") -> MercadoResposta:
        return _resposta(self._acucar.executar(desde, agregacao))

    def paises(
        self, pais: Annotated[str | None, Query()] = None, desde: Desde = None
    ) -> MercadoResposta:
        return _resposta(self._paises.executar(pais, desde))

    def cot(self, desde: Desde = None) -> MercadoResposta:
        return _resposta(self._cot.executar(desde))
