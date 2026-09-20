# 0001 — Organizar os dados em camadas bronze/silver/gold

**Status:** Aceita

## Contexto

O projeto evolui por três etapas sobre a mesma base de dados: descoberta (agora), protótipo em
Power BI e aplicação em Dash. Cada etapa consome o dado tratado. Sem uma separação clara, cada
etapa rebaixaria os dados da fonte e repetiria a limpeza.

## Decisão

Adotar três camadas físicas em `data/`:

- **raw (bronze):** dado cru, exatamente como veio da fonte. Permite reprocessar sem rebaixar.
- **interim (silver):** limpo, tipado e com valores ausentes padronizados.
- **processed (gold):** pronto para consumo, com indicadores já calculados.

## Consequências

O Power BI (Etapa 2) e o Dash (Etapa 3) leem a camada processed sem recalcular nada. O custo é
manter três cópias do dado, mitigado por `data/` ser ignorado no versionamento (só a estrutura
e as amostras pequenas ficam no repositório).
