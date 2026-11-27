# Matriz de cobertura

> Gerado por `scripts/gerar_matriz_cobertura.py`. Não editar à mão. A tabela completa está em `data/processed/matriz_cobertura.parquet`.

## Último ano com dado presente por fonte

| fonte_id | Fonte | Último ano |
|---|---|---|
| `anp_vendas_etanol` | ANP | 2024 |
| `conab_cana` | CONAB | 2026 |
| `ibge_pam_1612` | IBGE PAM | 2023 |

## Linhas por fonte, nível e situação

| fonte_id | nível | presente | sem_producao | suprimido | sem_registro |
|---|---|---|---|---|---|
| `anp_vendas_etanol` | uf | 945 | 0 | 0 | 0 |
| `conab_cana` | uf | 470 | 0 | 0 | 124 |
| `ibge_pam_1612` | microrregiao | 307 | 176 | 0 | 0 |
| `ibge_pam_1612` | municipio | 1797 | 2860 | 26 | 0 |
| `ibge_pam_1612` | uf | 567 | 0 | 0 | 0 |

## Municípios da Paraíba em 2023 (PAM)

| Situação | Municípios |
|---|---|
| presente | 82 |
| sem_producao | 140 |
| suprimido | 1 |
| sem_registro | 0 |

`sem_producao` é zero registrado pela fonte. `suprimido` é valor omitido por sigilo. `sem_registro` é combinação sem linha na fonte e nunca vira zero.
