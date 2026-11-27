from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

_CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class HttpSettings:
    timeout_seconds: int
    user_agent: str


@dataclass(frozen=True)
class LayerPaths:
    raw: Path
    interim: Path
    processed: Path

    def ensure_exist(self) -> None:
        for path in (self.raw, self.interim, self.processed):
            path.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class StorageSettings:
    format: str
    compression: str


@dataclass(frozen=True)
class Settings:
    http: HttpSettings
    paths: LayerPaths
    storage: StorageSettings
    log_level: str
    log_format: str


def _read_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@lru_cache
def load_settings() -> Settings:
    raw = _read_yaml(_CONFIG_DIR / "settings.yaml")
    paths = raw["paths"]
    return Settings(
        http=HttpSettings(**raw["http"]),
        paths=LayerPaths(
            raw=_PROJECT_ROOT / paths["raw"],
            interim=_PROJECT_ROOT / paths["interim"],
            processed=_PROJECT_ROOT / paths["processed"],
        ),
        storage=StorageSettings(**raw["storage"]),
        log_level=raw["logging"]["level"],
        log_format=raw["logging"]["format"],
    )


@lru_cache
def load_sources() -> dict[str, dict]:
    return _read_yaml(_CONFIG_DIR / "sources.yaml")


def source_config(key: str) -> dict:
    sources = load_sources()
    if key not in sources:
        raise KeyError(f"Fonte '{key}' não encontrada em sources.yaml")
    return sources[key]


_CHAVES_INDICADOR = (
    "id", "nome", "definicao", "formula", "unidade", "sentido", "fonte", "niveis",
    "funcao", "tratamento_ausencia", "limitacoes",
)
_SENTIDOS = {"maior_melhor", "menor_melhor", "neutro"}
_CHAVES_PARAMETRO = ("valor", "unidade", "status", "origem")


def _validar_indicadores(bruto: dict) -> dict:
    for chave in ("versao", "parametros", "indicadores"):
        if chave not in bruto:
            raise ValueError(f"Chave '{chave}' ausente em indicadores.yaml")
    for nome, parametro in bruto["parametros"].items():
        faltantes = [c for c in _CHAVES_PARAMETRO if c not in parametro]
        if faltantes:
            raise ValueError(f"Parâmetro '{nome}' sem as chaves {faltantes}")
    ids = set()
    for indicador in bruto["indicadores"]:
        rotulo = indicador.get("id", "?")
        faltantes = [c for c in _CHAVES_INDICADOR if c not in indicador]
        if faltantes:
            raise ValueError(f"Indicador '{rotulo}' sem as chaves {faltantes}")
        if indicador["sentido"] not in _SENTIDOS:
            raise ValueError(f"Indicador '{rotulo}' com sentido inválido: {indicador['sentido']!r}")
        if not indicador["limitacoes"]:
            raise ValueError(f"Indicador '{rotulo}' sem limitações")
        if rotulo in ids:
            raise ValueError(f"Indicador '{rotulo}' duplicado")
        ids.add(rotulo)
    return bruto


def carregar_indicadores_de(path: Path) -> dict:
    return _validar_indicadores(_read_yaml(path))


@lru_cache
def load_indicadores() -> dict:
    return carregar_indicadores_de(_CONFIG_DIR / "indicadores.yaml")
