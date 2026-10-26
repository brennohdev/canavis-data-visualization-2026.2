# Paleta e acessibilidade — Etapa 2 (roteiro, letra g)

**Projeto:** CanaVis — Benchmarking regional da produção de cana-de-açúcar na Paraíba

## Decisão de identidade visual (trajetória do projeto)

Na Etapa 1, o projeto usou azul institucional (`#1F497D`) justamente por **ainda não ter uma
identidade visual própria** — a entrega ficou com um aspecto "padrão", adequado a uma fase de
descoberta e enquadramento. Na Etapa 2 o projeto toma forma de produto, e adotamos o
**verde-cana (`#2F6B3C`)** como cor primária: ele amarra a identidade ao tema (cana-de-açúcar,
lavoura, campo), coisa que o azul genérico não fazia. A mudança é consciente e faz parte da
trajetória a ser contada na apresentação (rubrica: "o que veio da Etapa 1 e o que foi revisto").

## Paleta final (máximo 5 cores de dado)

### Cores de dado

| Papel | Hex | Uso |
|-------|-----|-----|
| Verde-cana primário (marca) | `#2F6B3C` | Paraíba em destaque, barra/linha principal, títulos, "acima da referência" |
| Verde claro | `#7BA886` | Séries secundárias, hover, 2º nível de hierarquia |
| Âmbar (acento divergente) | `#E08A1E` | "Abaixo da referência" nas barras divergentes, destaque |
| Azul-ardósia (apoio) | `#3A6EA5` | 3ª série; categoria industrial / mix |
| Cinza-ardósia (neutro de dado) | `#6B7785` | Demais regiões, "sem informação", linha de referência |

### Neutros (não contam como codificação de dado)

| Papel | Hex |
|-------|-----|
| Fundo da tela | `#F2F2F2` (ou `#FFFFFF` para projeção) |
| Texto principal | `#1A1A1A` |
| Texto secundário | `#50565E` |
| Linhas de grade | `#D5D9DE` |

## Contraste verificado (WCAG 2.1)

Mínimos WCAG: 4,5:1 para texto normal, 3:1 para texto grande e elementos gráficos. Projeção lava
o contraste, então as escolhas de texto miram folga.

| Par | Razão aprox. | Veredito |
|-----|--------------|----------|
| `#2F6B3C` texto sobre `#F2F2F2` | 5,0:1 | Passa AA (texto) / AAA (texto grande) |
| Branco sobre `#2F6B3C` | 4,8:1 | Passa AA — rótulo branco dentro da barra verde |
| `#1A1A1A` texto sobre `#F2F2F2` | 16:1 | AAA — corpo de texto |
| `#3A6EA5` sobre `#F2F2F2` | 4,0:1 | Texto grande e formas |
| `#E08A1E` sobre `#F2F2F2` | 2,4:1 | **Apenas formas grandes/barras; nunca texto fino** |
| `#7BA886` sobre `#F2F2F2` | 2,0:1 | **Apenas preenchimento; nunca texto** |

**Regra de uso:** âmbar e verde claro são preenchimento de formas (barras, áreas), não cor de
texto. Rótulo de valor: texto escuro (`#1A1A1A`) fora da barra, ou branco dentro da barra verde.

## Daltonismo

O par de risco clássico é **verde × vermelho** (protanopia/deuteranopia, ~8% dos homens). Como a
primária é verde, o acento divergente é **âmbar (`#E08A1E`)**, não vermelho: verde-cana × âmbar é
distinguível nos três tipos de daltonismo. Salvaguardas:

- **Não depender só da cor.** Nas barras divergentes, "acima/abaixo" também é lido pela direção
  da barra em relação ao zero — legível inclusive em escala de cinza.
- **"Sem informação" em cinza neutro** (`#6B7785`), nunca em cor de dado — alinha com a
  salvaguarda de ausências declarada na Etapa 1.

## Checklist da letra (g)

- [x] Paleta com no máximo 5 cores de dado.
- [x] Verificada para daltonismo (par divergente verde × âmbar, não verde × vermelho).
- [x] Contraste adequado documentado (razões WCAG por par).
- [ ] Testar em projeção, fora da tela do próprio computador (projetor lava `#7BA886` e `#D5D9DE`).
- [ ] Ordenação intencional das categorias (por valor/desvio, nunca alfabética).
- [ ] Sem eixo truncado sem aviso, 3D, pizza >3 fatias ou indicador sem denominador.

## Arquivo de tema do Power BI

Importável em `powerbi/canavis-theme.json` (Exibir → Temas → Procurar temas). Usa os mesmos hex
desta paleta, para a imagem de fundo do Figma e o tema do Power BI não divergirem.
