"""De-para das cinco microrregiões canavieiras para a divisão regional de 2017.

Os pares foram conferidos no serviço de localidades do IBGE em 29/10/2026.
Uma microrregião antiga pode cruzar mais de uma região nova; nesses casos,
``imediata``/``intermediaria`` ficam ``None`` e as opções constam nas listas.
As listas são descritivas, não uma licença para replicar totais da microrregião.
"""

CONFIRMACAO_FONTE_OFICIAL_PENDENTE = False

MICRORREGIOES_CANAVIEIRAS: dict[str, dict] = {
    "Litoral Norte - PB": {
        "imediatas": (("250001", "João Pessoa"), ("250003", "Mamanguape - Rio Tinto")),
        "intermediarias": (("2501", "João Pessoa"),),
    },
    "Litoral Sul - PB": {
        "imediatas": (("250001", "João Pessoa"),),
        "intermediarias": (("2501", "João Pessoa"),),
    },
    "Sapé - PB": {
        "imediatas": (("250001", "João Pessoa"), ("250004", "Itabaiana")),
        "intermediarias": (("2501", "João Pessoa"),),
    },
    "João Pessoa - PB": {
        "imediatas": (("250001", "João Pessoa"),),
        "intermediarias": (("2501", "João Pessoa"),),
    },
    "Brejo Paraibano - PB": {
        "imediatas": (("250002", "Guarabira"), ("250005", "Campina Grande")),
        "intermediarias": (("2501", "João Pessoa"), ("2502", "Campina Grande")),
    },
}


def regiao_de(microrregiao: str) -> dict:
    """Retorna regiões e códigos oficiais; relação singular só quando unívoca."""
    try:
        regioes = MICRORREGIOES_CANAVIEIRAS[microrregiao]
    except KeyError as erro:
        disponiveis = ", ".join(sorted(MICRORREGIOES_CANAVIEIRAS))
        raise KeyError(
            f"Microrregião '{microrregiao}' não está no de-para canavieiro. "
            f"Esperadas: {disponiveis}."
        ) from erro
    imediatas = regioes["imediatas"]
    intermediarias = regioes["intermediarias"]
    imediata = imediatas[0] if len(imediatas) == 1 else (None, None)
    intermediaria = intermediarias[0] if len(intermediarias) == 1 else (None, None)
    return {
        "imediata": imediata[1],
        "intermediaria": intermediaria[1],
        "cod_imediata": imediata[0],
        "cod_intermediaria": intermediaria[0],
        "imediatas": imediatas,
        "intermediarias": intermediarias,
    }
