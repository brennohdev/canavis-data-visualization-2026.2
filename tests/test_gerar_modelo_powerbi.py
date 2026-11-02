import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "gerar_modelo_powerbi.py"
TABELAS = [
    "fato_producao",
    "fato_producao_uf",
    "fato_producao_microrregiao",
    "fato_producao_municipio",
    "fato_industria",
    "fato_vendas_etanol_uf",
    "fato_vendas_etanol_municipio",
    "dim_territorio",
    "dim_calendario",
    "dim_fonte",
]


def _carregar_script():
    spec = importlib.util.spec_from_file_location("gerar_modelo_powerbi", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture(scope="module")
def modelo():
    """Regenera o TMDL a partir dos Parquet locais e devolve o texto."""
    _carregar_script().main()
    return (ROOT / "powerbi/modelo.tmdl").read_text(encoding="utf-8")


def test_url_base_configuravel():
    modulo = _carregar_script()
    assert modulo.URL_BASE == (
        "https://raw.githubusercontent.com/brennohdev/"
        "canavis-data-visualization-2026.2/main/data/processed"
    )


@pytest.mark.parametrize("nome", TABELAS)
def test_tabela_le_por_web_contents(modelo, nome):
    esperado = (
        'Parquet.Document(Web.Contents("https://raw.githubusercontent.com/'
        f'brennohdev/canavis-data-visualization-2026.2/main/data/processed/{nome}.parquet"))'
    )
    assert esperado in modelo


def test_sem_file_contents_nem_caminho_de_maquina(modelo):
    assert "File.Contents" not in modelo
    assert "C:\\Users" not in modelo
    assert "/Users/" not in modelo


def test_dim_territorio_sem_fallback_de_tier(modelo):
    assert "Table.HasColumns" not in modelo
    assert "Table.AddColumn" not in modelo


def test_dezessete_medidas_e_vinte_e_uma_relacoes(modelo):
    assert modelo.count("measure '") == 17
    assert modelo.count("\trelationship ") == 21


_COLUNAS_TEMPORAIS = [
    "tendencia_t_ha", "oscilacao_t_ha", "f_chow", "p_chow",
    "status_chow", "ponto_candidato_quebra", "quebra_confirmada",
]


def _bloco_tabela(modelo, nome):
    import re

    inicio = modelo.index(f"\ttable {nome}\n")
    resto = modelo[inicio + 1:]
    proximo = re.search(r"\n\ttable ", resto)
    return resto[: proximo.start()] if proximo else resto


def test_municipio_por_nivel_sem_colunas_temporais(modelo):
    municipio = _bloco_tabela(modelo, "fato_producao_municipio")
    uf = _bloco_tabela(modelo, "fato_producao_uf")
    micro = _bloco_tabela(modelo, "fato_producao_microrregiao")
    for coluna in _COLUNAS_TEMPORAIS:
        assert f"sourceColumn: {coluna}" not in municipio
        assert f"sourceColumn: {coluna}" in uf
        assert f"sourceColumn: {coluna}" in micro


def test_descricoes_e_fatores_atr_presentes(modelo):
    assert "/// " in modelo
    for fator in ("1.0495", "1.7651", "1.6913"):
        assert fator in modelo
