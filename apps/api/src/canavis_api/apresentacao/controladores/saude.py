from fastapi.responses import JSONResponse

from canavis_api.aplicacao.saude import VerificarDados
from canavis_api.apresentacao.controladores.base import ControladorBase
from canavis_api.apresentacao.esquemas import SaudeResposta


class SaudeControlador(ControladorBase):
    def __init__(self, verificar_dados: VerificarDados) -> None:
        self._verificar_dados = verificar_dados
        super().__init__()

    def _registrar_rotas(self) -> None:
        self.router.add_api_route(
            "/saude",
            self.saude,
            methods=["GET"],
            response_model=SaudeResposta,
            responses={503: {"model": SaudeResposta}},
        )

    def saude(self) -> JSONResponse:
        if self._verificar_dados.executar():
            return JSONResponse(SaudeResposta(status="ok", dados=True).model_dump())
        corpo = SaudeResposta(status="degradado", dados=False).model_dump()
        return JSONResponse(corpo, status_code=503)
