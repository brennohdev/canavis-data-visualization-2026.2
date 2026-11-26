from canavis_api.aplicacao.portas import ProducaoRepositorio
from canavis_api.dominio.erros import ProducaoNaoEncontrada
from canavis_api.dominio.producao import ProducaoUF
from canavis_api.dominio.territorio import uf_por_sigla


class ConsultarProducaoUF:
    def __init__(self, repositorio: ProducaoRepositorio) -> None:
        self._repositorio = repositorio

    def executar(self, sigla: str, ano: int) -> ProducaoUF:
        uf = uf_por_sigla(sigla)
        if uf is None:
            raise ProducaoNaoEncontrada(sigla, ano)
        producao = self._repositorio.buscar_uf(uf, ano)
        if producao is None:
            raise ProducaoNaoEncontrada(sigla, ano)
        return producao
