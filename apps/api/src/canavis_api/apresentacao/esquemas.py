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
