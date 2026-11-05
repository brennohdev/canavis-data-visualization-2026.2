# Justificativa das escolhas visuais — Etapa 2 (roteiro, letra f)

**Projeto:** CanaVis — Benchmarking regional da produção de cana-de-açúcar na Paraíba

Cada gráfico é justificado a partir da pergunta analítica correspondente da Etapa 1 (Tabela 1.4),
pelo **tipo de comparação** que a pergunta exige e pela **tarefa perceptual** que o leitor precisa
executar. Justificativas do tipo "é o gráfico mais comum" não são usadas.

Referência sobre precisão das tarefas perceptuais (Cleveland & McGill): posição numa escala comum
e comprimento são lidos com mais precisão; ângulo, área e cor/saturação são menos precisos. As
escolhas abaixo priorizam a tarefa mais precisa que responde a cada pergunta.

---

## Tela 1 — Panorama Nacional

### Visual dominante: barras divergentes (desvio vs. referência)

- **Pergunta (Etapa 1, Q3):** como a produtividade da região se compara à de outras, na mesma
  escala?
- **Tipo de comparação:** posição relativa a uma referência (acima/abaixo), entre 27 unidades.
- **Tarefa perceptual:** comprimento a partir de uma linha-base comum (o zero = a referência).
  É a tarefa mais precisa para julgar "quanto acima/abaixo", superior a cor (mapa) para magnitude.
- **Por que não outra forma:** um mapa colore bem o espaço, mas pede ao leitor comparar
  saturações — tarefa imprecisa; uma tabela traz o número exato mas não dá a leitura imediata de
  posição. As barras divergentes põem a referência no centro e deixam o desvio saltar à vista.
- **Ligação com o parâmetro (Task 9):** a referência das barras é trocável (todas as UFs / pares
  do tier / participação), então o mesmo visual responde à pergunta sob três referências.

### Visual secundário: mapa coroplético

- **Pergunta (Etapa 1, Q1):** como está distribuída a produção entre as regiões do país?
- **Tipo de comparação:** posição no espaço / composição geográfica.
- **Tarefa perceptual:** identificação espacial (onde), não comparação de magnitude. O mapa é
  secundário justamente porque cor é fraca para magnitude; ele situa, as barras comparam.

---

## Tela 2 — Detalhe do Estado

### Visual dominante: linha temporal da produtividade

- **Pergunta (Etapa 1, Q2):** como a produtividade da região evoluiu ao longo das safras?
- **Tipo de comparação:** evolução ao longo do tempo (tendência vs. oscilação).
- **Tarefa perceptual:** posição ao longo de um eixo temporal contínuo; a inclinação do traço
  comunica direção e ritmo. É a forma canônica para série temporal porque o olho lê tendência
  pela inclinação, não por saltos entre pontos isolados.
- **Reforço (Task 10):** a linha pode exibir o componente de tendência separado da oscilação,
  tornando visível o que é regime e o que é ruído — distinção pedida no feedback da Etapa 1.

### Visual secundário: ranking de estados (tabela ordenada)

- **Pergunta (Etapa 1, Q4):** quais unidades vêm ganhando/perdendo posição?
- **Tarefa perceptual:** posição numa escala comum + ordenação explícita. A ordenação é
  **intencional por produtividade** (decrescente), nunca alfabética.

### Visual secundário: mix açúcar/etanol (ver nota de higiene abaixo)

- **Pergunta (Etapa 1, Q5):** como se divide o destino da cana entre açúcar e etanol?
- **Tipo de comparação:** composição (duas partes de um todo).
- **Tarefa perceptual:** com apenas **2 fatias**, a pizza comunica uma proporção simples de forma
  imediata e está dentro do limite do roteiro (proíbe-se pizza com mais de 3 fatias). Para uma
  leitura de magnitude mais precisa, a alternativa seria uma barra 100% empilhada; a pizza foi
  mantida por ser uma partição binária clara e rotulada com os percentuais.

---

## Tela 3 — Detalhamento PB

### Visual dominante: produtividade por microrregião (linha/barra ordenada)

- **Pergunta (Etapa 1, Q4):** quais microrregiões se destacam dentro do estado?
- **Tarefa perceptual:** posição numa escala comum, com ordenação intencional por produtividade.

### Visual secundário: top municípios em vendas de etanol (barras)

- **Pergunta (Etapa 1, Q1/Q5):** onde se concentra a demanda de etanol na PB?
- **Tarefa perceptual:** comprimento de barra a partir de linha-base zero — comparação direta de
  magnitude entre municípios, ordenada por valor.

---

## Higiene visual e acessibilidade (letra g) — conformidade

Detalhe completo em `paleta-acessibilidade.md`. Resumo da conformidade nas telas:

| Item do roteiro | Situação |
|-----------------|----------|
| Paleta ≤ 5 cores de dado | Verde-cana, verde claro, âmbar, azul-ardósia, cinza (5) |
| Verificada para daltonismo | Par divergente verde × âmbar (não verde × vermelho) |
| Contraste para projeção | Texto em verde-cana/preto sobre fundo claro (≥ 5:1); âmbar só em formas |
| Ordenação intencional | Rankings e barras ordenados por valor, nunca alfabética |
| Sem eixo truncado sem aviso | Barras divergentes partem do zero (a referência) |
| Sem 3D | Nenhum visual 3D |
| Pizza ≤ 3 fatias | Mix com 2 fatias (dentro do limite) |
| Indicador com denominador | Produtividade (t/ha), participação (%), desvio (%) sempre com unidade |
| Página de metodologia | Tela "Metodologia" com fontes, indicadores e limitações |

### Narrativa em tela (letra f) — conformidade

| Item | Situação |
|------|----------|
| Título ativo (conclusão, não assunto) | Ex.: "PB está 3,4% acima do seu grupo industrial"; "Detalhe de [UF]" |
| 1 visual dominante + até 2 secundários | Respeitado em cada tela (ver acima) |
| Linha de contexto (fonte/período/unidade) | Rodapé: "Fontes: IBGE PAM (SIDRA 1612), CONAB, ANP. Produtividade em t/ha." |

---

## Ponto de atenção honesto (para a discussão da memória)

O **gráfico de pizza do mix** é o elemento mais frágil do conjunto do ponto de vista perceptual.
Está dentro da regra (2 fatias), mas pizza é a forma mais fraca para comparação de magnitude. Se
houver tempo, trocá-lo por uma barra 100% empilhada (ou um par de barras) melhora a leitura sem
custo — é um ajuste barato, no espírito da Etapa 2 ("descobrir o que não funciona enquanto mudar
é barato"). Mantido como está por ora; registrado aqui como decisão consciente, não descuido.
