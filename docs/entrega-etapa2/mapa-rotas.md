# Mapa de rotas — Etapa 2 (Tabela 2.1 do roteiro, letra c · OBRIGATÓRIO)

**Projeto:** CanaVis — Benchmarking regional da produção de cana-de-açúcar na Paraíba
**Requisito:** 3+ telas com navegação explícita, 1+ transição que transporta contexto
(drill-through), 3+ segmentações relevantes. A ausência trava a nota em 3,0.

> Status desta task: estrutura de telas e navegação pode ser montada já. O drill-through só
> mostra "o recorte, não o total" de verdade quando o modelo (Task 6 / #10) e as medidas
> (Task 7 / #11) estiverem no `.pbix`. Itens que dependem de dados estão marcados com **[dep]**.

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

## Passo a passo de implementação no Power BI

### A. Criar as 3 páginas
1. Criar 3 páginas: `Panorama Nacional`, `Detalhe do Estado`, `Detalhe do Município`.
2. Renomear as páginas (clique direito na aba → Renomear) — nomes claros ajudam na navegação.

### B. Drill-through que transporta contexto (Panorama → Estado) — o item obrigatório
1. Na página **Detalhe do Estado**, no painel *Visualizações*, localizar a área
   **Drill-through** (Drillthrough).
2. **[dep]** Arrastar o campo `dimTerritorio[uf]` (ou equivalente do modelo da Task 6) para a
   área *Drill-through*. O Power BI cria automaticamente o botão de voltar.
3. **[dep]** Na página **Panorama Nacional**, clicar com o botão direito em uma UF (barra ou
   ponto no mapa) → *Drill through* → *Detalhe do Estado*. A página de destino abre filtrada
   só por aquela UF.
4. Repetir B1–B3 para **Detalhe do Estado → Detalhe do Município**, usando o campo de
   microrregião/município na área *Drill-through* da página de município.

### C. Botões de navegação explícita (fluxo e voltar)
1. *Inserir → Botões → Em branco* (ou *Seta para a esquerda* para "voltar").
2. Selecionar o botão → painel *Formatar botão → Ação → Tipo: Navegação de página → Destino:
   a página desejada*.
3. Colocar um botão "← Panorama" nas páginas de detalhe. (O botão de voltar do drill-through já
   retorna à origem do drill; o botão de navegação garante o caminho explícito pedido no roteiro.)

### D. Segmentações
1. *Inserir → Segmentação de dados* para Ano, Indicador e Tier/região.
2. **[dep]** Vincular aos campos reais do modelo.
3. Opcional: *Sincronizar segmentações* (menu Exibir) para o filtro de Ano valer nas 3 telas.

### E. Título ativo na tela de destino (adianta a Task 11)
- **[dep]** Criar medida de título, ex.: `Título Estado = "Detalhe de " & SELECTEDVALUE(dimTerritorio[uf])`
  e usar num cartão de texto/título. Assim o destino anuncia o recorte herdado, reforçando que
  o contexto foi transportado.

---

## Teste de aceitação (fazer antes de fechar a issue #12)

- [ ] Existem 3+ telas com navegação funcionando.
- [ ] Clicar na Paraíba no Panorama abre o Detalhe do Estado mostrando **só a PB** (recorte, não o total). **[dep]**
- [ ] A transição Estado → Município transporta o recorte selecionado. **[dep]**
- [ ] Há botão de voltar / navegação explícita entre as telas.
- [ ] Existem 3+ segmentações relevantes (ano, indicador, tier), nenhuma decorativa.
- [ ] Tabela 2.1 preenchida com o que foi de fato implementado.

## Armadilhas

- Drill-through **sem o campo certo** na área de destino → o item do menu não aparece ou não
  filtra. O campo que transporta o contexto tem que estar na well *Drill-through* da página de
  destino.
- Destino **mostrando o total** em vez do recorte → invalida o requisito. Confirmar que os
  visuais de detalhe respeitam o filtro herdado.
- Filtro **decorativo** → o roteiro penaliza. Todo slicer deve responder a uma pergunta
  analítica.
