# 0002 — IBGE e CONAB como base; ANP como contexto; Comex fora

**Status:** Aceita

## Contexto

O produto precisa de dados públicos, reais e verificáveis. Durante a descoberta, cinco fontes
foram avaliadas e testadas por coleta direta.

## Decisão

- **IBGE PAM (Tabela 1612):** base principal. Produtividade em nível municipal, série longa,
  API estável. Coletada.
- **CONAB Série Histórica da Cana:** base principal para a camada industrial (açúcar, etanol,
  ATR) por UF e safra. Coletada.
- **ANP (vendas e produção de etanol):** contexto de demanda e produção industrial. Coletada;
  o arquivo municipal traz código IBGE, o que permite junção limpa com a PAM.
- **Comex Stat (exportação):** fora do escopo desta etapa. A API existe, mas está protegida por
  verificação anti-robô (Cloudflare com desafio de JavaScript). Acessá-la exigiria automação de
  navegador, desproporcional para uma fonte apenas de contexto.
- **Novo CAGED (emprego setorial):** localizado, não coletado. Candidato a etapa futura.

## Consequências

A pergunta de decisão principal é respondida com IBGE e CONAB. A ANP enriquece a leitura sem
ser essencial. Comex e CAGED ficam registrados como ampliação possível, com o motivo da
exclusão documentado para a arguição.
