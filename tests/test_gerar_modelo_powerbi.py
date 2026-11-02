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


def test_contagem_de_medidas_e_relacoes(modelo):
    # 33 medidas = 7 no fato_producao empilhado (retrocompat)
    #            + 7 (UF) + 6 (microrregião, sem Desvio vs grupo)
    #            + 3 (município: Produtividade, Participação, Desvio vs seleção)
    #            + 6 em fato_industria (3 razões + 3 ATR: equiv. açúcar/etanol, shares)
    #              na verdade: 3 razões + 2 ATR-equiv + 2 shares + 1 Situação mix = 8
    #            + 1 Vendas UF + 1 Vendas município.
    # 7+7+6+3+8+1+1 = 33.
    assert modelo.count("measure '") == 33
    # 21 relações = 7 fatos x 3 dimensões (territorio, calendario, fonte).
    assert modelo.count("\trelationship ") == 21


def test_medidas_cabiveis_por_granularidade(modelo):
    # Desvio vs grupo depende de tier: só UF (e o empilhado), nunca micro/município.
    assert "measure 'Desvio vs grupo (UF)'" in modelo
    assert "measure 'Desvio vs grupo (microrregião)'" not in modelo
    assert "measure 'Desvio vs grupo (município)'" not in modelo
    # Série temporal: UF e microrregião, nunca município (sem colunas temporais).
    assert "measure 'Tendência histórica (t por ha) (microrregião)'" in modelo
    assert "measure 'Tendência histórica (t por ha) (município)'" not in modelo
    assert "measure 'P Chow exploratório (2003-2023) (município)'" not in modelo
    # Produtividade existe nos três níveis, lendo o próprio fato.
    for sufixo, fato in [("(UF)", "fato_producao_uf"),
                         ("(microrregião)", "fato_producao_microrregiao"),
                         ("(município)", "fato_producao_municipio")]:
        assert f"measure 'Produtividade {sufixo}'" in modelo
        assert f"SUM({fato}[quantidade_produzida_t])" in modelo


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
