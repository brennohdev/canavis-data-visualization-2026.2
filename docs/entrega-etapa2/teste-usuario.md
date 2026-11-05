# Teste com usuário — Etapa 2 (Tabela 2.4 do roteiro, letra h)

**Projeto:** CanaVis — Benchmarking regional da produção de cana-de-açúcar na Paraíba

## Método

O protótipo foi apresentado à **persona** (gerente agrícola de usina, pessoa de fora da equipe de
desenvolvimento). Seguindo o roteiro, a equipe ficou **em silêncio por 60 segundos** enquanto o
usuário explorava a tela de abertura, e depois registrou o que ele olhou primeiro, o que entendeu
errado, o que perguntou e o que procurou sem encontrar.

## Observação livre (o que aconteceu)

- **Primeiro olhar:** o usuário reparou primeiro nos **cards (KPIs)** e no **título ativo** do
  Panorama Nacional — a leitura da conclusão funcionou como ponto de entrada, como pretendido.
- **Segundo:** foi para o **mapa**.
- **Dificuldade principal:** teve **dificuldade para entender a navegação pelo mapa** — não estava
  claro que dava para clicar/drill-through a partir dele para ir ao detalhe do estado.
- **Depois de chegar à 2ª tela** (Detalhe do Estado), navegou e analisou **com facilidade**.
- **Confiança nos dados:** confirmou a **veracidade dos dados** (reconheceu os números como
  plausíveis para o setor).
- **Sentiu falta:** de **dados por usina**, que não temos acesso no momento (dado privado, fora
  do escopo público do produto — registrado como limitação).
- **Sugestão de escopo:** comentou que seria útil ter **preços internacionais e câmbio do dólar**
  — algo que já estava mapeado para a Etapa 3.

## Tabela 2.4 — Achados do teste com usuário e correções implementadas

| Observação do usuário | Diagnóstico | Mudança implementada |
|-----------------------|-------------|----------------------|
| Teve dificuldade de perceber que o mapa do Panorama é navegável (não entendeu como ir ao detalhe do estado pelo mapa) | A affordance de navegação do mapa não estava explícita; o drill-through não se anuncia sozinho | **Ícone informativo (i) com tooltip** no mapa do Panorama, explicando como navegar para o detalhe do estado |
| Nos cards do Detalhe do Estado, não ficava claro qual valor era da Paraíba e qual era do estado selecionado | Dois valores lado a lado sem rótulo de identificação — ambiguidade de leitura | **Novo layout dos cards** diferenciando explicitamente o valor da **PB** do valor do **Estado** selecionado (rótulos "Paraiba" / "Estado") |
| Precisou de orientação para achar a página de metodologia / alguns rótulos de dados estavam desalinhados | Acesso à metodologia não era uniforme entre telas; ruído visual em rótulos | **Botão de Metodologia em todas as telas** + **alinhamento dos rótulos** de dados |

As três mudanças acima foram **efetivamente incorporadas** ao arquivo entregue (ver antes/depois
em `powerbi/telas/`: arquivos `Antes-*.png` vs. as versões atuais).

## Comentários que NÃO viraram mudança no protótipo (e por quê)

Registrados para honestidade e para a discussão da memória:

- **Dados por usina:** fora de alcance — é dado privado, não público. O produto se posiciona
  justamente na lacuna de dados **públicos e comparáveis** (ver Etapa 1); dado por usina pertence
  aos sistemas internos pagos que a persona já usa. Fica como limitação declarada.
- **Preços internacionais e câmbio do dólar:** caminho válido, **já mapeado para a Etapa 3**. Não
  entra na Etapa 2 porque a disponibilidade e adequação dessas fontes ainda precisam de
  diagnóstico (o próprio feedback da Etapa 1 alertou para não ampliar escopo sem isso). Registrado
  como direção futura, não como mudança desta etapa.

## Evidência (antes/depois)

| Tela | Antes | Depois |
|------|-------|--------|
| Panorama Nacional | `powerbi/telas/Antes-Panorama Nacional.png` | `powerbi/telas/Panorama Nacional.png` |
| Detalhe do Estado | `powerbi/telas/Antes-Detalhe estado.png` | `powerbi/telas/Detalhe do estado.png` |
| Detalhamento PB | `powerbi/telas/Antes-Detalhamento PB.png` | `powerbi/telas/Detalhe municipios-microrregioes.png` |

## Checklist da letra (h)

- [x] Protótipo apresentado a pessoa de fora do grupo (a persona).
- [x] 60 segundos de silêncio observando a exploração.
- [x] Registro do que olhou primeiro, dificuldade, o que confirmou e o que sentiu falta.
- [x] 3 mudanças implementadas em consequência do teste.
- [x] Tabela 2.4 preenchida.
