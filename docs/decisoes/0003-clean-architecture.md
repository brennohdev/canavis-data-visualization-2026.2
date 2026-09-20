# 0003 — Separar domínio, fontes e pipeline com regra de dependência

**Status:** Aceita

## Contexto

Os scripts de descoberta misturavam requisição HTTP, limpeza e cálculo num mesmo arquivo, com
código repetido entre fontes. Isso não sustentaria a evolução para uma aplicação.

## Decisão

Organizar o pacote `canavis` em camadas, com as dependências apontando para dentro:

- **domain:** indicadores como funções puras sobre `DataFrame`, sem conhecer HTTP ou arquivo.
- **sources:** adaptadores por fonte, atrás de uma interface comum (`DataSource`), com um
  cliente HTTP único compartilhado.
- **pipeline:** orquestra extract, transform e build entre as camadas de dados.

Configuração (URLs, códigos, caminhos) fica em `config/*.yaml`, fora do código.

## Consequências

O domínio é testável sem rede. Adicionar uma fonte é registrar um adaptador, não reescrever o
pipeline. A aplicação da Etapa 3 importará `canavis.domain` e `canavis.pipeline` em vez de
copiar lógica. O custo é mais arquivos e uma curva inicial maior que a de scripts soltos.
