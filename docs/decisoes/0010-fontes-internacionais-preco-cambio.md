# 0010 — Fontes internacionais de preço, câmbio e balanço por país

**Status:** Aceita como direção para a **Etapa 3** (não entra na Etapa 2 — ver "Escopo e timing")
**Origem:** feedback do professor (Etapa 2) + contexto da persona na entrevista
**Evidência:** `.agents/tasks/fontes-internacionais/relatorio-viabilidade.md` (estresse de tentativa, requisição HTTP real por fonte)

## Contexto

O feedback do professor na Etapa 2 foi explícito: os dados internacionais de preço da cana/açúcar
são **públicos**, alguns em **tempo real**, e a defasagem de ~1 ano da PAM (ADR 0004) **deixa de ser
desvantagem** se o painel trouxer sinal recente internacional, porque o demandante decide com base
nesse sinal e no **dólar**. O diagnóstico da Etapa 1 havia descartado o internacional por falta de
tentativa — o mesmo erro que a "Nota de honestidade" do `docs/mapeamento_dados.md` admite ter
cometido com a ANP (descarte por chute de URL).

A persona, na entrevista, reforçou o recorte: acompanha **sempre** o preço e os dados dos
países-referência da cana — explicitamente **Índia, Tailândia e China** (além do Brasil; UE e EUA
como referência). Índia e Tailândia são os maiores exportadores depois do Brasil; safra, política de
exportação e estoques desses países movem o preço internacional que a persona observa.

Este ADR registra o resultado do estresse de tentativa exaustivo e fixa o escopo de fontes
internacionais **antes de ampliar o produto**, como o professor pediu ("não ampliem o escopo sem
esse diagnóstico").

## Evidência

Cada fonte abaixo foi testada com requisição HTTP real (`curl`/`python3`), não por chute de URL. O
relatório completo traz endpoint, comando, status, amostra de payload, frequência, janela e licença
por fonte. Resumo do veredito:

| Papel | Fonte | O que entrega | Frequência | Veredito |
|-------|-------|---------------|-----------|----------|
| Núcleo | **BCB — SGS série 1 (PTAX dólar venda)** | Câmbio BRL/USD oficial | Diária | **ACESSÍVEL** (aberto) |
| Núcleo | **Yahoo Finance `SB=F`** | Açúcar bruto ICE Nº 11 (futuro) | Tempo quase real / diário | **ACESSÍVEL** (aberto) |
| Núcleo | **FRED `PSUGAISAUSDM`** | Preço mundial do açúcar (ISA), US$/lb | Mensal (defasagem ~1–2 meses) | **ACESSÍVEL** (aberto) |
| Núcleo | **World Bank Pink Sheet (CMO)** | Açúcar mundo/EU/EUA, histórico longo | Mensal | **ACESSÍVEL** (aberto) |
| Núcleo | **CFTC Commitments of Traders** | Posição de traders no Açúcar Nº 11 (expectativa) | Semanal | **ACESSÍVEL** (aberto) |
| Núcleo país | **USDA FAS — PSD "Sugar, Centrifugal" (bulk CSV)** | Produção/exportação/estoques/consumo por país (Índia, Tailândia, China, Brasil, UE, EUA) com **ano corrente** | Por safra | **ACESSÍVEL** (bulk, sem chave) |
| Contexto | **CEPEA/ESALQ** | Etanol BR, açúcar PB/SP, **paridade de exportação** | Diária/semanal | **ACESSÍVEL** (licença **NÃO COMERCIAL**) |
| Contexto | **BCB Olinda PTAX (OData)** | Câmbio com boletins intradiários | Intradiário | **ACESSÍVEL** (aberto) |
| Contexto | **UN Comtrade (preview)** | Export/import de açúcar HS 1701 por país | Anual/mensal, defasado | **ACESSÍVEL** (preview) / cadastro p/ volume |
| Cadastro | **EIA** (etanol/combustíveis EUA) | Preço/produção de etanol nos EUA | Semanal/mensal | **COM-CADASTRO** (API key grátis) |
| Cadastro | **USDA NASS QuickStats / WASDE** | Balanço de açúcar, estimativas de safra | Mensal | **COM-CADASTRO** (API key grátis) |
| Histórico | **FAOSTAT (bulk)** | Produção de cana/açúcar por país | Anual, defasagem ~1 ano | **ACESSÍVEL via bulk** (API ao vivo deu HTTP 521) |
| Redundante | **IMF Primary Commodity Prices** | Preço de commodities | Mensal | **ACESSÍVEL** (redundante com FRED/WB) |
| Fora | **ISO (International Sugar Organization)** | Yearbook / World Sugar Balance | — | **PAGO/MEMBROS** (sem feed aberto) |
| Bloqueado | **Stooq** | CSV de futuros | Diária | **BLOQUEADO** (proof-of-work JS) |
| Bloqueado | **Nasdaq Data Link / Quandl** | Datasets CHRIS/ICE_SB1 | Diária | **BLOQUEADO** (Incapsula anti-bot) |
| Gated | **B3 (futuros etanol ETH)** | Futuros de etanol Brasil | Diária (atraso) | Público só com atraso/feed registrado |

Pontos de evidência que mais importam:

- **Sinal recente de preço:** Yahoo `SB=F` retornou cotação do açúcar ICE Nº 11 em tempo quase real
  (amostra em out/2026); o FRED `PSUGAISAUSDM` fecha o mês com ~1–2 meses de defasagem — muito melhor
  que o ~1 ano da PAM.
- **Países-referência com ano corrente:** o bulk CSV do USDA FAS PSD (152 mil linhas, sem cadastro)
  traz Índia/Tailândia/China/Brasil até o **Market Year 2026** (safra corrente + estimativa). É
  **sinal recente**, não retrato defasado — materializa exatamente o acompanhamento que a persona
  declarou fazer.
- **Câmbio oficial:** BCB SGS série 1 (PTAX), diário, série longa, fonte primária correta para um
  projeto brasileiro.
- **Lição ANP aplicada:** o CEPEA respondeu HTTP 403 ao primeiro GET e abriu (HTTP 200) ao usar
  `User-Agent` de navegador — não foi descartado no 403. Onde o bloqueio era real (Stooq, Nasdaq),
  a evidência do mecanismo (proof-of-work JS, Incapsula) foi registrada, como se fez com o Comex.

## Decisão

### Escopo recomendado para a Etapa 3

**Núcleo (integrar; acesso aberto, sem cadastro):**

1. **BCB SGS série 1 (PTAX dólar)** — câmbio diário oficial; base da conversão US$→R$.
2. **Yahoo `SB=F`** — açúcar bruto ICE Nº 11; sinal recente/tempo quase real. Peça central contra a
   defasagem.
3. **FRED `PSUGAISAUSDM`** (+ **World Bank Pink Sheet** como histórico e para o branco EU) — açúcar
   mensal, cruzável por safra.
4. **CFTC COT (Açúcar Nº 11)** — camada de expectativa/posicionamento (semanal); responde ao
   "preços, expectativas e contratos futuros".
5. **USDA FAS PSD "Sugar, Centrifugal" (bulk CSV)** — balanço por país (Índia, Tailândia, China,
   Brasil, UE, EUA) com o ano corrente. Materializa o acompanhamento dos países-referência.

**Contexto (integrar com ressalva):**

6. **CEPEA/ESALQ** (etanol BR, açúcar PB/SP, **paridade de exportação**) — liga externo↔interno;
   exige `User-Agent` de navegador e respeito à **licença de uso NÃO COMERCIAL** (uso acadêmico com
   atribuição; esta ressalva é condição da integração).
7. **UN Comtrade (preview)** — fluxo bilateral de exportação por país; complementa o PSD quando se
   quiser valor/peso, mais defasado.
8. **BCB Olinda PTAX** — apenas se o painel quiser cotação intradiária.

**Fora desta rodada (com justificativa):**

- **FAOSTAT** — produção por país é anual e defasada ~1 ano (mesma dor da PAM) e a API ao vivo deu
  HTTP 521; o PSD já cobre produção por país com o ano corrente. Só como série histórica via bulk, se
  necessário.
- **EIA** e **USDA QuickStats** — exigem API key e são centrados nos EUA; entram só se o etanol
  internacional virar foco.
- **IMF Primary Commodity Prices** — redundante com FRED/World Bank.
- **ISO** — dados estruturados são pagos/membros; o preço ISA que importa já vem de graça do
  FRED/World Bank.
- **B3 futuros de etanol** — público só com atraso/feed registrado; o CEPEA cobre o etanol interno
  abertamente.
- **Política de exportação da Índia** — sem API estável; contexto qualitativo (anotação no painel).
  O efeito já aparece, quantitativo, nas linhas de Exports/Ending Stocks da Índia no PSD.
- **Stooq**, **Nasdaq Data Link/Quandl** — **BLOQUEADOS** por desafio JS/anti-bot; não insistir sem
  navegador headless.

### Eixo de junção com a série nacional

- **Ano/safra:** o açúcar mensal (FRED/WB) agrega-se por safra para casar com PAM/CONAB; o PSD e a
  CONAB já falam em safra, a PAM em ano civil (alinhamento de calendário já tratado no ADR 0004).
- **Câmbio:** converter preço externo US$→R$ com a PTAX, aproximando a paridade de exportação que o
  CEPEA (SP mercado externo) publica.

A narrativa que o painel passa a sustentar: *safra fraca na Índia/Tailândia + estoques baixos → preço
ICE sobe → convertido pelo dólar → paridade de exportação melhora → sinal para a persona direcionar o
mix açúcar/etanol*.

## Escopo e timing — por que Etapa 3, não Etapa 2

A Etapa 2 **já está fechada no design** (telas, modelo de dados e medidas definidos — ver
`docs/entrega-etapa2/`). Introduzir fontes internacionais agora exigiria reabrir o modelo de dados e o
layout, o que não é adequado a esta altura. Portanto esta decisão é registrada como **direção para a
Etapa 3**: o diagnóstico de viabilidade está feito e o escopo fixado, para que a ampliação entre de
forma controlada na próxima etapa, sem retrabalho do design atual.

## Consequências

- O argumento do professor sobre a defasagem fica respondido **com evidência testada**: há conjunto
  público e recente (preço + câmbio + balanço por país com ano corrente) que compensa o atraso da PAM.
  A PAM passa a ser o retrato estrutural de fundo, não a fonte de atualidade.
- Nenhuma alteração foi feita em `config/sources.yaml` nem em código de produção nesta decisão — é
  diagnóstico e direção. A implementação dos adapters (BCB, Yahoo `SB=F`, FRED, World Bank, CFTC, USDA
  PSD) fica para a Etapa 3, quando será registrada em ADR de implementação próprio.
- A **licença não comercial do CEPEA** é uma restrição explícita: se o produto evoluir para uso
  comercial, essa fonte precisa ser reavaliada ou substituída.
- Fica documentado, para a arguição, quais fontes foram testadas, quais acessam e quais estão
  bloqueadas (com a evidência do bloqueio), no padrão de honestidade do `mapeamento_dados.md`.
