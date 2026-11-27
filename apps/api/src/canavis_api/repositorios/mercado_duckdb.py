import json
import logging
from collections import defaultdict
from datetime import date
from pathlib import Path

import duckdb

from canavis_api.dominio.erros import MercadoIndisponivel
from canavis_api.dominio.mercado import FonteMercado, PontoSerie, fonte_da_serie

ARQUIVO_MANIFESTO = "manifest.json"
ARQUIVO_DIM = "dim_fonte_intl.parquet"
_SQL_DIM = (
    "SELECT fonte_id, fonte, url, licenca, atribuicao, nao_oficial FROM read_parquet(?) "
    "WHERE list_contains(?, fonte_id)"
)
_SQL_PONTOS = (
    "SELECT serie_id, fonte_id, unidade, CAST(data AS DATE), valor FROM read_parquet(?) "
    "WHERE list_contains(?, serie_id) AND CAST(data AS DATE) >= ? AND CAST(data AS DATE) <= ? "
    "ORDER BY serie_id, data"
)
_log = logging.getLogger(__name__)


class MercadoDuckDB:
    def __init__(self, external_dir: Path) -> None:
        self._external_dir = external_dir

    def disponivel(self) -> bool:
        return (self._external_dir / ARQUIVO_MANIFESTO).is_file()

    def _manifesto(self) -> dict:
        try:
            texto = (self._external_dir / ARQUIVO_MANIFESTO).read_text(encoding="utf-8")
            fontes = json.loads(texto)["fontes"]
        except (OSError, ValueError, KeyError) as erro:
            _log.warning("Manifesto ilegível em %s", self._external_dir)
            raise MercadoIndisponivel() from erro
        if not isinstance(fontes, dict):
            raise MercadoIndisponivel()
        return fontes

    def _dimensao(self, fonte_ids: tuple[str, ...]) -> dict[str, tuple]:
        arquivo = self._external_dir / ARQUIVO_DIM
        if not arquivo.is_file():
            return {}
        con = duckdb.connect(":memory:")
        try:
            linhas = con.execute(_SQL_DIM, [str(arquivo), list(fonte_ids)]).fetchall()
        except duckdb.Error:
            _log.warning("Falha ao ler %s", arquivo)
            return {}
        finally:
            con.close()
        return {linha[0]: linha for linha in linhas}

    def fontes(self, fonte_ids: tuple[str, ...]) -> tuple[FonteMercado, ...]:
        if not self.disponivel():
            raise MercadoIndisponivel()
        manifesto = self._manifesto()
        dimensao = self._dimensao(fonte_ids)
        return tuple(self._fonte(i, manifesto.get(i), dimensao.get(i)) for i in fonte_ids)

    def _fonte(self, fonte_id: str, entrada: dict | None, dim: tuple | None) -> FonteMercado:
        entrada = entrada or {}
        arquivo = entrada.get("arquivo")
        existe = bool(arquivo) and (self._external_dir / arquivo).is_file()
        status = entrada.get("status", "ausente") if entrada else "ausente"
        if status == "ok" and not existe:
            status = "ausente"
        return FonteMercado(
            fonte_id=fonte_id,
            nome=dim[1] if dim else fonte_id,
            status=status,
            origem="snapshot",
            coletado_em=entrada.get("coletado_em"),
            defasagem_dias=_defasagem(entrada.get("coletado_em"), entrada.get("periodo_fim")),
            licenca=dim[3] if dim else entrada.get("licenca", ""),
            atribuicao=dim[4] if dim else "",
            url=dim[2] if dim else entrada.get("url", ""),
            nao_oficial=bool(dim[5]) if dim else False,
            erro=entrada.get("erro"),
            dado_ate=entrada.get("periodo_fim"),
        )

    def pontos(
        self, serie_ids: tuple[str, ...], desde: date | None, ate: date | None
    ) -> list[PontoSerie]:
        if not self.disponivel():
            raise MercadoIndisponivel()
        manifesto = self._manifesto()
        por_fonte: dict[str, list[str]] = defaultdict(list)
        for serie_id in serie_ids:
            fonte_id = fonte_da_serie(serie_id)
            if fonte_id is not None:
                por_fonte[fonte_id].append(serie_id)
        pontos: list[PontoSerie] = []
        for fonte_id, ids in por_fonte.items():
            arquivo = (manifesto.get(fonte_id) or {}).get("arquivo")
            if not arquivo or not (self._external_dir / arquivo).is_file():
                continue
            pontos.extend(self._ler(self._external_dir / arquivo, ids, desde, ate))
        return pontos

    def _ler(
        self, arquivo: Path, ids: list[str], desde: date | None, ate: date | None
    ) -> list[PontoSerie]:
        con = duckdb.connect(":memory:")
        try:
            parametros = [str(arquivo), ids, desde or date.min, ate or date.max]
            linhas = con.execute(_SQL_PONTOS, parametros).fetchall()
        except duckdb.Error as erro:
            _log.warning("Falha ao ler o snapshot %s", arquivo)
            raise MercadoIndisponivel() from erro
        finally:
            con.close()
        return [PontoSerie(*linha[:4], float(linha[4])) for linha in linhas]


def _defasagem(coletado_em: str | None, periodo_fim: str | None) -> int | None:
    if not coletado_em or not periodo_fim:
        return None
    try:
        return (date.fromisoformat(coletado_em[:10]) - date.fromisoformat(periodo_fim[:10])).days
    except ValueError:
        return None
