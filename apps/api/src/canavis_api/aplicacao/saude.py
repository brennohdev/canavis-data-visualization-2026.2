from canavis_api.aplicacao.portas import ProducaoRepositorio


class VerificarDados:
    def __init__(self, repositorio: ProducaoRepositorio) -> None:
        self._repositorio = repositorio

    def executar(self) -> bool:
        return self._repositorio.disponivel()
