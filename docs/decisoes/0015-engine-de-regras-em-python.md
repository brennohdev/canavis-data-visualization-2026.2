# 0015 — Engine de regras de texto em Python e vocabulário calibrado

**Status:** Proposta
**Evidência:** `docs/entrega-etapa3/planejamento-etapa3.md` (seções 5 e 7.5)
**Ancora em:** ADR 0003, ADR 0009/0011 (sem quebra confirmada)

## Contexto
Os textos dinâmicos (descrever, destacar, sugerir) dependem de desvio vs grupo, tiers, FDR e
cobertura, que já vivem em Python e SQL.

## Decisão
- Regras como funções puras em `src/canavis/domain/regras/`, sem IO, expostas por
  `GET /api/v1/insights`. O front só renderiza.
- Cada insight retorna `{regra_id, funcao, texto, severidade, evidencias, limitacoes}`.
- Limiares em `config/regras.yaml`, tratados como hipótese a calibrar com o demandante.
- Vocabulário de observação ("houve", "ficou", "está"); nunca causal ou garantidor.
  Toda comparação traz referência e ano; hedge obrigatório com evidência exploratória.
- Testes: `pytest` parametrizado por regra e caso-limite, textos dourados (golden) e teste
  que proíbe verbos como "falhou", "culpa", "causou", "garante".

## Alternativa rejeitada
Engine em TypeScript no front: reage sem ida ao servidor, mas duplica cálculos e dificulta
testar com dados reais. O slider usa debounce de 250 ms.
