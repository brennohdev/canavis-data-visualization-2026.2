# Mapa de rotas — Etapa 2 (Tabela 2.1 do roteiro, letra c · OBRIGATÓRIO)

**Projeto:** CanaVis — Benchmarking regional da produção de cana-de-açúcar na Paraíba
**Requisito:** 3+ telas com navegação explícita, 1+ transição que transporta contexto
(drill-through), 3+ segmentações relevantes. A ausência trava a nota em 3,0.

> Status: o modelo estrela (Task 6) e as medidas DAX (Task 7) já estão no `.pbix`, e os tiers
> (Task 4) já estão materializados em `dim_territorio[tier]`. Então toda a navegação pode ser
> montada e testada com dados reais. Os nomes de campo abaixo são os do modelo real
> (`powerbi/modelo.tmdl`).

---

## Telas do relatório

| Tela | Layout (Task 5) | Papel | Pergunta analítica (Etapa 1) |
|------|-----------------|-------|------------------------------|
| 1. Panorama Nacional | B — comparação dominante | Entrada; posicionamento relativo da região | Como a produtividade da região se posiciona frente às outras? |
| 2. Detalhe do Estado | C — trajetória + ranking | Evolução e ranking de microrregiões da UF selecionada | Como a produtividade evoluiu? Quais microrregiões ganham/perdem? |
| 3. Detalhe do Município | série histórica + mix | Série e mix açúcar/etanol do recorte | Como se divide o destino da cana na região? |

---

## Tabela 2.1 — Mapa de rotas implementado (rascunho)

| Origem | Destino | Mecanismo | Contexto transportado | Pergunta que a transição responde |
|--------|---------|-----------|-----------------------|-----------------------------------|
| Panorama Nacional | Detalhe do Estado | **Drill-through** | UF selecionada | "Como as microrregiões dessa UF se comparam entre si e evoluíram ao longo das safras?" |
| Detalhe do Estado | Detalhe do Município | **Drill-through** | Microrregião/município selecionado | "Como é a série histórica e o mix açúcar/etanol desse município?" |
| Detalhe do Estado / Município | Panorama Nacional | **Botão** (navegação de página) | — (retorno ao panorama) | "Voltar à visão geral para escolher outra região." |

**A primeira linha é a transição obrigatória que transporta contexto.** As demais podem ser
botões. Preencher/ajustar conforme a implementação real.

---

## Segmentações (slicers) — mínimo 3, relevantes

| Slicer | Tela(s) | Por que é relevante (não decorativo) |
|--------|---------|--------------------------------------|
| Ano / safra | todas | Define o período da leitura; a pergunta de decisão é safra a safra |
| Indicador | 1 e 2 | Troca o que está sendo comparado (liga com o parâmetro de campo da Task 9) |
| Tier / região de comparação | 1 | Escolhe os pares semelhantes (Task 4) — responde direto ao feedback |

Evitar slicer decorativo (ex.: filtro de "fonte de dados" na tela principal). Estado e Município
como slicer são opcionais e só se não forem redundantes com o drill-through.

---

## Particularidade do modelo (ler antes de implementar)

A `dim_territorio` **não tem um campo "UF" separado**: os três níveis (município, microrregião,
UF) convivem na mesma dimensão, distinguidos pela coluna `nivel_territorial` (valores
`"municipio"`, `"microrregiao"`, `"uf"`). O identificador é `territorio_id` (ex.: `"uf:25"`,
`"municipio:2500106"`) e o nome legível é `nome_territorio`. As medidas já respeitam isso: a
`Produtividade` só calcula com um único `nivel_territorial` no contexto; as medidas industriais
exigem `nivel_territorial = "uf"`; a de município exige `"municipio"`.

Consequência prática: cada página precisa de um **filtro de nível** fixo. A tela Panorama
Nacional filtra `nivel_territorial = "uf"`; o Detalhe do Estado também trabalha em UF (e, se
houver ranking de microrregião, num visual com filtro de microrregião); o Detalhe do Município
filtra `nivel_territorial = "municipio"`. Sem isso, as medidas retornam vazio de propósito.

## Passo a passo de implementação no Power BI

### A. Criar as 3 páginas
1. Criar 3 páginas: `Panorama Nacional`, `Detalhe do Estado`, `Detalhe do Município`.
2. Renomear as páginas (clique direito na aba → Renomear).
3. Em cada página, no painel *Filtros → Filtros nesta página*, arrastar
   `dim_territorio[nivel_territorial]` e fixar o valor do nível daquela tela (`uf` no Panorama e
   no Estado; `municipio` no Município). Isso garante que as medidas calculem.

### B. Drill-through que transporta contexto (Panorama → Estado) — o item obrigatório
1. Na página **Detalhe do Estado**, no painel *Visualizações*, localizar a área
   **Drill-through** (Drillthrough, logo abaixo de "Filtros").
2. Arrastar `dim_territorio[nome_territorio]` para a área *Drill-through*. O Power BI cria
   automaticamente o botão de voltar no canto da página.
3. Na página **Panorama Nacional**, clicar com o botão direito em uma UF (barra do gráfico de
   comparação ou região no mapa) → *Drill through* → *Detalhe do Estado*. A página de destino
   abre filtrada só por aquela UF.
4. Repetir B1–B3 para **Detalhe do Estado → Detalhe do Município**: na página Município, colocar
   `dim_territorio[nome_territorio]` na área *Drill-through*; o gatilho é clicar num município do
   ranking/visual da tela de estado.

> Observação sobre os níveis: como `nome_territorio` existe nos três níveis, use o drill-through
> a partir de um visual que já esteja filtrado pelo nível de origem (o Panorama está em `uf`, logo
> só UFs disparam o drill para o Estado). O filtro de página de nível (passo A3) da tela de
> destino garante que o detalhe mostre o recorte certo.

### C. Botões de navegação explícita (fluxo e voltar)
1. *Inserir → Botões → Em branco* (ou *Seta para a esquerda* para "voltar").
2. Selecionar o botão → painel *Formatar botão → Ação → Tipo: Navegação de página → Destino:*
   a página desejada.
3. Colocar um botão "← Panorama" nas páginas de detalhe. (O botão de voltar do drill-through
   retorna à origem do drill; o botão de navegação garante o caminho explícito pedido no
   roteiro.)

### D. Segmentações (mínimo 3)
1. *Inserir → Segmentação de dados* para:
   - **Ano:** `dim_calendario[ano]`.
   - **Tier / grupo de comparação:** `dim_territorio[tier]` (no Panorama).
   - **Indicador:** parâmetro de campo da Task 9 (ver `cenarios.md`), ou, se preferir um slicer
     simples antes da Task 9, um slicer de `dim_fonte[fonte]`.
2. Opcional: *Exibir → Sincronizar segmentações* para o filtro de Ano valer nas 3 telas.

### E. Título ativo na tela de destino (adianta a Task 11)
- Criar medida de título:
  `Título Estado = "Detalhe de " & SELECTEDVALUE(dim_territorio[nome_territorio])`
  e usar num cartão de texto. Assim o destino anuncia o recorte herdado, reforçando que o
  contexto foi transportado.

---

## Teste de aceitação (fazer antes de fechar a issue #12)

- [ ] Existem 3+ telas com navegação funcionando.
- [ ] Clicar na Paraíba no Panorama abre o Detalhe do Estado mostrando **só a PB** (recorte, não o total).
- [ ] A transição Estado → Município transporta o recorte selecionado.
- [ ] Há botão de voltar / navegação explícita entre as telas.
- [ ] Existem 3+ segmentações relevantes (ano, tier, indicador), nenhuma decorativa.
- [ ] Tabela 2.1 preenchida com o que foi de fato implementado.

## Armadilhas

- Drill-through **sem o campo certo** na área de destino → o item do menu não aparece ou não
  filtra. O campo que transporta o contexto tem que estar na well *Drill-through* da página de
  destino.
- Destino **mostrando o total** em vez do recorte → invalida o requisito. Confirmar que os
  visuais de detalhe respeitam o filtro herdado.
- Filtro **decorativo** → o roteiro penaliza. Todo slicer deve responder a uma pergunta
  analítica.
