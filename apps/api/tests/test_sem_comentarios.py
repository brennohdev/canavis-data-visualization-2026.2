import ast
import io
import tokenize
from pathlib import Path

APPS_API = Path(__file__).resolve().parents[1]
ARQUIVOS = sorted([*(APPS_API / "src").rglob("*.py"), *(APPS_API / "tests").rglob("*.py")])


def _comentarios(arquivo: Path) -> list[int]:
    fonte = arquivo.read_text(encoding="utf-8")
    return [
        token.start[0]
        for token in tokenize.generate_tokens(io.StringIO(fonte).readline)
        if token.type == tokenize.COMMENT
    ]


def _docstrings(arquivo: Path) -> list[str]:
    arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
    tipos = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    return [
        getattr(no, "name", "modulo")
        for no in ast.walk(arvore)
        if isinstance(no, tipos) and ast.get_docstring(no, clean=False) is not None
    ]


def test_ha_arquivos_para_varrer():
    assert len(ARQUIVOS) > 5


def test_zero_comentarios():
    achados = {arquivo.name: _comentarios(arquivo) for arquivo in ARQUIVOS}
    assert {nome: linhas for nome, linhas in achados.items() if linhas} == {}


def test_zero_docstrings():
    achados = {arquivo.name: _docstrings(arquivo) for arquivo in ARQUIVOS}
    assert {nome: itens for nome, itens in achados.items() if itens} == {}
