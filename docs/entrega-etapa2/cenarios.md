# Parâmetro e cenários — Etapa 2 (Tabela 2.3 do roteiro, letra e · OBRIGATÓRIO)

**Projeto:** CanaVis — Benchmarking regional da produção de cana-de-açúcar na Paraíba
**Requisito:** ao menos 1 parâmetro que permita simular situações diferentes. O parâmetro
precisa **mudar a leitura**, não apenas o número. A ausência trava a nota em 3,0.

## Decisão: parâmetro de campo que troca a REFERÊNCIA de comparação

O parâmetro escolhido é um **parâmetro de campo** (field parameter) que troca contra qual
referência a produtividade da região é lida. Isso responde diretamente ao feedback da Etapa 1
("a comparação regional precisa estar ligada à decisão") e usa as três medidas de desvio que já
existem no modelo (`powerbi/modelo.tmdl`):

- **Desvio vs seleção** — compara com a média do conjunto atualmente selecionado na tela
  (`ALLSELECTED`). Referência "móvel": quem está no filtro.
- **Desvio vs grupo** — compara com a média do **mesmo tier** da unidade
  (`KEEPFILTERS(dim_territorio[tier] = Tier)`). Referência de **pares semelhantes** (Task 4).
- **Participação regional** — peso da unidade no total do nível. Referência "o todo".

As três são medidas reais e testadas. O parâmetro de campo deixa o usuário alternar qual delas
governa o visual de comparação da tela principal.

## Por que isso muda a leitura (e não só o número)

A Paraíba está no tier **"media escala"** (14 UFs: além da PB, Bahia, Ceará, RN, Sergipe,
Maranhão, Piauí, Pará, Amazonas, ES, RJ, RS, SC, Tocantins). Os gigantes (SP, MG, GO, MS, PR,
além de AL e PE) estão no tier **"grande escala industrial"**.

- Comparada ao **conjunto nacional inteiro** (desvio vs seleção com todas as UFs), a PB parece
  muito abaixo — porque está sendo medida contra SP, que sozinho é 56,8% da produção.
- Comparada aos **pares do mesmo tier** (desvio vs grupo), a leitura muda: a pergunta passa a ser
  "entre estados de porte parecido, a PB é eficiente?" — que é a decisão real do gerente, não
  "a PB é menor que São Paulo" (o que todo mundo já sabe).

Essa é a diferença entre um número que muda e uma **leitura** que muda: o mesmo valor de
produtividade conta uma história diferente dependendo da referência, e é isso que o parâmetro
expõe.

## Tabela 2.3 — Cenários simulados

| Cenário | Valor do parâmetro | O que muda no relatório | Leitura e implicação para a persona |
|---------|--------------------|-------------------------|-------------------------------------|
| **Base** | Desvio vs seleção (todas as UFs) | O visual de comparação mede a PB contra a média de todas as 27 UFs; o desvio aparece fortemente negativo | "A PB está muito abaixo da média nacional" — mas essa média é puxada por São Paulo. Leitura de contexto amplo, pouco acionável para decidir plantio. |
| **Alternativo 1** | Desvio vs grupo (tier "media escala") | A referência passa a ser a média das 14 UFs do mesmo porte; o desvio recalcula contra pares comparáveis e o ranking reordena dentro do grupo | "Entre estados de porte parecido, onde a PB está?" Referência justa (Task 4). Sustenta decisão de meta e priorização: dá para perseguir a eficiência dos pares reais, não a de SP. |
| **Alternativo 2** | Participação regional | O visual passa a mostrar o peso da PB no total nacional (%), não o desvio de eficiência | "Quanto a PB representa da produção do país?" Leitura de escala/relevância, não de eficiência. Mostra que porte e eficiência são perguntas distintas — reforça por que o tier existe. |

> Ajuste livre: se preferir que o cenário-base já seja o tier (pares), inverta Base e
> Alternativo 1. O importante é os três cenários existirem e cada um mudar a leitura.

## Passo a passo no Power BI — parâmetro de campo

1. **Aba Modelagem → Novo parâmetro → Campos** (não "Numérico"; é um parâmetro de *campo*).
2. Nomear como `Referência de comparação`.
3. Adicionar as três medidas na ordem dos cenários:
   - `Desvio vs seleção`
   - `Desvio vs grupo`
   - `Participação regional`
4. Marcar **"Adicionar segmentação a esta página"** — o Power BI cria o slicer do parâmetro
   automaticamente.
5. No visual dominante da tela Panorama (barras divergentes), colocar o **parâmetro de campo**
   no eixo de valores, no lugar de uma medida fixa. Agora o visual responde ao slicer do
   parâmetro.
6. Garantir que o slicer de **tier** (`dim_territorio[tier]`) esteja na mesma tela: o cenário
   "Desvio vs grupo" só faz sentido com o tier no contexto (a medida usa `SELECTEDVALUE(tier)`).
   Para a PB, deixe a tela com o tier "media escala" selecionável.

### Alternativa (ou complemento): parâmetro numérico de hipótese — "meta de produtividade"

Se quiser também um parâmetro numérico (o roteiro aceita um ou outro; ter os dois é opcional e
rende demonstração forte):

1. **Modelagem → Novo parâmetro → Numérico**. Nome: `Meta de produtividade (t/ha)`.
   Intervalo sugerido: mín 40, máx 100, incremento 1, padrão 65 (a PB fica na casa de 56–65 t/ha
   na série recente).
2. Isso cria uma tabela de parâmetro e um slicer.
3. Criar medida de distância para a meta:
   ```DAX
   Distância da meta (t/ha) =
   VAR Meta = SELECTEDVALUE('Meta de produtividade (t/ha)'[Meta de produtividade (t/ha)])
   RETURN IF( NOT ISBLANK([Produtividade]) && NOT ISBLANK(Meta), [Produtividade] - Meta )
   ```
4. Usar num cartão ("faltam X t/ha para a meta") ou numa linha de referência no gráfico de
   evolução. Cenários: Base = meta no patamar atual; Alternativo = meta no nível dos pares do
   tier; Alternativo = meta ambiciosa (nível do tier grande).

## Teste de aceitação (antes de fechar a issue #13)

- [ ] Existe pelo menos 1 parâmetro (campo ou numérico) com slicer na tela.
- [ ] Trocar o valor do parâmetro muda a leitura do visual (não só o número) — demonstrável nos
      3 cenários da Tabela 2.3.
- [ ] O cenário de pares (desvio vs grupo) recalcula contra o tier e reordena coerentemente.
- [ ] Tabela 2.3 preenchida com o que foi de fato implementado, com a implicação para a persona.

## Armadilhas

- **Parâmetro de campo sem as medidas certas** → o slicer troca o rótulo mas o visual não reage;
  confirme que o parâmetro está no eixo de valores do visual, não só na tela.
- **Desvio vs grupo retornando vazio** → falta o tier no contexto. O slicer de
  `dim_territorio[tier]` precisa estar na tela e com um tier selecionável; a medida exige
  `SELECTEDVALUE(tier)` não vazio.
- **Parâmetro que só muda o número** → o roteiro penaliza. Garanta que a troca muda o eixo/ordem
  ou a pergunta respondida, não apenas a escala do mesmo gráfico.
