# Série temporal no Power BI — leitura descritiva com incerteza explícita

**Projeto:** CanaVis — Benchmarking regional da produção de cana-de-açúcar na Paraíba
**Tela:** Detalhe do Estado / Detalhe do Município (linha temporal — ver `mapa-rotas.md`)
**Responde ao feedback:** quebras estruturais ("uma mudança visível na série não basta para afirmar quebra")
**Ancora em:** ADR 0004 (janela temporal), ADR 0009 (decomposição + gate), ADR 0011 (metodologia),
`notebooks/04_econometria_serie_temporal.ipynb` (números reais)

---

## Princípio da entrega (leia primeiro)

A série de produtividade (t/ha) é **anual e curta** (21 pontos, 2003–2023) e, no diagnóstico
econométrico completo (notebook 04), **não sustentou afirmação confirmatória de quebra estrutural**:
o supF endógeno da Paraíba recai em 2013 mas fica muito abaixo do crítico de Quandt-Andrews; o
Zivot-Andrews não separa quebra de passeio aleatório; e, sob controle de múltiplas comparações (FDR),
a própria Paraíba **deixa de sobreviver** (p ajustado 0,0606).

Isso **não** inviabiliza a série no painel — muda o modo de apresentá-la. O painel conta o que a série
**mostra** (queda e recuperação, tendência vs oscilação), nunca o que ela **não prova** (quebra
confirmada). A incerteza deixa de ser limitação escondida e vira mensagem de produto: o visual comunica
honestamente que o sinal é de baixo poder. É esse enquadramento que responde ao feedback.

**Regra de ouro:** descrever, nunca confirmar. Um território por gráfico; nunca somar tendências de
territórios diferentes; nunca projetar para o futuro.

---

## Não precisa reabrir o modelo de dados

Todo o necessário já está materializado em `powerbi/modelo.tmdl` (Task 10, ADR 0009). Esta entrega é de
**layout e rotulagem** no `.pbix`, não de modelagem:

| Coluna / medida existente | Uso na tela |
|---------------------------|-------------|
| medida `Produtividade` | linha do **observado** |
| medida `Tendência histórica (t por ha)` (`MAX(tendencia_t_ha)`) | linha suave de **tendência** (média móvel de 3 anos) |
| medida `Oscilação histórica (t por ha)` (`MAX(oscilacao_t_ha)`) | base da **banda de incerteza** (observado − tendência) |
| coluna `ponto_candidato_quebra` (True em 2013) | marcador vertical de **"divisão exploratória"** |
| coluna `quebra_confirmada` (sempre nula) | **não** vira visual; alimenta o tooltip de ressalva |
| medida `P Chow exploratório (2003-2023)` | cartão/tooltip discreto, sempre rotulado "exploratório" |
| `status_chow` | filtro de sanidade (só `exploratorio` tem teste válido) |

---

## Os cinco elementos da tela (ordem de prioridade)

### 1. Gráfico de linha: observado + tendência

Um gráfico de linha único, **um território por vez** (as medidas já têm `HASONEVALUE` e forçam isso):

- Eixo X: ano (2003–2023).
- Linha cheia: `Produtividade` (observado).
- Linha suave sobreposta: `Tendência histórica (t por ha)`.

É o coração da entrega e atende diretamente ao objetivo da Task 10: a **tendência** é a linha suave; a
**oscilação** é a distância entre as duas linhas. Mantenha as lacunas visíveis (anos sem dado ficam
sem ponto) — não interpolar.

### 2. Banda de incerteza ao redor da tendência

A jogada de maior retorno. Em vez de esconder que a série é curta, **mostre** a margem: uma faixa
sombreada ao redor da linha de tendência (área entre `Tendência + Oscilação` e `Tendência − Oscilação`,
ou um intervalo equivalente). A leitura vira "a tendência é esta, com esta margem de ruído". É o que
comunica, dentro do próprio painel, que o sinal é incerto — a resposta visual ao feedback do professor.

### 3. Marcador de 2013 como "divisão exploratória"

Uma linha vertical de referência em 2013 (via `ponto_candidato_quebra`), rotulada **"divisão
exploratória"** ou **"inversão observada"**. O que **não** pode aparecer: a palavra "quebra" como
afirmação, nem selo de confirmação. A coluna `quebra_confirmada` é nula de propósito — e isso exige um
**tooltip** explicando que *nulo significa "não confirmada", não "provou-se que não há quebra"*. Sem
esse tooltip, o usuário lê o vazio como "não houve quebra", que é tão errado quanto afirmar que houve.

### 4. Anotação do pico de 2023

Destaque visual em 2023 com nota "pico atípico (+15%)" (ADR 0004), para o usuário não ler o último ponto
como novo patamar. Opcional e barato: nota de robustez de que o resultado não depende de 2023 (a
sensibilidade do ADR 0009 mostra F praticamente igual sem ele: 4,19 vs 4,25).

### 5. Cartão/tooltip de contexto estatístico

A medida `P Chow exploratório` pode aparecer num cartão discreto ou tooltip, **sempre** com o rótulo
"exploratório" colado e, idealmente, a nota do FDR: a Paraíba não sobrevive à correção de múltiplas
comparações. É o detalhe que mostra, na arguição, que a equipe sabe o que o número vale. Nunca como
número de destaque da tela.

---

## Linguagem — descritiva, nunca confirmatória

| Pode aparecer na tela | Não pode aparecer |
|-----------------------|-------------------|
| "queda observada até ~2012" | "quebra estrutural" (como afirmação) |
| "recuperação até 2023" | "mudança de regime confirmada" |
| "diferença entre períodos **sugestiva** (teste exploratório)" | "o regime mudou em 2013" |
| "tendência com margem de incerteza" | "tendência de X t/ha ao ano" projetada ao futuro |

---

## O que NÃO fazer

- **Não** plotar `f_chow`/`p_chow` como resultado central — são rodapé/tooltip.
- **Não** colorir territórios como "tem quebra / não tem quebra".
- **Não** extrapolar a linha para o futuro (sem projeção/forecast — fora de escopo nesta etapa; a
  modelagem de série longa cabe às fontes internacionais do ADR 0010, na Etapa 3).
- **Não** comparar tendências de territórios de porte diferente na mesma escala (isso é papel do tier,
  na tela de comparação, não desta).
- **Não** usar município para a série longa (62% de supressão; ADR 0004) — a linha temporal é de
  microrregião/UF.

---

## Passo a passo no Power BI

1. Na tela de Detalhe do Estado/Município, inserir um visual de **linha**. Eixo X = `dim_calendario[ano]`.
2. Adicionar as medidas `Produtividade` e `Tendência histórica (t por ha)` nos valores (duas linhas).
3. Garantir que a tela tenha **um território no contexto** (slicer de território ou drill-through), para
   `HASONEVALUE` resolver — sem isso as medidas de tendência/oscilação ficam em branco de propósito.
4. Banda de incerteza: criar duas medidas auxiliares (limite superior = `[Tendência histórica (t por ha)] +`
   `ABS([Oscilação histórica (t por ha)])`; inferior = a mesma com `−`) e usar um visual que suporte área
   sombreada entre linhas, ou o recurso de **faixa de erro** / análise do visual de linha.
5. Linha de referência vertical em 2013 (via analítica do visual ou medida que marque
   `ponto_candidato_quebra`), rótulo "divisão exploratória".
6. Anotação/marcador em 2023 ("pico atípico, +15%").
7. Tooltip personalizado no ponto 2013 explicando "candidato exploratório; quebra não confirmada — nulo
   não significa ausência de quebra" + nota do FDR.

---

## Teste de aceitação (antes de fechar a Task 10 no painel)

- [ ] A tela mostra observado + tendência num mesmo gráfico, um território por vez.
- [ ] A incerteza aparece visualmente (banda), não só no texto.
- [ ] 2013 está marcado como "divisão exploratória"; em nenhum lugar há "quebra confirmada".
- [ ] 2023 está sinalizado como pico atípico.
- [ ] O tooltip explica que `quebra_confirmada` nula ≠ "não houve quebra".
- [ ] Nenhuma projeção/forecast na tela.

---

## Armadilhas

- **Medida de tendência em branco** → falta território único no contexto; `HASONEVALUE` exige um
  `territorio_id` selecionado (drill-through ou slicer).
- **Banda "explodindo"** → usar `ABS` na oscilação e manter as lacunas nulas (não forçar zero).
- **Usuário lendo o nulo como "sem quebra"** → sem o tooltip da ressalva, o vazio de `quebra_confirmada`
  é mal interpretado; o tooltip é obrigatório, não decorativo.
- **Somar tendências** → tendência e oscilação não são aditivas entre territórios nem entre anos; usar
  sempre com um território e um ano no contexto (as medidas já protegem com `HASONEVALUE`, não burlar).
