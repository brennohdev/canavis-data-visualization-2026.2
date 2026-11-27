from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import pandas as pd

from canavis import storage
from canavis.config import load_settings, load_sources
from canavis.logging import get_logger
from canavis.sources.http_client import HttpClient
from canavis.sources.intl.base import BrutoIntl, FonteIntl
from canavis.sources.intl.esquema import FORMATO_COLETA, validar
from canavis.sources.intl.snapshot import (
    bruto_mais_recente,
    gravar_manifesto,
    gravar_snapshot,
    hash_bytes,
    hash_dados,
    hash_quadro,
    ler_manifesto,
    salvar_bruto,
)
from canavis.sources.registry import build_source, intl_sources

_log = get_logger(__name__)

NOME_DIM = "dim_fonte_intl"


def pasta_saida() -> Path:
    return load_settings().paths.raw.parent / "external"


def pasta_bruto() -> Path:
    return load_settings().paths.raw / "intl"


def _selecionar(fontes: list[str] | None) -> list[str]:
    disponiveis = intl_sources()
    if not fontes:
        return disponiveis
    desconhecidas = [f for f in fontes if f not in disponiveis]
    if desconhecidas:
        raise KeyError(f"Fontes internacionais desconhecidas: {desconhecidas}")
    return fontes


def _entrada(
    frame: pd.DataFrame,
    arquivo: str,
    hash_snapshot: str,
    hash_conteudo: str,
    bruto_sha: str,
    coletado_em: str,
    versao_fonte: str | None,
    url: str,
    licenca: str,
) -> dict:
    return {
        "arquivo": arquivo,
        "sha256": hash_snapshot,
        "sha256_dados": hash_conteudo,
        "sha256_bruto": bruto_sha,
        "linhas": int(len(frame)),
        "coletado_em": coletado_em,
        "versao_fonte": versao_fonte,
        "periodo_ini": pd.Timestamp(frame["data"].min()).strftime("%Y-%m-%d"),
        "periodo_fim": pd.Timestamp(frame["data"].max()).strftime("%Y-%m-%d"),
        "status": "ok",
        "erro": None,
        "url": url,
        "licenca": licenca,
    }


def _marcar_falha(manifesto: dict, fonte_id: str, erro: str) -> None:
    config = load_sources()[fonte_id]
    anterior = dict(manifesto["fontes"].get(fonte_id) or {})
    anterior.setdefault("arquivo", None)
    anterior.setdefault("sha256", None)
    anterior.setdefault("sha256_bruto", None)
    anterior.setdefault("linhas", 0)
    anterior.setdefault("coletado_em", None)
    anterior.setdefault("versao_fonte", None)
    anterior.setdefault("periodo_ini", None)
    anterior.setdefault("periodo_fim", None)
    anterior["url"] = config["url"]
    anterior["licenca"] = config["license"]
    anterior["status"] = "falha"
    anterior["erro"] = erro
    manifesto["fontes"][fonte_id] = anterior


def _gravar_dimensao(saida: Path) -> None:
    configs = load_sources()
    linhas = [
        {
            "fonte_id": fonte_id,
            "fonte": configs[fonte_id]["name"],
            "url": configs[fonte_id]["url"],
            "periodicidade": configs[fonte_id]["periodicity"],
            "licenca": configs[fonte_id]["license"],
            "atribuicao": configs[fonte_id]["attribution"],
            "nao_oficial": bool(configs[fonte_id].get("unofficial", False)),
        }
        for fonte_id in intl_sources()
    ]
    storage.write(pd.DataFrame(linhas), saida, NOME_DIM)


def _processar(
    fonte: FonteIntl,
    fonte_id: str,
    bruto: BrutoIntl,
    coletado_em: datetime,
    saida: Path,
    bruto_sha: str,
    anterior: dict | None = None,
) -> dict:
    frame = validar(fonte.normalizar(bruto, coletado_em))
    conteudo = hash_dados(frame)
    if (
        anterior
        and anterior.get("status") == "ok"
        and anterior.get("sha256_dados") == conteudo
        and (saida / anterior["arquivo"]).exists()
    ):
        return anterior
    caminho = gravar_snapshot(frame, saida, fonte_id)
    return _entrada(
        frame,
        caminho.name,
        hash_quadro(frame),
        conteudo,
        bruto_sha,
        coletado_em.strftime(FORMATO_COLETA),
        bruto.versao_fonte,
        bruto.url,
        load_sources()[fonte_id]["license"],
    )


def refresh(
    fontes: list[str] | None = None,
    saida: Path | None = None,
    raiz_bruto: Path | None = None,
    client: HttpClient | None = None,
    tentativas: int = 2,
    pausa: Callable[[float], None] = time.sleep,
) -> dict:
    saida = saida or pasta_saida()
    raiz_bruto = raiz_bruto or pasta_bruto()
    manifesto = ler_manifesto(saida)
    mudou = False
    for fonte_id in _selecionar(fontes):
        ultima_falha = ""
        for tentativa in range(1, tentativas + 1):
            try:
                fonte = build_source(fonte_id, client)
                bruto = fonte.baixar()
                coletado_em = datetime.now(timezone.utc).replace(microsecond=0)
                salvar_bruto(
                    raiz_bruto,
                    fonte_id,
                    bruto.conteudo,
                    bruto.extensao,
                    bruto.url,
                    bruto.versao_fonte,
                    coletado_em,
                )
                anterior = manifesto["fontes"].get(fonte_id)
                entrada = _processar(
                    fonte,
                    fonte_id,
                    bruto,
                    coletado_em,
                    saida,
                    hash_bytes(bruto.conteudo),
                    anterior,
                )
                mudou = mudou or entrada is not anterior
                manifesto["fontes"][fonte_id] = entrada
                _log.info(
                    "intl | %s | ok | %d linhas",
                    fonte_id,
                    manifesto["fontes"][fonte_id]["linhas"],
                )
                ultima_falha = ""
                break
            except Exception as erro:
                ultima_falha = f"{type(erro).__name__}: {erro}"
                _log.warning(
                    "intl | %s | tentativa %d/%d falhou | %s",
                    fonte_id,
                    tentativa,
                    tentativas,
                    ultima_falha,
                )
                if tentativa < tentativas:
                    pausa(3.0 * tentativa)
        if ultima_falha:
            _marcar_falha(manifesto, fonte_id, ultima_falha)
    if mudou:
        _gravar_dimensao(saida)
        gravar_manifesto(saida, manifesto)
    return manifesto


def reprocess(
    fontes: list[str] | None = None,
    saida: Path | None = None,
    raiz_bruto: Path | None = None,
) -> dict[str, dict]:
    saida = saida or pasta_saida()
    raiz_bruto = raiz_bruto or pasta_bruto()
    manifesto = ler_manifesto(saida)
    comparacao: dict[str, dict] = {}
    for fonte_id in _selecionar(fontes):
        registro = manifesto["fontes"].get(fonte_id) or {}
        anterior = registro.get("sha256")
        if registro.get("status") != "ok":
            _log.warning("intl | %s | fonte sem snapshot ok, nada a reprocessar", fonte_id)
            comparacao[fonte_id] = {"anterior": anterior, "novo": None, "igual": False}
            continue
        achado = bruto_mais_recente(raiz_bruto, fonte_id)
        if achado is None:
            _log.warning("intl | %s | sem bruto para reprocessar", fonte_id)
            comparacao[fonte_id] = {"anterior": anterior, "novo": None, "igual": False}
            continue
        caminho, meta = achado
        try:
            coletado_em = datetime.strptime(meta["coletado_em"], FORMATO_COLETA).replace(
                tzinfo=timezone.utc
            )
            bruto = BrutoIntl(
                caminho.read_bytes(), meta["url"], meta.get("versao_fonte"), caminho.suffix[1:]
            )
            entrada = _processar(
                build_source(fonte_id), fonte_id, bruto, coletado_em, saida, meta["sha256_bruto"]
            )
        except Exception as erro:
            _log.warning("intl | %s | reprocessamento falhou | %s", fonte_id, erro)
            comparacao[fonte_id] = {"anterior": anterior, "novo": None, "igual": False}
            continue
        comparacao[fonte_id] = {
            "anterior": anterior,
            "novo": entrada["sha256"],
            "igual": anterior == entrada["sha256"],
        }
        manifesto["fontes"][fonte_id] = entrada
    _gravar_dimensao(saida)
    gravar_manifesto(saida, manifesto)
    return comparacao
