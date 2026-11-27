from collections import defaultdict
from dataclasses import dataclass
from datetime import date

AGREGACOES = ("bruta", "mensal", "safra")
MES_INICIO_SAFRA = 4

PAISES = ("br", "in", "th", "cn", "ue", "us")
ATRIBUTOS_PAISES = ("producao", "exportacoes", "importacoes", "estoque_final", "consumo_humano")

SERIES_CAMBIO = ("cambio_usd_brl",)
SERIES_ACUCAR_DIARIO = ("acucar_ny11_fechamento",)
SERIES_ACUCAR_MENSAL = ("acucar_isa_fred",)
SERIES_ACUCAR_MENSAL_ALTERNATIVA = ("acucar_mundo_wb",)
SERIES_COT = (
    "cot_acucar_managed_money_long",
    "cot_acucar_managed_money_short",
    "cot_acucar_produtores_long",
    "cot_acucar_produtores_short",
    "cot_acucar_open_interest",
)

_FONTE_POR_SERIE = {
    **dict.fromkeys(SERIES_CAMBIO, "bcb_sgs"),
    **dict.fromkeys(SERIES_ACUCAR_DIARIO, "yahoo"),
    **dict.fromkeys(SERIES_ACUCAR_MENSAL, "fred"),
    **dict.fromkeys(SERIES_ACUCAR_MENSAL_ALTERNATIVA, "worldbank"),
    **dict.fromkeys(SERIES_COT, "cftc"),
    **{f"psd_{p}_{a}": "usda_psd" for p in PAISES for a in ATRIBUTOS_PAISES},
}


@dataclass(frozen=True)
class PontoSerie:
    serie_id: str
    fonte_id: str
    unidade: str
    data: date
    valor: float


@dataclass(frozen=True)
class FonteMercado:
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
    dado_ate: str | None = None


@dataclass(frozen=True)
class SerieMercado:
    serie_id: str
    fonte_id: str
    unidade: str | None
    agregacao: str
    pontos: tuple[PontoSerie, ...]


@dataclass(frozen=True)
class ConsultaMercado:
    fontes: tuple[FonteMercado, ...]
    series: tuple[SerieMercado, ...]
    observacoes: tuple[str, ...]


def fonte_da_serie(serie_id: str) -> str | None:
    return _FONTE_POR_SERIE.get(serie_id)


def series_de_paises(pais: str | None) -> tuple[str, ...]:
    paises = PAISES if pais is None else (pais,)
    return tuple(f"psd_{p}_{a}" for p in paises for a in ATRIBUTOS_PAISES)


def ano_safra(data: date) -> int:
    return data.year if data.month >= MES_INICIO_SAFRA else data.year - 1


def _chave_periodo(data: date, agregacao: str) -> date:
    if agregacao == "mensal":
        return date(data.year, data.month, 1)
    return date(ano_safra(data), MES_INICIO_SAFRA, 1)


def agregar(pontos: list[PontoSerie], agregacao: str) -> list[PontoSerie]:
    if agregacao == "bruta":
        return sorted(pontos, key=lambda p: p.data)
    grupos: dict[date, list[PontoSerie]] = defaultdict(list)
    for ponto in pontos:
        grupos[_chave_periodo(ponto.data, agregacao)].append(ponto)
    return [
        PontoSerie(
            grupo[0].serie_id,
            grupo[0].fonte_id,
            grupo[0].unidade,
            periodo,
            sum(p.valor for p in grupo) / len(grupo),
        )
        for periodo, grupo in sorted(grupos.items())
    ]


def montar_series(
    pontos: list[PontoSerie], serie_ids: tuple[str, ...], agregacao: str
) -> tuple[SerieMercado, ...]:
    por_serie: dict[str, list[PontoSerie]] = defaultdict(list)
    for ponto in pontos:
        por_serie[ponto.serie_id].append(ponto)
    series = []
    for serie_id in serie_ids:
        agregados = agregar(por_serie.get(serie_id, []), agregacao)
        unidade = agregados[0].unidade if agregados else None
        series.append(
            SerieMercado(
                serie_id, fonte_da_serie(serie_id) or "", unidade, agregacao, tuple(agregados)
            )
        )
    return tuple(series)
