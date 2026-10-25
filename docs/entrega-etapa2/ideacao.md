# Ideação — Etapa 2 (Tabela 2.1 do roteiro, letra a)

**Projeto:** CanaVis — Benchmarking regional da produção de cana-de-açúcar na Paraíba
**Tela ideada:** Panorama Nacional (tela principal / de entrada)
**Pergunta analítica mais importante:** como a produtividade/produção da região da persona se
posiciona frente às outras regiões produtoras do país (pergunta de decisão principal da Etapa 1).

Os esboços em baixa fidelidade estão em `wireframes/etapa2/` (`Layout A.png`, `Layout B.png`,
`Layout C.png`). Os descartes são parte da entrega e estão documentados abaixo.

---

## 1. Três layouts da tela principal

Cada layout foi construído para priorizar uma resposta diferente à dúvida central levantada no
feedback da Etapa 1: *a referência regional exibida liga com a decisão que o gerente precisa
tomar?*

| Layout | Aposta | Elemento dominante | O que facilita | O que limita |
|--------|--------|--------------------|----------------|--------------|
| **A — Mapa dominante** | "Onde estou" | Mapa coroplético do Brasil, PB destacada | Leitura espacial imediata; vizinhança e concentração geográfica | Situa, mas não diz se a PB está melhor ou pior que seus pares nem qual decisão isso muda; título passivo; cor é tarefa perceptual fraca para comparar magnitude |
| **B — Comparação dominante** | "Estou acima ou abaixo dos meus pares" | Barras divergentes de desvio vs. referência; mapa como apoio lateral | Posição relativa lida por comprimento a partir de uma linha-base (a referência); título já enuncia a conclusão | Perde a geografia como protagonista; depende de uma referência bem escolhida (liga com os tiers da Task 4) |
| **C — Trajetória dominante** | "Para onde estou indo" | Linha temporal do posicionamento + ranking de produtividade | Evolução ao longo das safras; o ranking já traz denominador (t/ha) e a PB marcada como referência | Dois elementos fortes tensionam o limite de 1 dominante + 2 secundários; responde melhor "para onde vou" que "onde estou agora" |

---

## 2. Três formas visuais para a pergunta de posicionamento

O roteiro exige dizer o que cada forma **facilita** e o que **esconde**, com argumento de tipo de
comparação e tarefa perceptual (não "é o gráfico mais comum").

| Forma visual | Facilita | Esconde / limita | Tarefa perceptual |
|--------------|----------|------------------|-------------------|
| **Mapa coroplético** | Leitura espacial imediata; mostra vizinhança e concentração geográfica | Compara mal valores próximos; a cor satura e o município pequeno some ao lado do grande; não ordena | Cor / saturação — fraca para magnitude precisa |
| **Barras divergentes** (desvio vs. referência) | Posição relativa acima/abaixo do par lida na hora; o ponto zero é a referência explícita | Perde a geografia; depende de uma referência bem escolhida | Comprimento a partir de linha-base comum — a mais precisa para comparação |
| **Dot plot / ranking ordenado** | Compara magnitude e ordena bem com muitas UFs; econômico em tinta | Não mostra espaço nem evolução; exige ordenação intencional (nunca alfabética) | Posição numa escala comum — alta precisão |

**Forma descartada explicitamente — gráfico de pizza de participação regional.** O ângulo é uma
tarefa perceptual ruim para comparação, com 27 UFs estoura o limite de legibilidade, e o roteiro
proíbe pizza com mais de três fatias. Documentada como descarte consciente.

---

## 3. Escolha justificada

### Layout escolhido: **B — Comparação dominante**

**Justificativa (tipo de comparação + tarefa perceptual):** a pergunta de decisão principal da
Etapa 1 é de **posicionamento relativo** — onde a produtividade da região está frente às outras.
As **barras divergentes** leem esse posicionamento pela tarefa perceptual mais precisa
(comprimento a partir de uma linha-base comum, que aqui é a referência de comparação), enquanto o
mapa usa cor, tarefa fraca para magnitude. O Layout B coloca a comparação como elemento dominante
e o mapa como contexto secundário, cumprindo a hierarquia visual que o roteiro pede (1 dominante +
até 2 secundários) e o título ativo que enuncia a conclusão da tela ("PB está X% abaixo do
grupo"), em vez de apenas nomear o assunto.

**Resposta ao feedback:** o professor questionou a ligação entre a referência regional exibida e a
decisão do gerente. O Layout B torna a comparação com a referência o centro da tela, não um
detalhe. O ajuste previsto é deixar explícito na tela qual é a referência ("comparado a: [média
nacional ▾]"), porque é exatamente essa referência que o parâmetro de cenário da Task 9 vai
trocar (média nacional → pares do mesmo tier → outras regiões produtoras).

### Forma visual escolhida: **barras divergentes** (com o mapa como apoio)

Pelo mesmo argumento perceptual acima. Ajuste a aplicar no `.pbix`: ordenação intencional por
desvio (não alfabética) e rótulo de cada barra pelo eixo.

### Descartes (parte da avaliação)

- **Layout A — descartado como tela principal.** O mapa situa bem, mas a cor é tarefa perceptual
  fraca para comparar magnitude e não responde "melhor ou pior que meus pares". É justamente a
  ligação que o feedback apontou como frágil. Reaproveitado como visão geográfica secundária.
- **Layout C — descartado como tela principal.** Responde melhor "para onde vou" que "onde estou
  agora" e divide a atenção em dois elementos fortes, pesado demais para a tela de entrada.
  Reaproveitado como tela de detalhe.

---

## 4. Encaixe no fluxo de navegação (liga com a Task 8, letra c)

Os três layouts não são um vencedor e dois descartes: viram as três telas do fluxo obrigatório de
navegação.

| Tela | Layout | Papel |
|------|--------|-------|
| Panorama Nacional (entrada) | **B** | Abre com o posicionamento relativo da região |
| Detalhe do Estado / Município | **C** | Trajetória e ranking do recorte selecionado (destino do drill-through) |
| Visão geográfica de apoio | **A** | Contexto espacial secundário |

O drill-through parte da tela B (posicionamento) e leva o recorte selecionado para a tela C
(trajetória + ranking daquele estado/município), transportando contexto — a transição exigida
pela letra (c).

---

## Checklist da letra (a) — status

- [x] 3 layouts da tela principal em esboço (`wireframes/etapa2/`)
- [x] 3 formas visuais consideradas, com o que cada uma facilita e esconde
- [x] Escolha de uma de cada, justificada por tipo de comparação e tarefa perceptual
- [x] Descartes preservados e documentados
