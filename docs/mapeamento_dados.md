# Mapeamento de dados — Etapa 1

Documento de trabalho interno da POC. Registra o que foi efetivamente testado,
o que foi apenas localizado, e o que sustenta o dicionário e os indicadores do
documento final. Tudo que aparece como "coletado" foi baixado de verdade pelos
scripts em `poc/`.

## 1. Catálogo de fontes

| # | Fonte | Órgão | O que traz | Granularidade | Recorte temporal | Acesso | Situação na POC | Papel no produto |
|---|-------|-------|-----------|---------------|------------------|--------|-----------------|------------------|
| 1 | PAM — Tabela 1612 | IBGE (via API SIDRA) | Área plantada, área colhida, quantidade produzida, rendimento médio, valor da produção da cana | Município, microrregião, mesorregião, UF, região, Brasil | Anual, 1974–2025 | API REST JSON, aberta, sem cadastro | **Coletado** (municípios PB, todas UFs, série PB) | **Base principal** — produtividade e benchmarking regional |
| 2 | Série Histórica da Cana | CONAB | Área, produção de cana, produção de açúcar (mil t), etanol anidro/hidratado/total (mil L), ATR (kg/t) | UF | Safra (ano agrícola), 2005/06 em diante | Arquivo `.txt` (`;`, latin-1), aberto | **Coletado** (470 linhas, 22 safras PB) | **Base principal** — camada industrial e mix açúcar/etanol |
| 3 | Vendas de etanol hidratado por município | ANP | Volume vendido de etanol hidratado, com código IBGE do município | Município | Anual, 1990–2024 | CSV aberto (`;`, UTF-8) | **Coletado** (5.079 linhas da PB, 348 municípios) | Contexto de demanda; casa com PAM pelo código IBGE |
| 4 | Produção de etanol anidro/hidratado por UF | ANP | Produção mensal de etanol por tipo e UF | UF | Mensal, 2012–2026 | CSV aberto (`;`, UTF-8) | **Coletado** (350 linhas da PB) | Contexto industrial mensal (complementa CONAB) |
| 5 | Comex Stat | MDIC/SECEX | Exportação de açúcar e etanol (NCM/SH4) | Município e UF | Mensal, 1997– | API JSON | **Bloqueado** — API atrás de Cloudflare (challenge JS), inviável sem navegador headless | Contexto de destino da produção (etapa futura) |
| 6 | Novo CAGED | MTE | Emprego formal no setor sucroalcooleiro (CNAE) | Município | Mensal | Dados abertos (FTP/painel) | Localizado, não coletado | Contexto socioeconômico (emprego) |

Decisão de escopo: as fontes 1 e 2 sustentam o produto e o dicionário da Etapa 1
porque casam com a cadência anual/safra da decisão da persona. As fontes 3 e 4 (ANP)
foram efetivamente coletadas e entram como contexto de demanda e produção industrial,
com a vantagem de o arquivo municipal trazer o código IBGE, o que permite juntar com a
PAM sem ambiguidade de nome. A fonte 5 (Comex) tem API pública, mas está protegida por
Cloudflare com desafio de JavaScript: um GET simples de metadados passa, mas a consulta
de dados é barrada; acessá-la exigiria automação de navegador, desproporcional para uma
fonte apenas de contexto. Fica registrada para etapa futura. A fonte 6 (CAGED) não foi
baixada nesta POC.

Nota de honestidade da POC: numa primeira passada, as fontes ANP foram descartadas cedo
demais, por chute de URL. Ao raspar os links reais das páginas de dados abertos, os
arquivos se mostraram acessíveis e relevantes. O Comex, ao contrário, foi testado a
fundo (headers de origem, várias rotas) e o bloqueio é real, não falta de tentativa.

## 2. Variáveis brutas disponíveis

### IBGE PAM (Tabela 1612), produto cana-de-açúcar (código 2696)

| Código | Variável | Unidade |
|--------|----------|---------|
| 109 | Área plantada | hectares |
| 216 | Área colhida | hectares |
| 214 | Quantidade produzida | toneladas |
| 112 | Rendimento médio da produção | kg/ha |
| 215 | Valor da produção | mil reais |

### CONAB Série Histórica da Cana

| Coluna | Descrição | Unidade |
|--------|-----------|---------|
| ano_agricola | Safra (ex.: 2023/24) | — |
| uf | Unidade federativa | — |
| area_plantada_mil_ha | Área plantada | mil hectares |
| producao_mil_t | Produção de cana | mil toneladas |
| producao_acucar_mil_t | Produção de açúcar | mil toneladas |
| producao_etanol_anidro_mil_l | Etanol anidro | mil litros |
| producao_etanol_hidratado_mil_l | Etanol hidratado | mil litros |
| producao_etanol_total_mil_l | Etanol total | mil litros |
| produtcao_atr_kg_t | ATR (açúcar total recuperável) | kg/t |

## 3. Indicadores derivados propostos

Todos calculáveis a partir das variáveis brutas acima. Servem de base para o
item (i) do documento.

1. **Produtividade da cana (rendimento)**
   - Fórmula: quantidade produzida (t) ÷ área colhida (ha)
   - Unidade: t/ha (a PAM já entrega uma versão em kg/ha na variável 112)
   - Sentido: maior é melhor
   - Referência: média estadual, média nacional, safra anterior

2. **Participação regional na produção**
   - Fórmula: produção do município (ou UF) ÷ produção do agregado (PB ou Brasil) × 100
   - Unidade: %
   - Sentido: contextual (mede concentração/peso)
   - Referência: total estadual ou nacional

3. **Variação safra a safra**
   - Fórmula: (valor do ano t − valor do ano t−1) ÷ valor do ano t−1 × 100
   - Unidade: %
   - Sentido: depende da variável (produtividade maior é melhor)
   - Referência: período anterior

4. **Mix de destino da cana (açúcar vs. etanol)** — via CONAB
   - Fórmula: produção de açúcar convertida em ATR ÷ ATR total, ou razão etanol/açúcar
   - Unidade: % ou proporção
   - Sentido: contextual (decisão estratégica da persona)
   - Referência: média nacional, safra anterior

5. **Desvio de produtividade vs. referência regional**
   - Fórmula: (produtividade da unidade − produtividade média do grupo) ÷ média do grupo × 100
   - Unidade: %
   - Sentido: positivo é melhor
   - Referência: média da microrregião/UF/Nordeste

## 4. Limitações já observadas nos dados coletados

1. **Supressão em municípios pequenos (IBGE):** municípios com pouca produção
   retornam `-` em vez de valor, o que impede cálculo de produtividade nesses casos.
2. **Descompasso de calendário:** IBGE usa ano civil; CONAB usa safra (ano agrícola).
   Cruzar as duas bases exige uma decisão explícita de alinhamento temporal.
3. **Granularidade diferente:** IBGE chega ao município; CONAB para na UF. A camada
   industrial (açúcar/etanol) não existe em nível municipal público.
4. **Defasagem:** a PAM fecha com cerca de um ano de atraso; a CONAB divulga
   estimativas por levantamento antes do número consolidado.
