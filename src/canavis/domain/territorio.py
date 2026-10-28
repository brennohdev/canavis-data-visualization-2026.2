from __future__ import annotations

"""De-para territorial: microrregião (divisão antiga) × regiões geográficas.

Regra de agrupamento estável da série
-------------------------------------
A série da PAM vai de 2003 a 2023. Em 2017 o IBGE substituiu a divisão de
meso/microrregiões pela Divisão Regional do Brasil (DRB 2017), com as novas
regiões geográficas **imediatas** e **intermediárias**. Como a microrregião é a
unidade que aparece em TODA a série e é o único nível sub-UF com completude alta
o bastante (ADR 0004), ela permanece a **chave estável de agrupamento** de
2003–2023. Este de-para NÃO troca a chave: serve para *comparar* a leitura antiga
com as divisões novas, respondendo ao feedback da Etapa 1 sobre recorte
territorial, sem reprocessar a série sob uma divisão que só existe a partir de
2017.

As cinco microrregiões canavieiras vêm do ADR 0007 (98% da produção da PB):
Litoral Norte, Litoral Sul, Sapé, João Pessoa e Brejo.

Confirmação em fonte oficial
----------------------------
O mapeamento é feito ao nível de **nome**. A Paraíba tem uma única região
geográfica intermediária relevante para a cana ("João Pessoa"); as imediatas são
nomeadas conforme a DRB 2017. Os pares abaixo precisam de confirmação na fonte
oficial do IBGE (DRB 2017) — a flag ``CONFIRMACAO_FONTE_OFICIAL_PENDENTE`` marca
isso explicitamente. **Nenhum código oficial foi inventado**: quando o código não
pôde ser verificado nos dados locais, o campo fica ``None``.
"""

# Marca que os pares nome→nome ainda não foram confirmados na fonte oficial do
# IBGE (Divisão Regional do Brasil 2017). Nenhum código oficial foi inventado.
CONFIRMACAO_FONTE_OFICIAL_PENDENTE = True

# Chaves usam o nome exato como aparece na coluna ``local`` do parquet da PAM
# (extracao == "serie_microrregioes_pb"), para casar direto com o dado cru.
MICRORREGIOES_CANAVIEIRAS: dict[str, dict] = {
    "Litoral Norte - PB": {
        "imediata": "Mamanguape",
        "intermediaria": "João Pessoa",
        "cod_imediata": None,
        "cod_intermediaria": None,
    },
    "Litoral Sul - PB": {
        "imediata": "João Pessoa",
        "intermediaria": "João Pessoa",
        "cod_imediata": None,
        "cod_intermediaria": None,
    },
    "Sapé - PB": {
        "imediata": "João Pessoa",
        "intermediaria": "João Pessoa",
        "cod_imediata": None,
        "cod_intermediaria": None,
    },
    "João Pessoa - PB": {
        "imediata": "João Pessoa",
        "intermediaria": "João Pessoa",
        "cod_imediata": None,
        "cod_intermediaria": None,
    },
    "Brejo Paraibano - PB": {
        "imediata": "Guarabira",
        "intermediaria": "João Pessoa",
        "cod_imediata": None,
        "cod_intermediaria": None,
    },
}


def regiao_de(microrregiao: str) -> dict:
    """Devolve as regiões geográficas imediata e intermediária da microrregião.

    O parâmetro ``microrregiao`` deve ser o nome como aparece na coluna ``local``
    da PAM (ex.: ``"Sapé - PB"``). Retorna um dicionário com as chaves
    ``imediata``, ``intermediaria``, ``cod_imediata`` e ``cod_intermediaria``
    (códigos ``None`` enquanto pendentes de confirmação oficial).

    Levanta ``KeyError`` se a microrregião não estiver no de-para das canavieiras.
    """
    try:
        return dict(MICRORREGIOES_CANAVIEIRAS[microrregiao])
    except KeyError as erro:
        disponiveis = ", ".join(sorted(MICRORREGIOES_CANAVIEIRAS))
        raise KeyError(
            f"Microrregião '{microrregiao}' não está no de-para canavieiro. "
            f"Esperadas: {disponiveis}."
        ) from erro
