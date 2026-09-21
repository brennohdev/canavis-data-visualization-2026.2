# 0004 — Granularidade de trabalho e janela temporal confiável

**Status:** Aceita
**Evidência:** `notebooks/01_qualidade_dados.ipynb`

## Contexto

Antes de validar ou minerar indicadores, era preciso saber em que nível territorial e em que
recorte temporal os dados sustentam análise honesta. A PAM suprime valores de municípios com
poucos produtores, e a série de 21 anos pode conter mudanças de regime que distorcem a leitura
de tendência.

## Evidência

**Supressão por nível (taxa de ausentes do rendimento, 2003–2023):**

| Nível | Ausentes | Unidades com série completa | Completude média |
|-------|----------|-----------------------------|------------------|
| Município | 62% | 58 de 120 | 71% |
| Microrregião | 36% | 13 de 17 | 86% |
| UF | 0% | 27 de 27 | 100% |

**Regime da série (rendimento da Paraíba):**

- Inclinação 2003–2012: **−502 kg/ha por ano** (queda)
- Inclinação 2013–2023: **+666 kg/ha por ano** (alta)
- Inclinação da série inteira: +396 kg/ha por ano — número que **esconde** a inversão
- Coeficiente de variação: 7,7% (volatilidade moderada, discrimina regiões)
- 2023 é um pico atípico da PB (+15% no ano, contra +1% a +7% nas demais UFs canavieiras)

## Decisão

1. **Granularidade por tipo de análise:**
   - Retrato de um ano (ranking, participação): **município**, com ausências marcadas como
     "sem informação", nunca como zero.
   - Série de longo prazo (tendência, volatilidade, resiliência): **microrregião**, único nível
     abaixo da UF com completude alta o bastante.
   - Benchmarking nacional: **UF**.

2. **Janela temporal para tendência:** usar janela recente (por padrão, os últimos dez anos)
   em vez da série inteira, porque a série contém inversão de regime. A tendência global de
   21 anos é estatisticamente enganosa.

3. **Tratamento de 2023:** sinalizar como pico atípico da Paraíba onde ele aparecer, para não
   induzir leitura de salto estrutural onde há recuperação pontual.

## Consequências

Os indicadores de longo prazo que serão minerados na fase seguinte nascem no nível de
microrregião e sobre janela recente. Isso descarta, desde já, a ideia de um ranking municipal
de tendência — seria indefensável com 62% de supressão. Falhar aqui é barato; falhar na Etapa 3
seria caro.
