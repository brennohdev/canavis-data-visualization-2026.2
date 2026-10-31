from __future__ import annotations

from pathlib import Path

import pandas as pd

from canavis import storage
from canavis.config import load_settings
from canavis.logging import get_logger

_log = get_logger(__name__)

_MISSING_TOKENS = {"-", "..", "...", "X"}

# Tokens de ausência do SIDRA/IBGE mapeados para a classificação semântica.
# A classificação vem SEMPRE do token publicado pelo IBGE, NUNCA do porte do
# município (uma ausência não é inferida a partir do tamanho da localidade).
_TOKENS_AUSENCIA = {
    "-": "sem_producao",      # zero absoluto: o fenômeno não existe (produção real zero)
    "...": "suprimido",       # dado numérico não disponível (inclui sigilo estatístico)
    "X": "suprimido",         # valor omitido para não identificar o informante
    "..": "outra_condicao",   # não se aplica à célula
}


def classificar_ausencia(valor) -> str:
    """Classifica um valor cru da PAM segundo a convenção de tokens do IBGE.

    Retorna um de quatro rótulos ASCII (snake_case), estáveis para uso a jusante
    (Power BI, testes):

    - ``"presente"``        — valor numérico informado;
    - ``"sem_producao"``    — token ``-`` (zero absoluto, o fenômeno não existe);
    - ``"suprimido"``       — token ``...`` (dado não disponível/sigilo) ou ``X``
      (omitido para não identificar o informante);
    - ``"outra_condicao"``  — token ``..`` (não se aplica) ou ausência sem token
      semântico (``None``, ``NaN``, ``pd.NA``, string vazia ou só espaços).

    A classificação deriva exclusivamente do token publicado pelo IBGE; ela NUNCA
    é atribuída a partir do porte do município. É isso que separa "sem produção"
    (zero real) de "suprimido" (dado sonegado), colapsados na Etapa 1.
    """
    if valor is None or valor is pd.NA:
        return "outra_condicao"
    try:
        if pd.isna(valor):
            return "outra_condicao"
    except (TypeError, ValueError):
        pass

    bruto = str(valor).strip()
    if bruto == "":
        return "outra_condicao"

    # O token literal é checado ANTES de qualquer limpeza numérica: remover os
    # pontos de ``-``/``..``/``...`` os colapsaria em string vazia e perderia a
    # semântica. Só depois tentamos interpretar o valor como número.
    if bruto in _TOKENS_AUSENCIA:
        return _TOKENS_AUSENCIA[bruto]

    numerico = bruto.replace(".", "").replace(",", ".")
    convertido = pd.to_numeric(numerico, errors="coerce")
    if pd.notna(convertido):
        return "presente"
    return "outra_condicao"


def transform_all() -> dict[str, Path]:
    """Camada silver: padroniza tipos e valores ausentes em data/interim."""
    settings = load_settings()

    transformers = {
        "ibge_pam": _transform_ibge,
        "conab_cana": _transform_conab,
        "anp_vendas_etanol": _transform_anp_vendas,
        "anp_producao_etanol": _transform_anp_producao,
    }

    written: dict[str, Path] = {}
    for key, transformer in transformers.items():
        if not storage.exists(settings.paths.raw, key):
            _log.warning("silver | %s | ausente em raw, pulando", key)
            continue
        frame = transformer(storage.read(settings.paths.raw, key))
        destination = storage.write(frame, settings.paths.interim, key)
        _log.info("silver | %s | %d linhas | %s", key, len(frame), destination.name)
        written[key] = destination
    return written


def _to_numeric(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")
    cleaned = series.astype(str).str.strip().replace(_MISSING_TOKENS, pd.NA)
    cleaned = cleaned.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(cleaned, errors="coerce")


def _transform_ibge(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    # Classifica o valor cru ANTES da conversão numérica, para distinguir
    # "sem produção" (zero real) de "suprimido" — as duas ausências que a
    # Etapa 1 colapsava num único balde descartado.
    frame["situacao_valor"] = frame["valor"].map(classificar_ausencia).astype("string")
    frame["valor"] = _to_numeric(frame["valor"])
    # Token ``-`` representa produção zero de fato: vira 0.0, não NA.
    frame.loc[frame["situacao_valor"] == "sem_producao", "valor"] = 0.0
    frame["periodo"] = pd.to_numeric(frame["periodo"], errors="coerce").astype("Int64")
    # Nenhuma linha é descartada: as três situações de ausência são preservadas
    # via ``situacao_valor`` para que o downstream/Power BI as distinga.
    return frame


def _transform_conab(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    text_columns = {"ano_agricola", "dsc_safra_previsao", "uf", "produto", "dsc_situacao_levantamento"}
    for column in frame.columns:
        if column in text_columns:
            frame[column] = frame[column].astype("string").str.strip()
        else:
            frame[column] = _to_numeric(frame[column])
    return frame


def _transform_anp_vendas(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [c.lower().replace(" ", "_") for c in frame.columns]
    frame["vendas"] = _to_numeric(frame["vendas"])
    return frame


def _transform_anp_producao(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [c.lower().replace(" ", "_") for c in frame.columns]
    frame["produção"] = _to_numeric(frame["produção"])
    return frame
