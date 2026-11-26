from typing import Annotated

from fastapi import Query

from canavis_api.aplicacao.producao_uf import ConsultarProducaoUF
from canavis_api.apresentacao.controladores.base import ControladorBase
from canavis_api.apresentacao.esquemas import ErroResposta, ProducaoUFResposta


class ProducaoUFControlador(ControladorBase):
    def __init__(self, consultar: ConsultarProducaoUF) -> None:
        self._consultar = consultar
        super().__init__()

    def _registrar_rotas(self) -> None:
        self.router.add_api_route(
            "/uf/{sigla}/producao",
            self.producao_uf,
            methods=["GET"],
            response_model=ProducaoUFResposta,
            responses={404: {"model": ErroResposta}, 503: {"model": ErroResposta}},
        )

    def producao_uf(self, sigla: str, ano: Annotated[int, Query()] = 2021) -> ProducaoUFResposta:
        producao = self._consultar.executar(sigla, ano)
        return ProducaoUFResposta.model_validate(producao, from_attributes=True)
