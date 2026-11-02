from __future__ import annotations

"""Normalização canônica de texto para padronizar nomes na camada gold.

Princípio (separação valor de exibição × forma canônica):

- O **valor de exibição** preserva acentuação e caixa natural (``"João Pessoa"``,
  ``"Água Branca - PB"``). É o que o painel mostra ao humano — acento é
  informação, não ruído.
- A **forma canônica** (``sem_acento``) remove acentuação e dobra a caixa para
  uma chave estável de busca, ordenação e junção, sem perder o original.

Essa dupla é o padrão ``display label`` × ``normalized form``: nenhuma grafia é
descartada, e toda comparação/junção técnica passa pela forma canônica. As
funções são puras (sem IO), vivem no domínio e são reutilizadas por todo o
pipeline em vez de espalhar ``str.replace``/``unicodedata`` ponto a ponto.
"""

import unicodedata

import pandas as pd


def sem_acento(valor) -> str | None:
    """Remove acentuação preservando a caixa e os separadores do nome.

    ``"João Pessoa"`` → ``"Joao Pessoa"``; ``"Água Branca - PB"`` →
    ``"Agua Branca - PB"``. Mantém espaços, hífens e caixa (serve de rótulo
    auxiliar legível, não de slug). Retorna ``None`` para ausência (``None``,
    ``pd.NA``, ``NaN`` ou string vazia), nunca converte ausência em texto.
    """
    if valor is None or valor is pd.NA:
        return None
    try:
        if pd.isna(valor):
            return None
    except (TypeError, ValueError):
        pass
    texto = str(valor).strip()
    if texto == "":
        return None
    decomposto = unicodedata.normalize("NFKD", texto)
    return decomposto.encode("ascii", "ignore").decode("ascii")


def sem_acento_series(serie: pd.Series) -> pd.Series:
    """Aplica :func:`sem_acento` a uma série, preservando o índice e os NA."""
    return serie.map(sem_acento).astype("string")


def chave_nome(valor) -> str | None:
    """Forma canônica agressiva para JUNÇÃO de nomes (não para exibição).

    Remove acento, descarta tudo que não for letra/dígito e dobra para
    maiúsculas: ``"Água Branca - PB"`` → ``"AGUABRANCAPB"`` (sem o sufixo de UF,
    quando presente, fica a cargo de quem chama cortar antes). Usada só para
    casar chaves entre fontes com grafias divergentes, nunca como rótulo.
    """
    base = sem_acento(valor)
    if base is None:
        return None
    return "".join(ch for ch in base.upper() if ch.isalnum())
