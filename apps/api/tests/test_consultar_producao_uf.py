import pytest

from canavis_api.aplicacao.producao_uf import ConsultarProducaoUF
from canavis_api.aplicacao.saude import VerificarDados
from canavis_api.dominio.erros import DadosIndisponiveis, ProducaoNaoEncontrada
from canavis_api.dominio.producao import ProducaoUF
from canavis_api.dominio.territorio import Uf

PB_2021 = ProducaoUF("PB", "uf:25", "Paraíba", 2021, 55.6, 100.0, 2.0)


class RepositorioFalso:
    def __init__(self, resultado=PB_2021, erro=None, disponivel=True):
        self.resultado = resultado
        self.erro = erro
        self._disponivel = disponivel
        self.chamadas: list[tuple[Uf, int]] = []

    def disponivel(self) -> bool:
        return self._disponivel

    def buscar_uf(self, uf: Uf, ano: int):
        self.chamadas.append((uf, ano))
        if self.erro:
            raise self.erro
        return self.resultado


def test_sucesso():
    repositorio = RepositorioFalso()
    assert ConsultarProducaoUF(repositorio).executar("PB", 2021) == PB_2021
    assert repositorio.chamadas == [(Uf("PB", "25"), 2021)]


def test_sigla_minuscula_normalizada():
    repositorio = RepositorioFalso()
    ConsultarProducaoUF(repositorio).executar(" pb ", 2021)
    assert repositorio.chamadas == [(Uf("PB", "25"), 2021)]


def test_sigla_desconhecida_nao_toca_no_repositorio():
    repositorio = RepositorioFalso()
    with pytest.raises(ProducaoNaoEncontrada):
        ConsultarProducaoUF(repositorio).executar("XX", 2021)
    assert repositorio.chamadas == []


def test_resultado_vazio_vira_nao_encontrada():
    with pytest.raises(ProducaoNaoEncontrada) as erro:
        ConsultarProducaoUF(RepositorioFalso(resultado=None)).executar("PB", 1999)
    assert erro.value.ano == 1999


def test_dados_indisponiveis_propaga():
    repositorio = RepositorioFalso(erro=DadosIndisponiveis())
    with pytest.raises(DadosIndisponiveis):
        ConsultarProducaoUF(repositorio).executar("PB", 2021)


@pytest.mark.parametrize("disponivel", [True, False])
def test_verificar_dados(disponivel):
    assert VerificarDados(RepositorioFalso(disponivel=disponivel)).executar() is disponivel
