import logging
import re
import threading
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
import yaml

from canavis.sources.intl.base import FonteIntl
from canavis.sources.intl.bcb_sgs import BcbSgsSource
from canavis.sources.intl.yahoo import YahooSource
from canavis_api.aplicacao.portas import MercadoRepositorio
from canavis_api.dominio.mercado import FonteMercado, PontoSerie, fonte_da_serie

ORIGEM_AO_VIVO = "ao_vivo"
TTL_SUCESSO = timedelta(hours=6)
TTL_FALHA = timedelta(minutes=5)
TIMEOUT_SEGUNDOS = 4.0
JANELA_DIAS = 120
USER_AGENT = "canavis/0.1 (projeto academico UFPB - Visualizacao de Dados)"

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Coleta:
    pontos: tuple[PontoSerie, ...]
    coletado_em: datetime
    dado_ate: date


@dataclass(frozen=True)
class _Item:
    coleta: Coleta | None
    expira: datetime


Coletor = Callable[[datetime], Coleta]


class ClienteHttpCurto:
    def __init__(self, timeout: float = TIMEOUT_SEGUNDOS) -> None:
        self._timeout = timeout

    def get_bytes(self, url: str, headers: dict[str, str] | None = None) -> bytes:
        cabecalhos = {"User-Agent": USER_AGENT, **(headers or {})}
        resposta = requests.get(url, headers=cabecalhos, timeout=(self._timeout, self._timeout))
        resposta.raise_for_status()
        return resposta.content


def _coletor(fonte_id: str, construir: Callable[[date], FonteIntl]) -> Coletor:
    def coletar(agora: datetime) -> Coleta:
        quadro = construir(agora.date()).fetch()
        if quadro.empty:
            raise ValueError(f"Fonte {fonte_id} devolveu quadro vazio")
        pontos = tuple(
            PontoSerie(
                linha.serie_id,
                linha.fonte_id,
                linha.unidade,
                linha.data.date(),
                float(linha.valor),
            )
            for linha in quadro.itertuples(index=False)
        )
        return Coleta(pontos, agora, max(p.data for p in pontos))

    return coletar


def criar_fontes_ao_vivo(
    arquivo: Path, cliente: ClienteHttpCurto | None = None
) -> dict[str, Coletor]:
    try:
        configuracao = yaml.safe_load(arquivo.read_text(encoding="utf-8"))
        bcb = dict(configuracao["bcb_sgs"], key="bcb_sgs")
        yahoo = dict(configuracao["yahoo"], key="yahoo")
    except (OSError, KeyError, TypeError, yaml.YAMLError):
        _log.warning("Configuração das fontes ao vivo ilegível em %s", arquivo)
        return {}
    cliente = cliente or ClienteHttpCurto()

    def construir_bcb(hoje: date) -> FonteIntl:
        desde = (hoje - timedelta(days=JANELA_DIAS)).isoformat()
        return BcbSgsSource(dict(bcb, desde=desde), cliente)

    def construir_yahoo(hoje: date) -> FonteIntl:
        url = re.sub(r"range=\w+", "range=3mo", yahoo["url"])
        return YahooSource(dict(yahoo, url=url), cliente)

    return {
        "bcb_sgs": _coletor("bcb_sgs", construir_bcb),
        "yahoo": _coletor("yahoo", construir_yahoo),
    }


def _agora() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


class MercadoAoVivo:
    def __init__(
        self,
        base: MercadoRepositorio,
        coletores: Mapping[str, Coletor],
        relogio: Callable[[], datetime] = _agora,
        ttl: timedelta = TTL_SUCESSO,
        ttl_falha: timedelta = TTL_FALHA,
    ) -> None:
        self._base = base
        self._coletores = dict(coletores)
        self._relogio = relogio
        self._ttl = ttl
        self._ttl_falha = ttl_falha
        self._cache: dict[str, _Item] = {}
        self._travas = {fonte_id: threading.Lock() for fonte_id in self._coletores}

    def disponivel(self) -> bool:
        return self._base.disponivel()

    def _coleta(self, fonte_id: str) -> Coleta | None:
        coletor = self._coletores.get(fonte_id)
        if coletor is None:
            return None
        with self._travas[fonte_id]:
            agora = self._relogio()
            item = self._cache.get(fonte_id)
            if item is not None and agora < item.expira:
                return item.coleta
            try:
                coleta = coletor(agora)
            except Exception as erro:
                _log.warning("Falha na coleta ao vivo de %s: %s", fonte_id, type(erro).__name__)
                coleta = None
            validade = self._ttl if coleta is not None else self._ttl_falha
            self._cache[fonte_id] = _Item(coleta, agora + validade)
            return coleta

    def fontes(self, fonte_ids: tuple[str, ...]) -> tuple[FonteMercado, ...]:
        return tuple(self._fonte(f) for f in self._base.fontes(fonte_ids))

    def _fonte(self, fonte: FonteMercado) -> FonteMercado:
        coleta = self._coleta(fonte.fonte_id)
        if coleta is None:
            return fonte
        return replace(
            fonte,
            status="ok",
            origem=ORIGEM_AO_VIVO,
            coletado_em=coleta.coletado_em.strftime("%Y-%m-%dT%H:%M:%SZ"),
            defasagem_dias=(coleta.coletado_em.date() - coleta.dado_ate).days,
            erro=None,
            dado_ate=coleta.dado_ate.isoformat(),
        )

    def pontos(
        self, serie_ids: tuple[str, ...], desde: date | None, ate: date | None
    ) -> list[PontoSerie]:
        pontos = self._base.pontos(serie_ids, desde, ate)
        pedidas = {fonte_da_serie(serie_id) for serie_id in serie_ids}
        for fonte_id in self._coletores:
            if fonte_id not in pedidas:
                continue
            coleta = self._coleta(fonte_id)
            if coleta is None:
                continue
            inicio = min(p.data for p in coleta.pontos)
            vivos = [
                p
                for p in coleta.pontos
                if p.serie_id in serie_ids
                and (desde is None or p.data >= desde)
                and (ate is None or p.data <= ate)
            ]
            if not vivos:
                continue
            pontos = [p for p in pontos if not (p.fonte_id == fonte_id and p.data >= inicio)]
            pontos.extend(vivos)
        return sorted(pontos, key=lambda p: (p.serie_id, p.data))
