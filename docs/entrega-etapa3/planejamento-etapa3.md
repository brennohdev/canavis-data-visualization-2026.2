# CanaVis — Planejamento da Etapa 3 (relatório de varredura)

Investigação somente leitura. Nenhum código de produção foi alterado. O backlog de issues está em `backlog.json` (mesma pasta). Prazo exato da entrega no Moodle: **desconhecido** (registrado como risco R1 e pergunta P1).

> **Atualizações posteriores à varredura (Etapa 3, novembro de 2026).** (1) Prazo no Moodle: **01/12/2026**; meta interna **27/11/2026** (README do projeto). R1 e P1 estão resolvidos. (2) O professor **confirmou a stack** (ADR 0013). R2 e P2 estão resolvidos. (3) Os passos 3 e 5 da jornada foram revisados com dados da gold: a versão vigente está em `jornada-e-rotas.md` (seção 7) e `design-system.md`, e as seções 2, 3, 5 e 8 abaixo foram corrigidas. Evidência: `scripts/analise_tendencia_base_municipal.py`. O texto original das seções corrigidas não foi preservado aqui; está no histórico do git.

## 0. Resposta curta

1. **Stack:** confirmo a recomendação **React + TypeScript (Vite) no front e FastAPI + DuckDB sobre os parquet da gold no back**, empacotados em **um único contêiner** (FastAPI serve a API e o build estático do React). Isso captura, no mesmo desenho, os extras 3 (DuckDB com consulta parametrizada), 4 (API própria e consumo de APIs externas) e 5 (publicação), além de resolver "sobe com um comando" (`docker compose up`).
2. **Engine de textos dinâmicos:** funções puras **em Python** (`src/canavis/domain/regras/`), expostas por `GET /api/v1/insights`. O front só renderiza. Motivo: os cálculos que alimentam as regras (desvio vs grupo, tiers, FDR, cobertura) já vivem em Python e em SQL, e a regra de dependência do ADR 0003 (domínio sem IO) já existe. Os testes de caso-limite ficam em `pytest` parametrizado.
3. **Backlog:** 20 issues no formato "Task N" da Etapa 2, 4 marcos (M1 a M4), com esqueleto andante já em M1 (inclui deploy público inicial). As trilhas (dados, backend, modelagem, design, frontend, qualidade/entrega) são labels; o detalhe fino está nos checklists.
4. **Maior risco de nota (trava em 3,0):** rotas com URL como fonte de verdade e teste do "link copiado em outra aba". Está coberto por Task 8, Task 8 e Task 8, todos em M1/M2, antes de qualquer gráfico sofisticado.
5. **Tensão a resolver com o demandante:** a Etapa 1 descartou "recomendar mix" por ser decisão comercial (enquadramento 2). O professor (ADR 0010) quer o sinal internacional. A proposta é usar o sinal de mercado como **contexto para metas, prioridades e para levar uma pergunta à área comercial**, nunca como "mude o mix".

---

## 1. Persona e decisões (fonte: Etapa 1 e entrevista)

Fontes: `docs/entrega-etapa1/Etapa1_Cordeiro_Alex.tex` (seções Persona, Jornada, Critérios de sucesso, Perguntas analíticas) e `docs/entrevista/roteiro-e-anotacoes.md`; teste da Etapa 2 em `docs/entrega-etapa2/teste-usuario.md`.

| Campo | O que os documentos dizem |
|---|---|
| Quem | "Ricardo Meneses" (nome fictício): gerente agrícola de usina na Paraíba, engenheiro agrônomo (UFPE), 5 anos na função. Responde por agrícola, transporte e logística, oficina e segurança do trabalho. |
| Decisões | Plantio, tratos culturais e manejo da colheita (agosto a março); manutenção e logística; **contribui** para o mix açúcar x etanol, decidido a cada safra por preço de mercado (peso comercial, clima, produção de outros países, política de combustíveis). |
| Cadência | Uso **pontual, ligado ao ciclo da safra**: planejamento anual e revisão antes de reuniões de programação. Não é uso diário. |
| Letramento | Alto (Power BI, Excel, tabelas dinâmicas). Refaz análises à mão quando o sistema não entrega o corte. |
| Dor | Informação comparativa dispersa, em boa parte paga ("todos os sistemas são pagos"), montada manualmente. |
| Pergunta de decisão | "Como a produtividade e a produção da minha região se comparam às de outras regiões e como esse posicionamento evoluiu ao longo das safras?" |
| Ações esperadas (Etapa 1, seção j) | Priorizar área e plantio; reavaliar fornecedores; revisar metas de safra com base no posicionamento. |
| Sinais pedidos depois | Teste da Etapa 2: quis **dólar e preços internacionais**; sentiu falta de dado por usina (privado, fora de escopo). Entrevista (ADR 0010): acompanha Índia, Tailândia e China, além de Brasil, UE e EUA. |

**Critérios de sucesso declarados na Etapa 1 (a retomar no teste de aceitação):**
1. **Tempo:** levantamento comparativo que hoje exige várias fontes e planilha passa a ser resolvido em uma consulta de poucos minutos.
2. **Comportamento:** a persona consulta o produto antes das reuniões de planejamento de safra, em vez de recorrer só a boletins pagos.
3. **Decisão:** o posicionamento deixa de ser lido "de memória" e passa a ter número com referência explícita.
4. **Custo:** parte da leitura comparativa hoje assinada passa a ser coberta por fonte pública.

**A confirmar com o demandante** (nada disso está nos documentos): (a) quais desvios ele considera relevantes (os limiares da seção 5 são hipóteses do time); (b) se a unidade de tempo natural é a safra (os dados são anuais; o enunciado cita "trimestre" apenas como exemplo); (c) se ele aceita ver o sinal de mercado como contexto e não como recomendação de mix; (d) quem na usina decide o mix e se o relatório da ferramenta chega a essa pessoa; (e) disponibilidade para o teste de aceitação.

---

## 2. Cenários de decisão

Formato: situação -> o que ele vê -> decisão -> resultado. "PAM" = só IBGE (sem dado internacional). "INT" = depende dos dados internacionais. Dados citados vêm de `docs/entrega-etapa2/*` e ADRs; onde o valor ainda precisa ser calculado na Etapa 3, está marcado.

| # | Cenário | Dados | Depende de INT? |
|---|---|---|---|
| S1 | Planejamento de plantio: onde priorizar área | PAM microrregião + tier | Não |
| S2 | Revisão de meta de safra | PAM UF/micro + parâmetro "meta" | Não |
| S3 | Base de cana: em quais municípios está a área | PAM município (área e quantidade) | Não |
| S4 | Dólar e açúcar ICE sobem: vale levar a pauta de mix à reunião? | PTAX, ICE, CONAB share ATR | **Sim** |
| S5 | Safra fraca na Índia/Tailândia e estoques baixos | USDA PSD, ICE, COT | **Sim** |
| S6 | 2023 foi pico: a meta deve subir? | PAM série, médias por fase, inclinação com intervalo | Não |
| S7 | Cobertura insuficiente: o app recusa recomendar | cobertura por fonte/território | Não |
| S8 | Véspera da reunião de programação: resumo em 10 minutos | `/prioridades` + link compartilhável | Opcional |

**S1 — Planejamento de plantio (PAM sozinha).**
- Situação: antes do planejamento anual, ele quer saber quais microrregiões da PB estão perdendo posição.
- Vê: `/uf/PB` com séries de produtividade por microrregião (múltiplos pequenos), inclinação na janela de 10 anos com intervalo de confiança e classe (sobe, estável ou cai; só sobe ou cai se o intervalo exclui zero), e a leitura: "Microrregião X: produtividade 2023 de A t/ha, B% abaixo da média da PB; inclinação de C t/ha/ano (IC 95% de D a E; janela 2013-2023)". Ação sugerida: "vale revisar a priorização de área nessa microrregião; confira a área colhida antes (D ha)".
- Decide: reorientar esforço de tratos e renovação para as microrregiões em queda ou adiar expansão onde a base é pequena.
- Resultado: priorização com número e referência (critério de sucesso 3), em minutos (critério 1).
- Não pode afirmar: causa da queda, produtividade futura, quebra estrutural (ADR 0009/0011: PB não sobrevive ao FDR, p ajustado 0,0606). Série de 21 pontos.

**S2 — Meta de safra (PAM).** Parâmetro "meta de produtividade (t/ha)". Ele vê a distância entre o realizado e a meta, e onde a meta está na distribuição histórica (percentil) e entre pares do tier. Decide se a meta é ambiciosa demais ("meta acima do máximo observado da PB na série") ou conservadora. Não afirma probabilidade de atingir a meta.

**S3 — Base de cana por município (PAM, só PB).** Retrato de um ano. Em 2023, 82 dos 223 municípios produzem cana, 140 têm produção zero registrada (`sem_producao`, ADR 0008) e 1 está suprimido; os "62% ausentes" do ADR 0004 misturam zero real e supressão (errata no ADR 0004). Ele vê os municípios ordenados por **área colhida**, com participação na área da PB, e "82 de 223 municípios produzem cana; os demais têm produção zero". Decide em quais municípios concentrar a atenção ao conversar com fornecedores, usando dado próprio da usina. Não afirma quem fornece à usina (dado privado), nem que um município é mais produtivo que outro: a produtividade municipal tem poucos valores distintos (13 entre 82 municípios em 2023, 39% em 65,0 t/ha) e a quantidade deriva dela. Não afirma que município com zero registrado "produz pouco". Quando restam menos de 5 municípios produtores, o app recusa ranking.

**S4 — Dólar sobe e ICE sobe (INT).**
- Situação: câmbio e açúcar ICE em alta no trimestre. A PB tem perfil etanoleiro (27,54% de açúcar em ATR em 2023/24, abaixo de SP 55,4%, MG 50,3% etc., `auditoria-medidas-dax.md`).
- Vê: `/cenarios` com preço do açúcar em R$/t (ICE x PTAX) e variação em 90 dias contra o nível base; faixa histórica do share de açúcar da PB (mínimo e máximo observados desde 2005/06, como **indício** de capacidade, não restrição conhecida); texto: "o açúcar em reais subiu X% em 90 dias; a PB destinou Y% do ATR a açúcar em 2023/24 e já chegou a Z% em safra anterior".
- Decide: levar à reunião com o comercial a pergunta "vale revisar o mix?", com o dado em mãos. **Não** decide o mix.
- Resultado: pauta preparada em minutos, com fonte e defasagem visíveis.
- Não pode afirmar: paridade açúcar x etanol (falta preço do etanol no escopo aberto; CEPEA é não comercial e precisa de checagem de acesso), capacidade da usina, preço futuro, causalidade.

**S5 — Safra fraca na Índia/Tailândia (INT).** Vê produção, exportação e estoques finais por país (USDA PSD, ano de safra corrente), variação contra a safra anterior, e o ICE no mesmo período. Texto: "o USDA estima estoques finais da Índia X% menores que na safra anterior; o ICE variou Y% no período". Decide ajustar a expectativa de contexto de preço (reunião de planejamento, orçamento). Não afirma que um causa o outro. Há risco de licença/acesso do PSD: validar em Task 7.

**S6 — Pico de 2023 (PAM).** A PB subiu cerca de 15% em 2023, contra 1% a 7% nas outras UFs canavieiras (ADR 0004). Ele vê o alerta "2023 destoa do padrão da série (variação de +15% contra desvio-padrão histórico de Z%)" e vê a média por fase (50,9 t/ha em 2003-12 e 55,0 t/ha em 2013-22) com 2023 destacado (64,7 t/ha), e consegue mudar a janela da inclinação (5, 10 ou 21 anos). Nas janelas de 5 e 10 anos o intervalo de confiança da PB inclui zero (classe "estável"), e sem 2023 a inclinação de 2013 a 2022 é +0,30 t/ha/ano, contra +0,67 com 2023. Decide não ancorar a meta no pico. Não afirma "novo patamar" nem "anomalia por clima" (ADR 0007 rejeitou chuva).

**S7 — Recusa por cobertura insuficiente.** Ele filtra uma microrregião com mais de metade da série ausente, ou uma UF sem dado CONAB. O app mostra o estado "dado insuficiente", diz o que falta ("12 de 21 anos sem informação") e **não gera ação sugerida**. Isso é critério de qualidade, não falha: demonstra que as regras têm limiar mínimo.

**S8 — Resumo de véspera.** Em `/prioridades` ele vê os 3 casos prioritários da safra (ranking de achados por relevância e cobertura), cada um com ação sugerida e link. Esse é o desenho da tarefa do teste de aceitação.

**Separação PAM x INT.** S1, S2, S3, S6, S7 funcionam só com PAM e CONAB. S4 e S5 dependem de BCB, ICE, FRED e USDA. Se uma fonte internacional cair, as telas de PAM não devem sofrer (degradação graciosa, Task 7).

---

## 3. Jornada do usuário, rotas e persistência de filtros

### 3.1 Jornada (passo a passo)

| Passo | Gatilho | Pergunta | Tela | Ação | Resultado |
|---|---|---|---|---|---|
| 1 | Reunião de programação em 2 dias | "Como estamos frente aos pares?" | `/` | Abre; lê KPIs e a leitura do recorte | Posição da PB (desvio vs grupo) com referência explícita |
| 2 | Estranha o desvio | "Contra quem estou me comparando?" | `/` | Troca a referência (seleção, grupo, participação) | Entende que a leitura muda com a referência |
| 3 | Quer a evolução | "Está melhorando ou foi 2023?" | `/uf/PB` | Lê a média por fase com 2023 destacado; abre a inclinação com intervalo (5, 10 ou 21 anos) como apoio | Fase e pico separados; "sobe" ou "cai" só com intervalo que exclui zero; aviso de quebra não confirmada |
| 4 | Quer localizar o problema | "Quais microrregiões caem?" | `/uf/PB` -> `/microrregiao/:id` | Clica na microrregião (drill) | Série, referência e ação sugerida |
| 5 | Quer saber onde está a base de cana | "Onde está a cana na PB?" | `/municipios` | Ordena por área colhida; filtra micro e área mínima | Participação na área da PB; zero real separado de suprimido; sem ranking de produtividade |
| 6 | Sinal de mercado | "O açúcar subiu em reais?" | `/mercado` | Lê câmbio, ICE, países | Contexto com data e fonte |
| 7 | Hipótese | "E se a meta for 65?" | `/cenarios` | Mexe nos parâmetros | Leitura muda; cenário vira link |
| 8 | Prepara pauta | "Quais 3 casos levo?" | `/prioridades` | Copia o link | Resumo reabre idêntico em outro lugar |
| 9 | Dúvida de confiança | "De onde vem isso?" | `/metodologia` | Lê definições e limitações | Confiança calibrada |

### 3.2 Tabela 3.1 (proposta): rotas

| Rota | Conteúdo | Parâmetros aceitos | Como o usuário chega |
|---|---|---|---|
| `/` | Panorama nacional: KPIs, mapa e barras divergentes por UF, leitura do recorte | `ano`, `ref` (`selecao`\|`grupo`\|`participacao`), `tier`, `ind` (`produtividade`\|`participacao`\|`mix`), `janela` | Abertura; clique no logo |
| `/uf/:sigla` (parâmetro de caminho) | Série por fase, inclinação com intervalo, microrregiões da UF, leitura | `ano`, `ref`, `janela`, `meta` | Clique em UF no mapa/barras de `/` |
| `/microrregiao/:cod` (parâmetro de caminho) | Série e referência da microrregião, municípios | `ano`, `janela` | Clique em microrregião em `/uf/PB` |
| `/municipios` | Base de cana dos municípios da PB: área, participação e quantidade (só PB) | `ano`, `micro`, `area_min`, `ordem`, `pagina` | Botão em `/uf/PB`; clique na microrregião |
| `/municipio/:cod` (parâmetro de caminho) | Retrato e série curta do município, com ausentes | `ano` | Clique na linha de `/municipios` |
| `/cenarios` | Parâmetros de hipótese e comparação base x alternativos | `uf`, `ano`, `meta`, `cambio`, `ice`, `janela`, `ref`, `base` | Menu; botão "simular" em `/uf/:sigla` |
| `/mercado` | Câmbio, ICE, balanço por país, COT, status das fontes | `periodo` (`3m`\|`12m`\|`5a`), `paises` (lista) | Menu; link no texto de cenário |
| `/prioridades` | 3 casos prioritários com ação sugerida | `ano`, `uf`, `n` | Menu; abertura recomendada |
| `/metodologia` (+ `#indicador`) | Fontes, definições, limitações, licenças, atualização | `ind` (âncora) | Rodapé de todas as telas e botão "?" na leitura |

Regras de URL: valor igual ao padrão é omitido (URLs curtas). Parâmetro inválido ou fora de faixa **não gera erro**: cai no padrão e a tela avisa "ajustamos o parâmetro X". O teste de aceitação do requisito (a) copia a URL e abre em aba anônima; Task 8 automatiza isso.

### 3.3 Persistência de filtros (requisito b)

Controles globais: `ano`, território em foco (UF), `tier`, `ref`, `ind`, `janela`. Controles de cenário: `meta`, `cambio`, `ice`. Controles locais: `micro`, `area_min`, `ordem`, `pagina`.

| Controle | Navegação Panorama -> UF -> micro -> município | Para `/cenarios` | Para `/mercado` | Para `/metodologia` | Justificativa |
|---|---|---|---|---|---|
| `ano` | Persiste | Persiste | Não se aplica (usa `periodo`) | Reinicia | O ano é o eixo de leitura de toda a decisão |
| `ref` | Persiste até `/uf`; some em micro/município (tier não existe nesses níveis, ADR 0006) mas fica na URL e **volta** ao retornar | Persiste | Reinicia | Reinicia | Mantém a leitura coerente; só esconde onde não faz sentido |
| `tier` | Persiste em `/` e `/uf`; irrelevante abaixo | Persiste | Reinicia | Reinicia | Tier só existe para UF |
| `janela` | Persiste | Persiste | Reinicia | Reinicia | Altera a inclinação; mudar sem avisar enganaria |
| `ind` | Persiste | Reinicia (cenário tem indicador próprio) | Reinicia | Âncora | Evita indicador "preso" |
| `meta`, `cambio`, `ice` | Persistem **na sessão da URL** em `/uf` e `/cenarios`; reiniciam em `/` | Origem | `cambio` e `ice` persistem | Reinicia | Hipótese não pode "vazar" para a leitura do realizado sem rótulo |
| `micro`, `area_min`, `ordem`, `pagina` | Reiniciam ao trocar de nível ou de ano (paginação volta à 1) | Reinicia | Reinicia | Reinicia | Filtros locais valem só para a lista |
| Seleção de entidade (`:sigla`, `:cod`) | Muda por clique (drill-through) | Entra como `uf` | Reinicia | Reinicia | O caminho é parte do estado |

Toda tela com parâmetro de cenário ativo mostra um selo "Cenário: meta 65 t/ha" e botão "voltar ao realizado".

---

## 4. Parâmetros de cenário (Tabela 3.2)

**Não há projeção de produtividade.** A série tem 21 pontos e o ADR 0009/0011 não confirma quebra; projetar seria "confiança fabricada". Os parâmetros são **hipóteses de leitura**, não previsões.

Parâmetros propostos (3, dois obrigatórios para a demo):

- **P1 Meta de produtividade da PB (t/ha)** — *principal e puramente PAM*. Slider de 40 a 100 (faixa já sugerida em `cenarios.md`), passo 1.
- **P2 Preço do açúcar em reais (câmbio BRL/USD x ICE US¢/lb)** — *sensibilidade de contexto*. Dois controles (câmbio e ICE), com os valores do dia como base.
- **P3 Referência de comparação** (já existente da Etapa 2: seleção, grupo, participação) — mantém a continuidade da trajetória e mostra que a leitura muda sem mexer no dado.
- Janela de leitura da tendência (5, 10, 21 anos) é filtro, não cenário, mas aparece no teste da inversão de regime.

**Tabela 3.2 (rascunho; valores marcados "a calcular" serão gerados por Task 11):**

| Cenário | Valor do parâmetro | O que muda | Leitura e implicação para a persona |
|---|---|---|---|
| **Base (P1)** | Meta = média do tier "média escala" em 2023 (aprox. 62,6 t/ha, derivada de 64,69 e +3,41%) | Distância da PB à meta: aprox. +2,1 t/ha acima | A PB já está acima da média dos pares; a meta é de manutenção. |
| **Alt. 1 (P1)** | Meta = média nacional (aprox. 77,9 t/ha, derivada de −16,96%) | Distância: aprox. −13,2 t/ha | Meta inalcançável em curto prazo e dominada por SP (56,8% da produção). Sugere não adotar a média nacional como meta. |
| **Alt. 2 (P1)** | Meta = máximo observado da PB em 2013-2023 (a calcular) | Percentil e distância | Mostra se a meta exigiria superar o próprio pico; alerta quando a meta está acima de qualquer valor da série. |
| **Base (P2)** | Câmbio e ICE do último dia disponível (a calcular) | Preço do açúcar em R$/t e variação em 90 dias | Referência de contexto. |
| **Alt. 1 (P2)** | Câmbio +10% (a calcular) | Preço em R$ sobe 10% se ICE constante | Leitura de sensibilidade; texto exige a ressalva "não é previsão". |
| **Alt. 2 (P2)** | ICE -15% com câmbio constante (a calcular) | Preço em R$ cai | Sinaliza quando o contexto deixa de favorecer o açúcar; conversa com o comercial. |

Valor de P2: US$/t = ICE (US¢/lb) x 22,0462; R$/t = US$/t x PTAX. Fórmula simples, auditável, sem modelo.

**Vale ter sensibilidade a preço/câmbio?** Sim, mas só nesta forma (aritmética de conversão e variação), porque é o que o professor sugeriu (ADR 0010) e o que a persona pediu. **Não** vale construir paridade açúcar x etanol sem preço do etanol: o preço do etanol não está na gold; a fonte aberta citada (CEPEA) tem licença não comercial e acesso a confirmar. Ficou como stretch (nota em Task 11), não como requisito.

---

## 5. Regras de texto dinâmico (rascunho da Tabela 3.3)

Funções: **D** descrever, **H** destacar, **A** sugerir ação. Todos os limiares ficam em `config/regras.yaml` (a calibrar com o demandante) e valem como hipótese. Vocabulário: verbos de observação ("houve", "ficou", "está"), nunca causais ("falhou", "por causa de"); toda comparação traz a referência e o ano; hedge obrigatório quando a evidência é exploratória.

| ID | Fn | Condição (limiar) | Modelo de texto | Caso-limite |
|---|---|---|---|---|
| R01 | D | Seleção com >= 1 registro | "Recorte: {território}, {ano}. Produtividade de {x} t/ha ({fonte}, dado de {ano_dado})." | **Seleção vazia:** "Nenhum registro atende a esta combinação de filtros. Tente: remover o grupo (tier), escolher outro ano ou ampliar a janela." |
| R02 | D | Referência ativa | "Referência: média de {k} UFs do grupo {tier}." | **k < 5:** acrescenta "grupo com poucos pares; leitura frágil" e R05 passa a modo descritivo |
| R03 | D | Fontes com último ano diferente (PAM 2023, ANP 2024, CONAB 2026/27) | "Atenção: PAM vai até {a}; CONAB até {safra} (estimativa)." | **Defasagem >= 2 anos entre fontes usadas na mesma tela:** destaca em faixa, não só em rodapé |
| R04 | D | Município/micro com zero registrado ou suprimido | "{n} de {N} municípios produzem cana em {ano}; {z} têm produção zero registrada e {s} estão sem informação (dado não divulgado pelo IBGE)." | **Suprimido != zero:** suprimido nunca soma nem plota como 0 e não entra na média; zero registrado plota como 0; **menos de 5 municípios produtores:** recusa ranking (R12); **cobertura < 50%:** aciona R12 |
| R05 | H | \|desvio vs referência\| >= 5% | "A produtividade ficou {x}% {acima/abaixo} da referência ({ref})." | **\|desvio\| < 2%:** "em linha com"; **2% a 5%:** "ligeiramente"; **empate entre categorias** (diferença < 0,5 t/ha): "empate técnico entre A e B" |
| R06 | H | Variação interanual >= 10% em módulo | "Houve {alta/queda} de {x}% frente a {ano-1}." | **Ano anterior ausente:** omite; **variação > 2 desvios-padrão da série:** acrescenta "valor fora do padrão histórico" |
| R07 | H | Classes de 5 e 10 anos diferem (sobe, estável, cai) e os dois intervalos de confiança de 95% excluem zero | "A tendência mudou: {a} t/ha/ano nos últimos 5 anos contra {b} nos últimos 10 (intervalos em {tabela})." | **Série < 8 pontos:** suprime; **intervalo inclui zero:** classe "estável", sem alerta (caso atual da PB); **classe muda ao retirar o último ano:** acrescenta "a leitura depende de {ano}"; **sempre** acrescenta "sem evidência confirmada de quebra estrutural" quando `quebra_confirmada` é falso |
| R08 | H | Meta ativa e produtividade < meta | "Em {ano}, a produtividade ficou {d} t/ha ({p}%) abaixo da meta de {m} t/ha." | **Meta > máximo da série:** "meta acima de qualquer valor observado desde {ano0}"; **meta ausente:** não gera |
| R09 | H | Dispersão entre microrregiões: razão melhor/pior >= 1,3 | "Entre microrregiões da PB, a produtividade varia de {min} a {max} t/ha ({a} e {b})." | **Menos de 3 microrregiões com dado:** suprime; **empate no topo:** lista ambas |
| R10 | H | Share açúcar ATR: PB vs mediana das UFs com dado | "Em {safra}, {s}% do ATR da PB foi para açúcar; mediana das UFs: {m}%." | **UF sem CONAB:** "sem dado industrial para esta UF"; fatores CONSECANA "a confirmar" entram como nota |
| R11 | H | Preço do açúcar em R$ varia >= 10% em 90 dias | "O açúcar em reais {subiu/caiu} {x}% em 90 dias (ICE {a} US¢/lb; PTAX R$ {b})." | **Último dado > 5 dias úteis:** "último dado de {data}"; **fonte indisponível:** omite e mostra o selo "fonte fora do ar" |
| R12 | A | Cobertura < limiar (ex. < 50% dos anos ou < 5 pares) | "Dados insuficientes para recomendar nesta combinação ({motivo})." | **Recusa explícita:** nenhuma ação sugerida; mostra o que falta |
| R13 | A | R05 abaixo da referência + R07 classe "cai" + cobertura ok | "Vale revisar a priorização de área e tratos em {território}; confira a área colhida ({ha} ha) antes de decidir." | **Base pequena (área < limiar):** troca a ação por "olhar com cautela: base pequena" |
| R14 | A | R11 com alta + R10 PB abaixo da mediana de açúcar | "O contexto de preço favorece o açúcar. Se quiser, leve à reunião com o comercial a pergunta sobre o mix." | **Sem dado de câmbio ou ICE:** não gera; nunca diz "mude o mix" |
| R15 | H | Países-referência (PSD): variação de estoques finais ou exportações >= 10% vs safra anterior | "O USDA estima {indicador} da {país} {x}% {maior/menor} que na safra anterior." | **País sem dado do ano corrente:** omite; nunca atribui causa a preço |
| R16 | H | Quebra candidata em `ponto_candidato_quebra` (hoje fixo em 2013; a Task 15 propõe a varredura supF) | "Há indício exploratório de mudança de regime em {ano} (não confirmado)." | `quebra_confirmada` falso é o padrão; texto afirmativo de quebra fica **proibido** por teste |

Teste automatizado obrigatório: nenhuma saída contém verbos proibidos ("falhou", "culpa", "causou", "garante"); cada regra tem pelo menos um teste por caso-limite; textos dourados em arquivo (golden) para detectar mudança involuntária de vocabulário.

---

## 6. Design, colorimetria e acessibilidade

**Direção.** Ferramenta de decisão de um usuário (não portal institucional): sóbria, densa na medida, "pergunta -> achado -> ação". Cada tela tem três faixas: (1) pergunta e filtros; (2) leitura em texto (descrever, destacar, sugerir) em destaque, com os números em fonte tabular; (3) evidência gráfica e tabela. Herda da Etapa 2 o verde-cana como marca, a barra divergente e o âmbar de "abaixo da referência".

**Cores (reuso de `docs/entrega-etapa2/paleta-acessibilidade.md`):**

| Papel | Cor | Observação |
|---|---|---|
| Marca/PB/acima da referência | `#2F6B3C` | Contraste 5,0:1 sobre `#F2F2F2` |
| Abaixo da referência | `#E08A1E` (âmbar) | Só forma/preenchimento; **nunca texto** (2,4:1). Quando precisar de texto âmbar, usar tom escuro derivado (a definir e medir em Task 3) |
| Açúcar | verde-claro `#7BA886` ou azul-ardósia `#3A6EA5` (Task 3 decide o par açúcar x etanol e testa em simulação de daltonismo) | Rótulo direto, sem depender só da cor |
| Etanol | o outro do par | idem |
| Ausente / sem informação | cinza `#6B7785` + **hachura** | Ausente != zero: nunca na rampa de dados |
| Cenário ativo | borda e selo, não uma cor de dado | Separa hipótese de realizado |
| Neutros | texto `#1A1A1A`, secundário `#50565E`, grade `#D5D9DE`, fundo `#F2F2F2` | Texto principal 16:1 |

Verde x âmbar é o par escolhido na Etapa 2 por separar nos três tipos de daltonismo. A rampa do coroplético deve ser sequencial de luminância monotônica (não verde-vermelho), com hachura para ausente. Task 3 mede contraste com script (WCAG 2.1 AA) e simula protanopia/deuteranopia/tritanopia.

**Tipografia.** Inter (UI e números, `font-variant-numeric: tabular-nums`) e Source Serif 4 apenas no bloco de "leitura" (dá peso de texto-achado). Fontes auto-hospedadas (pacote Fontsource), sem CDN. Escala de 14/16/20/28 px.

**Densidade e hierarquia.** Desktop-first (>= 1280 px) por ser consulta de escritório; tablet em modo leitura (1024 px) como meta; celular fora do escopo (justificado: o uso é pontual e em reunião com notebook; fica documentado como limitação). Máximo de 3 gráficos por tela. A leitura em texto vem antes do gráfico.

**Estados (todos obrigatórios):**
- **Carregando:** esqueleto com o formato do gráfico e `aria-busy`; nunca spinner infinito; após 8 s mostra "ainda carregando" e botão de repetir.
- **Vazio:** "Nenhum registro atende a esta combinação de filtros." + sugestão do que afrouxar (primeiro filtro que, removido, devolve resultado; o backend calcula).
- **Erro de carga:** mensagem em linguagem simples, código técnico recolhido, botão "tentar de novo"; telas de PAM seguem funcionando se só o mercado falhou.
- **Dado ausente:** hachura cinza + legenda "sem informação (dado não divulgado pelo IBGE)". Zero registrado (`sem_producao`) é plotado como 0, não como ausente.
- **Base pequena e defasagem:** selo "base pequena" e faixa de defasagem.

**Acessibilidade proporcional (usuário único, mas avaliador e arguição olham):**
- *Faz:* contraste AA, informação nunca só por cor, foco visível e navegação por teclado em filtros, mapa e gráficos; componentes acessíveis (Radix/shadcn); `aria-live="polite"` na leitura quando o filtro muda; **tabela equivalente** de cada gráfico (botão "ver como tabela") e texto alternativo curto com a mensagem do gráfico; `prefers-reduced-motion`; auditoria automatizada com axe no Playwright.
- *Não faz (declarado):* leitor de tela de ponta a ponta nos gráficos (cobre-se com a tabela equivalente), WCAG AAA, internacionalização, alto contraste dedicado, versão para celular.

**Bibliotecas.**
- **Gráficos: Observable Plot + D3 (d3-geo, d3-scale), com wrapper React fino.** Plot cobre barras divergentes, linhas, facetas (múltiplos pequenos), pontos/inclinação (slope) e `geo` (coroplético) com pouco código, saída SVG (fácil de rotular, testar e dar `role`/`aria`). Alternativas: *ECharts* (mais interatividade pronta e mapa, mas canvas por padrão, bundle grande e acessibilidade por descrição gerada); *Recharts* (simples, mas fraco para mapa, slope e facetas); *visx* (controle total, mais código). Decisão: Plot por produtividade e adequação aos três gráficos extras. Risco: tooltips e interação são mais manuais (mitigado com a marca `tip` do Plot e uma tabela equivalente).
- **UI: Tailwind CSS v4 + shadcn/ui (Radix).** Primitivos acessíveis (Select, Slider, Tabs, Dialog, Tooltip) sem escrever ARIA do zero, e tokens de cor em um só lugar.

---

## 7. Arquitetura técnica recomendada

### 7.1 Confirmação da stack e trade-offs

| Opção | Extras capturados | Prós | Contras | Decisão |
|---|---|---|---|---|
| **FastAPI + DuckDB + React/Vite (um contêiner)** | 3, 4, 5 | Reuso direto do pipeline Python e de `domain/`; OpenAPI gera tipos TS; DuckDB lê parquet sem ETL novo; um deploy | Duas linguagens; cold start em hospedagem gratuita | **Escolhida** |
| Next.js + API routes + DuckDB (Node) | 3, 5; 4 parcial | Uma linguagem | Reescrever indicadores e engine em TS; testes estatísticos pesam; foge do que o time já tem em Python | Rejeitada |
| Node/Express ou Hono | 3, 5 | Leve | Mesmo problema de reescrita; sem ganho sobre FastAPI | Rejeitada |
| SPA estática + DuckDB-WASM | 3 (consulta no navegador), 5 | Hospedagem estática, sem servidor | **Não captura "API própria"** (extra 4); dados internacionais exigem proxy (CORS e chaves); engine Python teria de ser reescrita | Rejeitada. Fica como plano B de hospedagem de emergência |

O volume de dados é pequeno (gold em parquet soma cerca de 1,4 MB, o maior é `fato_vendas_etanol_municipio` com 1,0 MB), então DuckDB aqui não é por desempenho, e sim por **consulta SQL parametrizada** e por ser extra do enunciado. Declarar isso com honestidade na arguição.

### 7.2 Estrutura de pastas (monorepo)

```
apps/
  api/                      # FastAPI (camada de apresentação HTTP)
    src/canavis_api/{main.py, settings.py, routers/, schemas/, services/, repositories/}
    tests/
  web/                      # React + TS + Vite
    src/{app/, routes/, features/, components/, charts/, lib/{api,url}, styles/}
    e2e/                    # Playwright
src/canavis/                # pipeline e domínio existentes (NÃO mover)
  domain/{indicators,features,tiers,texto}.py  (existente)
  domain/regras/            # NOVO: engine pura (catálogo, regras, limiares)
  sources/intl/             # NOVO: adapters BCB, FRED, WB, Yahoo, CFTC, USDA
  pipeline/intl.py          # NOVO: job de atualização -> data/external/
config/{settings,sources,regras}.yaml
data/{raw,interim,processed,external,geo}/
docs/{decisoes,entrega-etapa3}/
Dockerfile, compose.yaml, Makefile, .env.example, .github/workflows/
```

Regra de dependência (ADR 0003): `domain` não conhece `apps/`. A API importa `canavis` como biblioteca.

### 7.3 Contrato e DuckDB

- OpenAPI-first: `apps/api` publica `/openapi.json`; `openapi-typescript` gera os tipos do front; CI falha se `openapi.json` versionado diverge do gerado.
- Endpoints (v1, todos GET para serem linkáveis e cacheáveis): `/api/v1/saude`, `/fontes`, `/territorios`, `/indicadores/panorama`, `/indicadores/serie`, `/indicadores/ranking`, `/indicadores/mix`, `/municipios`, `/insights`, `/prioridades`, `/cenarios/simular`, `/mercado/{cambio,acucar,paises,cot}`, `/metodologia`.
- DuckDB: conexão somente leitura, `CREATE VIEW` sobre `read_parquet('data/processed/*.parquet')`, **sempre** `con.execute(sql, [params])`; identificadores (nome de coluna/indicador) só via lista branca. Indicadores como views SQL (produtividade = `SUM(q)/NULLIF(SUM(area),0)`), testados contra os valores auditados do DAX (PB 2023: 64,69 t/ha; -16,96%; +3,41%; 0,90%; share açúcar 27,54%).
- Observação verificada nos parquet: as colunas de **desvio e participação não estão** nos fatos por nível (só produtividade, tendência, oscilação, `p_chow`, etc.), então o app precisa calculá-las (Task 5). Contrato completo em [contrato-dados.md](contrato-dados.md). A coluna `nivel_suavizado_t_ha` (antes `tendencia_t_ha`) é uma média móvel centrada de 3 anos (nível suavizado, vazia em 2003 e 2023), não uma taxa; a inclinação em t/ha/ano com erro-padrão e intervalo ainda não existe na gold e entra na Task 5, para sustentar a R07 (Task 10).

### 7.4 Dados internacionais (camada de serviço)

- **Esquema comum** (parquet): `serie_id, data, valor, unidade, fonte_id, coletado_em, defasagem_dias, licenca`.
- **Adapters** em `src/canavis/sources/intl/` sobre `DataSource` (`sources/base.py`, que hoje só exige `fetch()`), registrados em `sources/registry.py` e `config/sources.yaml`. Fontes: BCB SGS (PTAX), FRED `PSUGAISAUSDM`, World Bank Pink Sheet, Yahoo `SB=F`, CFTC COT, USDA PSD (bulk CSV). Fora: Stooq, Nasdaq/Quandl (bloqueadas), EIA e QuickStats (exigem chave), FAOSTAT live (521), IMF/ISO/B3.
- **Estratégia: snapshot primeiro.** O job `canavis-intl refresh` grava `data/external/*.parquet` e um `manifest.json` (hash, data de coleta, versão da fonte). O snapshot **é versionado no git** e vai na imagem: o trabalho acadêmico é reproduzível e o app funciona offline. Atualização ao vivo é opcional (`CANAVIS_INTL_LIVE=1`), com cache em memória e TTL de 6 h (diário) e 24 h (mensal/semanal). Falha de fonte: serve o snapshot com `origem=snapshot` e `defasagem`; a tela mostra selo e **nunca** quebra.
- **Risco Yahoo `SB=F`:** não oficial e sujeito a bloqueio; fica como fonte de snapshot, com fallback para o FRED mensal e rótulo "não oficial". **CEPEA:** licença não comercial, fora do núcleo; só entra se acesso e atribuição forem confirmados.
- **Segredos:** nenhuma fonte do núcleo exige chave. `.env.example` lista `CANAVIS_INTL_LIVE`, `CANAVIS_DATA_DIR`, `CANAVIS_LOG_LEVEL`. Varredura de segredos no CI (gitleaks).
- **Atribuição:** tabela `dim_fonte` ampliada com licença e URL; exibida em `/metodologia`.

### 7.5 Engine de texto: onde roda

Recomendação: **backend, Python, funções puras** em `src/canavis/domain/regras/`. Alternativa (TS no front) reage sem ida ao servidor ao mexer em slider, mas duplicaria cálculos e dificultaria testar as regras com dados reais. A latência de uma consulta DuckDB sobre dados desse tamanho é baixa; o slider usa debounce de 250 ms. Cada insight retorna `{regra_id, funcao, texto, severidade, evidencias, limitacoes}`: o front pode mostrar "por que vejo isto?" sem lógica própria. Decisão a registrar no ADR 0015.

### 7.6 Testes

- **Engine:** `pytest` parametrizado por regra e caso-limite; testes de propriedade simples (texto nunca contém verbo proibido; selecionar vazio nunca lança); golden files de texto.
- **Indicadores:** paridade com valores auditados do DAX.
- **API:** `httpx` + `pytest` (contrato, parâmetros inválidos, falha de fonte simulada).
- **Front:** Vitest (serialização URL ida e volta, estados) + Testing Library.
- **E2E (Playwright):** abre `/uf/PB?ano=2021&ref=grupo&meta=65`, copia `page.url()`, abre em novo contexto limpo e compara texto da leitura e valores dos KPIs (Task 8). Também `axe` nas rotas principais.
- Existentes: 94 testes verdes em `tests/` (informado no brief; não reexecutados nesta investigação somente leitura).

### 7.7 Deploy, um comando e CI

- **Um comando:** `docker compose up` (build multi-estágio: Node compila o web; Python serve API + estático). Alternativa sem Docker: `make dev` (uv + pnpm). Dependências **fixadas**: `uv.lock` + versões exatas (`==`) no `pyproject`; `pnpm-lock.yaml` + versões exatas no `package.json`; imagem base com tag de versão.
- **Hospedagem (extra 5). Revisado em 26/11/2026: Render, plano Free, no ar em <https://canavis.onrender.com> (ADR 0018). O Hugging Face foi descartado porque Spaces Docker exigem plano PRO em contas pessoais. Texto original da recomendação:** Hugging Face Spaces (SDK Docker). Contêiner único, tier gratuito de CPU (relatos indicam 2 vCPU e 16 GB), sem cartão, URL estável `huggingface.co/spaces/<org>/<nome>`; dorme após inatividade (relatos de cerca de 48 h) e acorda na próxima requisição. Alternativa: **Render (free web service)** com 512 MB e 0,1 CPU, que dorme após 15 minutos e leva cerca de 50 s para acordar ([docs Render](https://render.com/docs/free), [artigo Render](https://render.com/articles/from-side-project-to-production-scaling-your-first-app)). Fly.io não tem mais tier gratuito segundo comparativos recentes ([xcloud](https://xcloud.host/best-free-docker-hosting/)). Mitigação para a demo: acordar o app 10 minutos antes (ping) e ter o `docker compose up` local como plano B. Fontes de HF: [exemplo FastAPI + React](https://huggingface.co/spaces/Reel-studio/reel-studio-2/blob/main/DEPLOY.md) e [limites de Spaces gratuitos](https://huggingface.co/spaces/carlratberg/car/blob/main/README.md). Conteúdo parafraseado; conferir os limites atuais antes de depender deles.
- **CI (GitHub Actions):** jobs `py` (ruff, pytest), `web` (tsc, eslint, vitest, build), `contract` (OpenAPI sem divergência), `e2e` (Playwright contra o compose), `secrets` (gitleaks). Deploy manual por tag.
- **Malhas geográficas:** API de malhas do IBGE (v3) entrega GeoJSON por UF e por microrregião, com qualidade configurável ([documentação IBGE](https://servicodados.ibge.gov.br/api/docs/malhas?versao=3)). Baixar uma vez, simplificar e versionar em `data/geo/` (sem depender da API em tempo de execução). Verificar na Task 14 que as microrregiões da PB ainda estão disponíveis e casam com `cod_microrregiao`.

### 7.8 ADRs a escrever

0013 stack (React+TS, FastAPI, DuckDB, contêiner único); 0014 URL como fonte de verdade e rotas (TanStack Router, zod); 0015 engine de regras em Python e política de vocabulário calibrado; 0016 ingestão internacional (snapshot-first, TTL, licenças); 0017 bibliotecas de gráficos e UI (Plot/D3, Tailwind/shadcn); 0018 deploy (HF Spaces) e reprodutibilidade; 0019 modelagem estatística e seus limites; 0020 parâmetros de cenário (sem projeção).

---

## 8. Mapeamento para pontos

### 8.1 Requisitos obrigatórios e rubrica

| Item | Issues | Risco |
|---|---|---|
| (a) rotas >= 3, URL reflete estado, parâmetro, Tabela 3.1 | Task 2, Task 8, Task 9, Task 18 | URL não reabre a mesma visão (trava em 3,0) |
| (b) >= 3 filtros, persistência documentada | Task 2, Task 8, Task 18 | Persistência imprevisível |
| (c) parâmetro e Tabela 3.2 | Task 11, Task 18 | Só mudar número, não leitura |
| (d) textos dinâmicos + casos-limite + Tabela 3.3 | Task 10, Task 11 | Texto fixo disfarçado; confiança fabricada |
| (e) engenharia, README, versões fixadas, sem segredos, erro | Task 4, Task 6, Task 16 | Um comando falhar na máquina do professor |
| (f) design, estados, metodologia | Task 2, Task 3, Task 13, Task 16 | Estado vazio genérico |
| (g) teste de aceitação | Task 17 | Persona indisponível |
| Discussão, relatório, vídeo, zip | Task 18, Task 19, Task 20 | Escrever no fim, sem tempo |
| Apresentação e arguição | Task 19 | Narrativa que parte da arquitetura |

### 8.2 Extras (Tabela 3.4)

| Extra (até) | Plano | Issues |
|---|---|---|
| 1. Gráficos não convencionais (0,5) | (a) **Coroplético** de produtividade por UF e microrregiões da PB: "onde a PB está no mapa?" (esboço A da Etapa 1); (b) **slope chart** PB vs pares do tier, 2013 -> 2023: "quem ganhou ou perdeu posição desde a inversão de regime?"; (c) **múltiplos pequenos** de microrregiões: "quais ganham ou perdem de forma consistente?". Bump chart só se sobrar tempo | Task 3, Task 14 |
| 2. Modelagem estatística (0,5) | **Defensável:** tendência robusta (Theil-Sen ou OLS com erro-padrão) com intervalo e classificação sobe/estável/cai (a inclinação com intervalo entra na Task 5 por alimentar a R07; a Task 15 acrescenta o Theil-Sen por microrregião e a varredura supF); `p_chow` + FDR já feitos; clusterização dos tiers interpretada. **Exploratório:** sensibilidade do share de açúcar ao preço do açúcar em R$ (Spearman e regressão simples com IC por bootstrap, n da ordem de 20 safras). **Não fazer:** projeção de produtividade. Resultado nulo é reportado como nulo | Task 15 |
| 3. Banco de dados (0,5) | DuckDB com views sobre parquet e `execute(sql, params)` | Task 6 |
| 4. API (0,5) | FastAPI própria com OpenAPI **e** consumo de APIs externas (BCB SGS, FRED, World Bank, USDA) | Task 4, Task 6, Task 7 |
| 5. Publicado (0,5) | Render, plano Free (<https://canavis.onrender.com>) | Task 4, Task 16 |
| Bônus entrega antecipada (+1,0) | Entregar >= 72 h antes do prazo | Task 20 |

Teto declarado de extras: 1,5. Cada extra entra na Tabela 3.4 com o caminho no código (Task 18).

---

## 9. Marcos e caminho crítico

Quatro marcos. Sem o prazo real, estão em ordem e horas. O backlog tem **20 issues** (estimativa de cerca de 270 h, aproximadamente 90 h por pessoa), no formato "Task N" da Etapa 2, com o detalhe nos checklists de critérios de aceitação. Fixar a data interna de entrega em **prazo menos 4 dias** (bônus de 72 h).

| Marco | Objetivo | Tasks |
|---|---|---|
| **M1 Fundação e esqueleto andante** | Stack confirmada, ADRs, jornada, design system; uma rota com parâmetro, uma consulta DuckDB, contêiner, CI e **deploy público inicial** | 1, 2, 3, 4 |
| **M2 Núcleo analítico** | Indicadores e catálogo, API + DuckDB + contrato, ingestão internacional (em paralelo), rotas/URL/filtros com e2e, telas da PAM | 5, 6, 7, 8, 9 |
| **M3 Textos, cenários e extras** | Engine de regras, cenários e prioridades, mercado, estados e metodologia, gráficos extras e estatística | 10, 11, 12, 13, 14, 15 |
| **M4 Qualidade e entrega** | Acessibilidade, README, teste de aceitação, relatório, vídeo, ensaio, zip | 16, 17, 18, 19, 20 |

**Caminho crítico:** Task 1 -> Task 4 -> Task 6 (com Task 5) -> Task 8 -> Task 9 -> Task 10 -> Task 11 -> Task 16 -> Task 17 -> Task 18 -> Task 20. Fora do caminho crítico: Task 12, Task 14, Task 15. **Revisado em 26/11/2026: a Task 7 (#31, dados internacionais) entra na prioridade máxima por decisão do time.** Ela responde ao pedido do professor de compensar a defasagem da PAM com sinal recente e sustenta os cenários S4/S5. Não depende do caminho crítico, só da Task 4, e pode correr em paralelo com as Tasks 5 e 6.

---

## 10. Riscos

| # | Risco | Impacto | Mitigação |
|---|---|---|---|
| R1 | ~~Prazo no Moodle desconhecido~~ **Resolvido:** 01/12/2026; meta interna 27/11/2026 | Cronograma e bônus de 72 h | Datas dos marcos no GitHub e no README |
| R2 | ~~Professor não confirmar a stack por escrito~~ **Resolvido:** stack confirmada (ADR 0013) | Nota | Task 1 é a primeira issue; plano B: Dash só sobre o mesmo backend, o que custaria o front |
| R3 | URL não reabre a mesma visão | Trava em 3,0 | URL única fonte de verdade, e2e em CI desde M2 |
| R4 | "Sobe com um comando" falha em outra máquina | Trava em 3,0 (engenharia) | Teste do compose em máquina limpa (Task 4); CI sobe o compose |
| R5 | Textos soam autoritativos demais | Rubrica de textos | Limiares, vocabulário, golden files, Task 10 |
| R6 | Fonte internacional bloqueia ou muda (Yahoo) | Cenários S4/S5 | Snapshot-first, fallback FRED, degradação graciosa |
| R7 | Time com pouca experiência em React/TS | Atraso | Esqueleto andante cedo, pareamento, escopo de gráficos extras opcional |
| R8 | Persona indisponível para o teste | Rubrica (0,5) e critérios de sucesso | Agendar em M4; reserva de 2 usuários próximos da persona, declarando a limitação |
| R9 | Render Free dorme após 15 min e tem 512 MB | Demo | Abrir o link antes; plano B com `docker compose up` local (o risco original, sobre o HF Spaces, se confirmou: exige PRO) |
| R10 | Microrregiões do IBGE descontinuadas na API de malhas | Mapa extra | Verificar em Task 14; fallback usar regiões imediatas via de-para de `dim_territorio` |
| R11 | CONSECANA 1,0495 "a confirmar" | Share ATR | Task 5 confirma ou rotula como premissa em `/metodologia` |
| R12 | Escopo infla | Atraso | Marcos com corte: cortar Task 14 e Task 15 antes de tocar nos obrigatórios. A Task 7 (dados internacionais) não entra no corte; a Task 12 (`/mercado`) só sai se a Task 7 já estiver pronta e a tela puder ser simplificada |
| R13 | Tensão persona x mix (Etapa 1 descartou o enquadramento 2) | Coerência da narrativa | Narrativa: sinal de mercado como contexto; ação "levar ao comercial" |
| R14 | Licença do CEPEA (não comercial) | Ética/atribuição | Fora do núcleo; só com atribuição |
| R15 | Dado municipal pouco informativo (produtividade com poucos valores distintos; 140 de 223 municípios com zero) e tendência sem evidência (IC inclui zero na PB) | Textos que sugerem ranking ou tendência sem lastro | `/municipios` ordenada por área; classe "estável" quando o IC inclui zero; `jornada-e-rotas.md` seção 7 |
| R15 | Dado anual PAM vs "trimestre" do enunciado | Teste de aceitação | Tarefa em termos de safra/ano: "3 casos prioritários da safra" |

---

## 11. Perguntas em aberto

Para o professor: **P1** ~~prazo exato e hora no Moodle~~ (resolvido: 01/12/2026; confirmar a hora); **P2** ~~confirmação de React + TypeScript + FastAPI~~ (resolvido); **P3** o link publicado pode ser em hospedagem gratuita que dorme? **P4** o zip pode conter a imagem Docker ou basta o Dockerfile e o compose? **P5** os dados internacionais em snapshot versionado contam como "dados ou script de obtenção"?

Para o demandante: **P6** limiares de relevância (desvio, variação, tendência); **P7** unidade de tempo preferida (safra x ano civil); **P8** se aceita o sinal de mercado como contexto; **P9** disponibilidade para o teste de aceitação; **P10** quem fala com o comercial sobre mix.

Para o time: **P11** quem tem experiência em React/TS; **P12** máquinas e SO para validar o `docker compose up`; **P13** idioma do README (o repositório hoje tem README em inglês e docs em português: recomendo manter o README em português por ser a língua do avaliador, com um parágrafo curto em inglês; decidir).

---

## 12. Evidências consultadas

`docs/entrega-etapa1/Etapa1_Cordeiro_Alex.tex`; `docs/entrevista/roteiro-e-anotacoes.md`; `docs/decisoes/0004`, `0009`, `0010`, `0011`, `README`; `docs/entrega-etapa2/{mapa-rotas,cenarios,paleta-acessibilidade,teste-usuario,auditoria-medidas-dax,serie-temporal-descritiva}.md`; `data/processed/*.parquet` (esquemas e tamanhos lidos); `src/canavis/sources/{base,registry,http_client}.py`, `domain/texto.py`; `pyproject.toml`; `config/sources.yaml`; issues da Etapa 2 (`gh issue view 13`) para o padrão de corpo e labels existentes. Não existe `.github/` no repositório (CI é novo). `duckdb` não está instalado no ambiente atual (é dependência nova a fixar).

Não verificado nesta investigação: execução dos 94 testes; disponibilidade atual de cada fonte internacional; limites vigentes dos tiers gratuitos citados (tratar como indícios).
