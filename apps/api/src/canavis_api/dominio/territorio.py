from dataclasses import dataclass


@dataclass(frozen=True)
class Uf:
    sigla: str
    cod_ibge: str


COD_IBGE_POR_SIGLA: dict[str, str] = {
    "RO": "11",
    "AC": "12",
    "AM": "13",
    "RR": "14",
    "PA": "15",
    "AP": "16",
    "TO": "17",
    "MA": "21",
    "PI": "22",
    "CE": "23",
    "RN": "24",
    "PB": "25",
    "PE": "26",
    "AL": "27",
    "SE": "28",
    "BA": "29",
    "MG": "31",
    "ES": "32",
    "RJ": "33",
    "SP": "35",
    "PR": "41",
    "SC": "42",
    "RS": "43",
    "MS": "50",
    "MT": "51",
    "GO": "52",
    "DF": "53",
}


def uf_por_sigla(sigla: str) -> Uf | None:
    normalizada = sigla.strip().upper()
    cod_ibge = COD_IBGE_POR_SIGLA.get(normalizada)
    if cod_ibge is None:
        return None
    return Uf(normalizada, cod_ibge)
