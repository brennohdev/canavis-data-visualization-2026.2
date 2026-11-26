from dataclasses import dataclass


@dataclass(frozen=True)
class ProducaoUF:
    sigla: str
    territorio_id: str
    nome: str
    ano: int
    produtividade_t_ha: float | None
    quantidade_produzida_t: float | None
    area_colhida_ha: float | None
