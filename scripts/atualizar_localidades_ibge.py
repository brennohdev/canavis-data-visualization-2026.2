"""Atualiza o recorte territorial da PB a partir da API oficial de localidades do IBGE."""

from pathlib import Path

import pandas as pd
import requests


URL = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/25/municipios"
DESTINO = Path(__file__).resolve().parents[1] / "data/reference/municipios_pb_ibge.parquet"


def main() -> None:
    resposta = requests.get(URL, timeout=60)
    resposta.raise_for_status()
    linhas = []
    for municipio in resposta.json():
        micro = municipio["microrregiao"]
        imediata = municipio["regiao-imediata"]
        intermediaria = imediata["regiao-intermediaria"]
        linhas.append(
            {
                "cod_municipio": str(municipio["id"]),
                "cod_microrregiao": str(micro["id"]),
                "cod_regiao_imediata": str(imediata["id"]),
                "nome_regiao_imediata": imediata["nome"],
                "cod_regiao_intermediaria": str(intermediaria["id"]),
                "nome_regiao_intermediaria": intermediaria["nome"],
                "cod_uf": str(intermediaria["UF"]["id"]),
            }
        )
    frame = pd.DataFrame(linhas).sort_values("cod_municipio").reset_index(drop=True)
    if len(frame) != 223 or frame["cod_municipio"].duplicated().any():
        raise ValueError("Resposta inesperada da API de localidades da PB")
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(DESTINO, index=False, compression="zstd")
    print(f"{len(frame)} municípios gravados em {DESTINO}")


if __name__ == "__main__":
    main()
