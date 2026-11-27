from datetime import date

from pydantic import BaseModel


class ProducaoUFResposta(BaseModel):
    sigla: str
    territorio_id: str
    nome: str
    ano: int
    produtividade_t_ha: float | None
    quantidade_produzida_t: float | None
    area_colhida_ha: float | None


class SaudeResposta(BaseModel):
    status: str
    dados: bool


class ErroResposta(BaseModel):
    detail: str


class FonteResposta(BaseModel):
    fonte_id: str
    nome: str
    status: str
    origem: str
    coletado_em: str | None
    defasagem_dias: int | None
    licenca: str
    atribuicao: str
    url: str
    nao_oficial: bool
    erro: str | None
    dado_ate: str | None


class PontoResposta(BaseModel):
    data: date
    valor: float


class SerieResposta(BaseModel):
    serie_id: str
    fonte_id: str
    unidade: str | None
    agregacao: str
    pontos: list[PontoResposta]


class MercadoResposta(BaseModel):
    fontes: list[FonteResposta]
    series: list[SerieResposta]
    observacoes: list[str]
