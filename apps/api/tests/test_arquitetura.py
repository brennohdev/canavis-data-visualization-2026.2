import ast
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1] / "src" / "canavis_api"
STDLIB = set(sys.stdlib_module_names)


def _importacoes(arquivo: Path) -> set[str]:
    nomes: set[str] = set()
    for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8"))):
        if isinstance(no, ast.Import):
            nomes.update(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
    return nomes


def _arquivos(pasta: str) -> list[Path]:
    return sorted((RAIZ / pasta).rglob("*.py"))


def _permitido(modulo: str, prefixos: tuple[str, ...]) -> bool:
    return modulo.split(".")[0] in STDLIB or modulo.startswith(prefixos)


@pytest.mark.parametrize(
    ("pasta", "prefixos"),
    [
        ("dominio", ("canavis_api.dominio",)),
        ("aplicacao", ("canavis_api.dominio", "canavis_api.aplicacao")),
    ],
)
def test_camadas_internas_so_dependem_do_permitido(pasta, prefixos):
    for arquivo in _arquivos(pasta):
        for modulo in _importacoes(arquivo):
            assert _permitido(modulo, prefixos), f"{arquivo.name} importa {modulo}"


def test_duckdb_fica_em_repositorios():
    for arquivo in RAIZ.rglob("*.py"):
        if "repositorios" in arquivo.relative_to(RAIZ).parts:
            continue
        assert "duckdb" not in {m.split(".")[0] for m in _importacoes(arquivo)}, arquivo.name


def test_main_nao_referencia_configuracao():
    texto = (RAIZ / "main.py").read_text(encoding="utf-8").lower()
    for proibido in ("settings", "environ", "canavis_"):
        assert proibido not in texto.replace("canavis_api", "")
