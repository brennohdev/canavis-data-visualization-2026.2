# 0020 — Parâmetros de cenário sem projeção

**Status:** Proposta
**Evidência:** `docs/entrega-etapa3/planejamento-etapa3.md` (seção 4)
**Ancora em:** ADR 0009/0011, ADR 0010

## Decisão
Parâmetros são hipóteses de leitura, não previsões.
- **P1 Meta de produtividade da PB** (slider de 40 a 100 t/ha, passo 1), puramente PAM.
- **P2 Preço do açúcar em reais:** US$/t = ICE (US¢/lb) x 22,0462; R$/t = US$/t x PTAX.
  Aritmética de conversão e variação, sem modelo. Todo texto traz a ressalva "não é previsão".
- **P3 Referência de comparação** (seleção, grupo, participação), herdada da Etapa 2.
- Janela da tendência (5, 10, 21 anos) é filtro, não cenário.
- O sinal de mercado é contexto para metas e para levar uma pergunta ao comercial; nunca
  "mude o mix" (coerência com o enquadramento descartado na Etapa 1).
- Paridade açúcar x etanol fica fora: falta preço do etanol na gold e a licença do CEPEA é
  não comercial.
- Tela com cenário ativo mostra selo "Cenário" e botão "voltar ao realizado".
