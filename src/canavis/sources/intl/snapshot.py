from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from canavis import storage
from canavis.sources.intl.esquema import COLUNAS, FORMATO_COLETA

VERSAO_MANIFESTO = 1
NOME_MANIFESTO = "manifest.json"
COLUNAS_DADOS = [c for c in COLUNAS if c not in ("coletado_em", "defasagem_dias")]


def hash_quadro(frame: pd.DataFrame) -> str:
    ordenado = frame[COLUNAS].sort_values(["serie_id", "data"], kind="stable")
    resumo = hashlib.sha256()
    resumo.update(",".join(COLUNAS).encode("utf-8") + b"\n")
    for linha in ordenado.itertuples(index=False):
        campos = [
            str(linha.serie_id),
            pd.Timestamp(linha.data).strftime("%Y-%m-%d"),
            repr(float(linha.valor)),
            str(linha.unidade),
            str(linha.fonte_id),
            pd.Timestamp(linha.coletado_em).strftime(FORMATO_COLETA),
            str(int(linha.defasagem_dias)),
            str(linha.licenca),
        ]
        resumo.update(",".join(campos).encode("utf-8") + b"\n")
    return resumo.hexdigest()


def hash_dados(frame: pd.DataFrame) -> str:
    ordenado = frame[COLUNAS_DADOS].sort_values(["serie_id", "data"], kind="stable")
    resumo = hashlib.sha256()
    resumo.update(",".join(COLUNAS_DADOS).encode("utf-8") + b"\n")
    for linha in ordenado.itertuples(index=False):
        campos = [
            str(linha.serie_id),
            pd.Timestamp(linha.data).strftime("%Y-%m-%d"),
            repr(float(linha.valor)),
            str(linha.unidade),
            str(linha.fonte_id),
            str(linha.licenca),
        ]
        resumo.update(",".join(campos).encode("utf-8") + b"\n")
    return resumo.hexdigest()


def hash_bytes(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def gravar_snapshot(frame: pd.DataFrame, saida: Path, fonte_id: str) -> Path:
    return storage.write(frame, saida, fonte_id)


def salvar_bruto(
    raiz: Path,
    fonte_id: str,
    conteudo: bytes,
    extensao: str,
    url: str,
    versao_fonte: str | None,
    coletado_em: datetime,
) -> Path:
    pasta = raiz / fonte_id
    pasta.mkdir(parents=True, exist_ok=True)
    carimbo = coletado_em.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destino = pasta / f"{carimbo}.{extensao}"
    destino.write_bytes(conteudo)
    meta = {
        "url": url,
        "coletado_em": coletado_em.astimezone(timezone.utc).strftime(FORMATO_COLETA),
        "versao_fonte": versao_fonte,
        "sha256_bruto": hash_bytes(conteudo),
    }
    destino.with_name(f"{carimbo}.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return destino


def bruto_mais_recente(raiz: Path, fonte_id: str) -> tuple[Path, dict] | None:
    pasta = raiz / fonte_id
    if not pasta.is_dir():
        return None
    metas = sorted(pasta.glob("*.meta.json"))
    if not metas:
        return None
    meta_path = metas[-1]
    prefixo = meta_path.name.removesuffix(".meta.json")
    candidatos = [p for p in pasta.glob(f"{prefixo}.*") if not p.name.endswith(".meta.json")]
    if not candidatos:
        return None
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    return candidatos[0], meta


def ler_manifesto(saida: Path) -> dict:
    caminho = saida / NOME_MANIFESTO
    if not caminho.exists():
        return {"versao_manifesto": VERSAO_MANIFESTO, "gerado_em": None, "fontes": {}}
    return json.loads(caminho.read_text(encoding="utf-8"))


def gravar_manifesto(saida: Path, manifesto: dict) -> Path:
    saida.mkdir(parents=True, exist_ok=True)
    manifesto["versao_manifesto"] = VERSAO_MANIFESTO
    manifesto["gerado_em"] = datetime.now(timezone.utc).strftime(FORMATO_COLETA)
    caminho = saida / NOME_MANIFESTO
    caminho.write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return caminho
