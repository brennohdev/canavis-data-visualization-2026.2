from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import pytest

from canavis.sources.intl import snapshot
from canavis.sources.intl.esquema import COLUNAS, calcular_defasagem, validar


def _quadro(valor: float = 1.5) -> pd.DataFrame:
    coletado = pd.Timestamp("2026-11-27T12:00:00Z")
    return pd.DataFrame(
        {
            "serie_id": ["a", "a", "b"],
            "data": pd.to_datetime(["2026-01-02", "2026-01-01", "2026-01-01"]),
            "valor": [valor, 2.0, 3.0],
            "unidade": ["u", "u", "v"],
            "fonte_id": ["f", "f", "f"],
            "coletado_em": [coletado] * 3,
            "defasagem_dias": [329, 330, 330],
            "licenca": ["livre"] * 3,
        }
    )[COLUNAS]


def test_hash_igual_para_o_mesmo_quadro_em_ordem_diferente():
    quadro = _quadro()
    embaralhado = quadro.iloc[::-1].reset_index(drop=True)
    assert snapshot.hash_quadro(quadro) == snapshot.hash_quadro(embaralhado)


def test_hash_muda_quando_um_valor_muda():
    assert snapshot.hash_quadro(_quadro(1.5)) != snapshot.hash_quadro(_quadro(1.6))


def test_hash_sobrevive_ao_ciclo_parquet(tmp_path):
    quadro = _quadro()
    caminho = snapshot.gravar_snapshot(quadro, tmp_path, "f")
    assert caminho.name == "f.parquet"
    assert snapshot.hash_quadro(pd.read_parquet(caminho)) == snapshot.hash_quadro(quadro)


def test_manifesto_ida_e_volta(tmp_path):
    assert snapshot.ler_manifesto(tmp_path)["fontes"] == {}
    manifesto = {"fontes": {"f": {"sha256": "abc", "status": "ok", "erro": None}}}
    snapshot.gravar_manifesto(tmp_path, manifesto)
    lido = snapshot.ler_manifesto(tmp_path)
    assert lido["fontes"] == manifesto["fontes"]
    assert lido["versao_manifesto"] == snapshot.VERSAO_MANIFESTO
    assert lido["gerado_em"]


def test_bruto_salvo_e_recuperado_com_meta(tmp_path):
    coletado = datetime(2026, 11, 27, 12, 0, 0, tzinfo=timezone.utc)
    antigo = datetime(2026, 11, 26, 12, 0, 0, tzinfo=timezone.utc)
    snapshot.salvar_bruto(tmp_path, "f", b"velho", "csv", "http://x", None, antigo)
    caminho = snapshot.salvar_bruto(tmp_path, "f", b"novo", "csv", "http://x", "v1", coletado)
    achado, meta = snapshot.bruto_mais_recente(tmp_path, "f")
    assert achado == caminho
    assert achado.read_bytes() == b"novo"
    assert meta["coletado_em"] == "2026-11-27T12:00:00Z"
    assert meta["versao_fonte"] == "v1"
    assert meta["sha256_bruto"] == snapshot.hash_bytes(b"novo")
    assert snapshot.bruto_mais_recente(tmp_path, "outra") is None


def test_defasagem_em_dias():
    datas = pd.Series(pd.to_datetime(["2026-11-26", "2026-11-01"]))
    coletado = datetime(2026, 11, 27, 12, 0, 0, tzinfo=timezone.utc)
    assert calcular_defasagem(datas, coletado).tolist() == [1, 26]


def test_validar_aceita_quadro_correto_e_rejeita_defeitos():
    assert len(validar(_quadro())) == 3
    with pytest.raises(ValueError):
        validar(_quadro().drop(columns=["licenca"]))
    with pytest.raises(ValueError):
        validar(_quadro().iloc[0:0])
    duplicado = pd.concat([_quadro(), _quadro().iloc[:1]], ignore_index=True)
    with pytest.raises(ValueError):
        validar(duplicado)
    infinito = _quadro()
    infinito.loc[0, "valor"] = float("inf")
    with pytest.raises(ValueError):
        validar(infinito)
