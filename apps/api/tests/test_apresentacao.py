from fastapi import FastAPI
from fastapi.testclient import TestClient

from canavis_api.apresentacao.controladores.producao_uf import ProducaoUFControlador
from canavis_api.apresentacao.erros import registrar_erros
from canavis_api.dominio.erros import DadosIndisponiveis, ProducaoNaoEncontrada
from canavis_api.dominio.producao import ProducaoUF


class CasoDeUsoFalso:
    def __init__(self, resultado=None, erro=None):
        self.resultado = resultado
        self.erro = erro

    def executar(self, sigla: str, ano: int) -> ProducaoUF:
        if self.erro:
            raise self.erro
        return self.resultado


def _cliente(caso):
    app = FastAPI()
    app.include_router(ProducaoUFControlador(caso).router)
    registrar_erros(app)
    return TestClient(app)


def test_200():
    producao = ProducaoUF("PB", "uf:25", "Paraíba", 2021, 55.6, None, 2.0)
    r = _cliente(CasoDeUsoFalso(resultado=producao)).get("/uf/PB/producao?ano=2021")
    assert r.status_code == 200
    assert list(r.json()) == [
        "sigla",
        "territorio_id",
        "nome",
        "ano",
        "produtividade_t_ha",
        "quantidade_produzida_t",
        "area_colhida_ha",
    ]
    assert r.json()["quantidade_produzida_t"] is None


def test_404():
    r = _cliente(CasoDeUsoFalso(erro=ProducaoNaoEncontrada("PB", 1999))).get("/uf/PB/producao")
    assert r.status_code == 404
    assert r.json() == {"detail": "Sem dados para a UF «PB» no ano 1999."}


def test_503():
    r = _cliente(CasoDeUsoFalso(erro=DadosIndisponiveis())).get("/uf/PB/producao")
    assert r.status_code == 503
    assert "indisponíveis" in r.json()["detail"]


def test_ano_invalido_422():
    assert _cliente(CasoDeUsoFalso()).get("/uf/PB/producao?ano=abc").status_code == 422
