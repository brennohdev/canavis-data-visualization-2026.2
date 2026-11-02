# 0011 — Metodologias de quebra estrutural: confirmação endógena e por que o gate do 0009 permanece

**Status:** Aceita como extensão do ADR 0009 (continuação da **Task 10 / issue #14**, Etapa 2)
**Origem:** feedback do professor (Etapa 2)
**Evidência:** `.agents/tasks/quebra-estrutural/relatorio-metodologias.md`
**Estende:** ADR 0009 (decomposição + Chow exploratório); dialoga com ADR 0004 (janela temporal)

## Contexto

O professor foi direto: *"uma mudança visível na série não basta para afirmar que houve quebra
estrutural. Pesquisem metodologias para diferenciar mudança de regime, tendência e oscilação, e
expliquem como essa distinção afetaria a leitura do painel."*

O ADR 0009 já tinha chegado, por conta própria, à conclusão de que não se pode afirmar quebra: ver um
"degrau" em 2012/2013 na produtividade (t/ha) da PAM e rodar um Chow naquele ponto **não prova quebra**,
porque o ponto de corte foi escolhido olhando os próprios dados. O 0009 listou três ressalvas que
impedem conclusão confirmatória: (1) ponto selecionado a olho, (2) erros não verificados quanto a
independência/homocedasticidade, (3) múltiplas comparações sem correção. Esta decisão registra o
resultado da pesquisa pedida: quais métodos fecham essas três lacunas e se algum deles permite
**elevar** a afirmação de "exploratório" para "quebra confirmada".

A série em jogo é curta: **21 pontos anuais (2003–2023)** por território (UF ou microrregião), sem
sazonalidade intra-anual.

## Evidência — distinguir os quatro objetos

O feedback junta três objetos que precisam ser separados conceitualmente, mais um quarto que a série
curta torna crítico:

| Objeto | O que é | Assinatura | Erro de leitura se confundido |
|--------|---------|-----------|-------------------------------|
| **Quebra de nível/inclinação** | mudança abrupta e persistente dos parâmetros | "degrau"/"cotovelo" que não volta | tratar recuperação temporária como novo patamar |
| **Tendência suave** | deriva gradual ao longo do tempo | inclinação contínua, sem ruptura | ver "quebra" onde há curvatura mal ajustada por duas retas |
| **Oscilação / ruído estacionário** | flutuação em torno de nível estável | sobe e desce, reverte à média | ler um pico (ex.: 2023) como salto estrutural |
| **Raiz unitária / passeio aleatório** | choques se acumulam sem memória permanente | "degraus" e "tendências" aparentes, mas espúrios | afirmar estrutura onde há só ruído integrado |

O "degrau" 2012/2013 da PB é compatível com os quatro — e, com 21 pontos, **não dá para cravar qual**.

### Métodos pesquisados

| Método | O que detecta | Exige ponto a priori? | Disponível em Python / R | Adequado a 21 pontos anuais? |
|--------|---------------|-----------------------|--------------------------|------------------------------|
| **Chow clássico** (atual, 0009) | diferença de intercepto+inclinação em ponto **fixo** | **Sim** (vício: ponto garimpado) | Py: implementado à mão / R: `strucchange` | roda, mas p nominal inválido p/ confirmação |
| **Quandt-Andrews / supF** | **uma** quebra de data **desconhecida** | **Não** (varre e maximiza) | Py: `pyqlrtest`/`pysb` (3º) / R: `strucchange::Fstats` | parcial — corrige o viés, poder baixo; **reforço** |
| **Bai-Perron** | **múltiplas** quebras + datas (IC) | **Não** | Py: sem API oficial / R: `strucchange`, `mbreaks` | **não** — parâmetros demais p/ 21 pts |
| **CUSUM / CUSUM-of-squares** | instabilidade ao longo do tempo (visual) | **Não** | Py: `statsmodels` / R: `strucchange` | parcial — bom apelo visual; **opcional** |
| **Zivot-Andrews** | quebra determinística vs **random walk** | **Não** (quebra endógena) | Py: `statsmodels` / R: `urca` | parcial — distorção de tamanho + poder baixo |
| **Markov-switching** | alternância **repetida** entre regimes | **Não** | Py: `statsmodels` / R: `MSwM` | **não** — poder quase nulo aqui |
| **STL / Loess** | tendência suave vs oscilação | n/a | Py: `statsmodels` / R: `stl` | sim, mas a MM-3 atual já basta |
| **Filtro HP** | ciclo vs tendência | n/a | Py: `statsmodels` / R: `mFilter` | **não** — ciclos espúrios + instável nas pontas (2023) |
| **Correção FDR / Bonferroni** | ajuste de múltiplas comparações | n/a | Py: `statsmodels.stats.multitest` | **sim — barato e recomendado** |

Fatos de poder estatístico que decidem a questão:

- Testes endógenos (supF, Bai-Perron, Zivot-Andrews) aparam as pontas (~15%), reduzindo ainda mais os
  pontos efetivos; **não rejeitar não é prova de estabilidade**, é falta de poder.
- Distinguir regime de random walk é intrinsecamente difícil (Nelson, Piger & Zivot mostram poder
  baixíssimo dos testes de raiz unitária contra tendência Markov-switching) — com 21 pontos, impraticável
  de forma confiável.
- Múltiplas comparações: testar ~40 territórios a α=0,05 produz ~2 falsos positivos só por acaso; a
  contagem "p<0,05 em 15 UFs e 8 microrregiões" do 0009 precisa de correção.

## Decisão

**O gate do ADR 0009 permanece: não se afirma quebra estrutural.** A pesquisa confirma que, com 21
pontos anuais, nenhum método confirmatório eleva o veredito. Os métodos endógenos corrigem o viés do
ponto garimpado, mas pagam esse rigor com poder estatístico já escasso; o resultado provável é "não
rejeita" — que não prova ausência de quebra. A conclusão defensável continua **descritiva**.

Para fechar a **Task 10 (issue #14)** nesta Etapa 2, a recomendação (ordem de retorno) é:

1. **Correção de múltiplas comparações (Benjamini-Hochberg / FDR)** sobre os p-valores por território.
   Baixo custo (`statsmodels.stats.multitest.multipletests`), alto ganho de honestidade; reescreve
   "p<0,05 em 15 UFs e 8 microrregiões" para "N territórios sobrevivem ao controle de FDR".
2. **supF / Quandt-Andrews na UF Paraíba** (e opcionalmente **CUSUM**), rodado uma vez como evidência,
   **não** como selo no painel. Efeito permitido: mostrar que, mesmo sem fixar o ponto a olho, a
   evidência permanece exploratória. Implementável sobre a `teste_chow()` existente (varrer o ponto +
   valores críticos de Andrews).
3. **Zivot-Andrews na PB** como checagem conceitual "quebra vs random walk", registrando a ressalva de
   distorção de tamanho.

**Não compensa**, dado o tamanho da amostra: **Bai-Perron multi-quebra** (parâmetros demais, IC largo),
**Markov-switching** (poder quase nulo) e **filtro HP** (ciclos espúrios, instável nas pontas; a média
móvel centrada de 3 anos do 0009 é mais transparente).

O papel dos métodos endógenos é **defensivo**: responder ao professor com "tentamos o método correto
para data desconhecida, e ele confirma a prudência", não produzir um selo de confirmação.

A implementação em Python implica adicionar `statsmodels` como dependência (cobre FDR, CUSUM,
Zivot-Andrews e Markov-switching de uma vez); supF/Bai-Perron "de referência" vivem melhor em R
(`strucchange`/`mbreaks`) e podem ser rodados uma vez fora do pipeline, com o resultado citado no ADR.

## Impacto na leitura do painel

- **Rótulo do ponto 2013:** manter `ponto_candidato_quebra` como "divisão exploratória"/"candidato";
  **nunca** "quebra confirmada". A coluna `quebra_confirmada` segue **sempre nula** — com um tooltip
  explicando que nulo significa "confirmação não estabelecida", **não** "provou-se que não há quebra".
- **Linguagem:** verbos descritivos ("observa-se queda até ~2012 e recuperação até 2023"; "diferença
  entre períodos é **sugestiva** em teste exploratório"). Evitar "quebra"/"mudança de regime" como
  afirmação; se usados, que seja como pergunta com a ressalva anexada.
- **Pico de 2023:** sinalizar como pico atípico da PB (+15%, ADR 0004), com marcação visual. Expor a
  análise de sensibilidade do 0009 (F = 4,19 sem 2023, praticamente igual a 4,25) como nota de robustez.
- **Bandas de incerteza:** recomendadas — provavelmente a mudança de maior retorno. Comunicar a
  incerteza (faixa em torno da tendência; inclinações dos dois períodos com IC largos que podem se
  sobrepor) transforma o gate de "limitação escondida" em mensagem de produto: o painel mostra
  honestamente que o dado é curto.

## Escopo e timing — continuação da Task 10 (Etapa 2)

Esta frente **não é da Etapa 3**: é a continuação da **Task 10 / issue #14** ("Modelagem da série
temporal", `etapa-2`), co-assinada por Gustavo (yScroww) e Brenno, que o Gustavo começou e cujo ADR
0009 já entregou a base (decomposição + Chow exploratório + materialização + testes). O feedback do
professor sobre quebras estruturais pede o reforço metodológico acima **dentro desta Etapa 2**, não
depois. As colunas temporais já materializadas (`tendencia_t_ha`, `oscilacao_t_ha`, `f_chow`, `p_chow`,
`status_chow`, `ponto_candidato_quebra`, `quebra_confirmada`) permanecem; as checagens (FDR,
supF/CUSUM, Zivot-Andrews) e os ajustes de rotulagem/bandas de incerteza fecham os critérios de
aceitação restantes da issue #14. Única pendência de fato adiada para a **Etapa 3**: os **dados
internacionais** (ADR 0010).

## Consequências

- A resposta ao professor fica lastreada: passa-se de "não confirmamos porque o ponto foi escolhido a
  olho" para "tentamos os métodos endógenos corretos e a correção de multiplicidade, e o veredito
  exploratório se sustenta". É fortalecimento da mesma decisão, não uma decisão nova — por isso este
  ADR **estende** o 0009 em vez de substituí-lo.
- Nenhuma alteração em código ou no PBIX nesta decisão (é o registro metodológico); a implementação
  das checagens e dos ajustes de rotulagem fecha a Task 10 / issue #14 ainda na Etapa 2.
- A rotulagem honesta (sem "quebra confirmada", com bandas de incerteza) vira requisito de produto
  desta entrega.
