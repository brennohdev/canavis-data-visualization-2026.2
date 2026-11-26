# 0021 — Arquitetura em camadas da API

**Status:** Aceita
**Evidência:** `apps/api/src/canavis_api`, `apps/api/tests/test_arquitetura.py`

## Contexto

A fatia andante da API (#28) tinha `routers/` e `repositories/`. O repositório misturava
entidade, regra do intervalo de anos, tabela de UFs e acesso ao DuckDB. A configuração era um
singleton com `lru_cache` lido dentro das rotas, e a `main.py` conhecia `Settings`. Os testes
dependiam de `monkeypatch.setenv` e `cache_clear()`. O OpenAPI não descrevia as respostas.

## Decisão

**Camadas** (nomes em português, como o resto do código):

| Pacote | Conteúdo | Pode importar |
|---|---|---|
| `dominio/` | `Uf`, `uf_por_sigla`, `ProducaoUF`, `ErroDeDominio`, `ProducaoNaoEncontrada`, `DadosIndisponiveis` | só stdlib |
| `aplicacao/` | porta `ProducaoRepositorio`, casos de uso `ConsultarProducaoUF` e `VerificarDados` | `dominio` |
| `repositorios/` | `ProducaoDuckDB` (única que importa `duckdb`) | `aplicacao.portas`, `dominio` |
| `apresentacao/` | `ControladorBase`, controladores, esquemas Pydantic, `registrar_erros`, `montar_spa` | `aplicacao`, `dominio` |
| `composicao.py` | `create_app(settings=None)`, raiz de composição | todas |

`main.py` tem duas linhas (`create_app()`). Não cita `Settings`, `environ` nem `CANAVIS_*`.
`test_arquitetura.py` verifica essas regras por AST.

**D1. DI por construtor, feita à mão** em `composicao.py`. Sem container, sem `Depends` para
serviços, sem `lru_cache`. `Settings.from_env(env=None)` é a única leitura do ambiente. Os
testes passam um `Settings` pronto ou um repositório falso.

**D2. Sem regra fixa de anos.** `ANO_MIN` e `ANO_MAX` saíram da API. Ano sem linha na gold
vira `ProducaoNaoEncontrada` (404). Efeito aceito: com os parquet ausentes, `ano=1999` passa a
dar 503 (antes 404). A sigla desconhecida continua dando 404 antes de tocar nos dados. O
endpoint de anos disponíveis fica para a #30. No front, `ANO_MIN/ANO_MAX` de `lib/busca.ts`
seguem como fonte de verdade da URL (ADR 0014).

**D3. Esquemas Pydantic** (`ProducaoUFResposta`, `SaudeResposta`, `ErroResposta`) só na
apresentação. A entidade de domínio é um `dataclass(frozen=True)`. O JSON não mudou: mesmas
chaves, mesma ordem, nulos como `null`. O `/openapi.json` passa a descrever as respostas.

**Mapa de exceção para HTTP** (`apresentacao/erros.py`): `ProducaoNaoEncontrada` vira 404 e
`DadosIndisponiveis` vira 503, com corpo `{"detail": ...}`. O parquet ausente ou corrompido
(`duckdb.Error`) vira `DadosIndisponiveis`. O caminho vai só para o log, nunca para a resposta.

**Settings enxuto.** `port` e `log_level` saíram: a porta é do uvicorn (comando fixo do
Dockerfile) e a API deixa de ler `CANAVIS_PORT` e `CANAVIS_LOG_LEVEL`. Sem segredos e sem
caminho absoluto no código: os defaults são relativos (`data/processed`, `apps/web/dist`) e os
absolutos ficam no Dockerfile.

**Sem comentários.** `test_sem_comentarios.py` falha com qualquer comentário ou docstring em
`apps/api/src` e `apps/api/tests`.

## Contradições resolvidas

- Planejamento 7.2 listava `routers/, schemas/, services/, repositories/`. Ficam
  `apresentacao/, aplicacao/, dominio/, repositorios/`. `services` vira casos de uso nomeados
  por ação.
- ADR 0003 põe indicadores em `src/canavis/domain` e fala em `config/*.yaml`. O `dominio/` da
  API guarda só conceitos da fatia HTTP (UF, produção por UF, erros). Indicadores (#29) e
  engine (#34) ficam em `src/canavis/domain` e entram na API pela camada `aplicacao`. Caminhos
  de deploy seguem em variável de ambiente (`Settings.from_env`); `config/*.yaml` fica para
  fontes e regras.
- ADR 0013 pede DuckDB somente leitura com views. Hoje cada consulta abre `:memory:` e lê o
  parquet com `read_parquet(?)` parametrizado. Mantido nesta fatia; views e conexão somente
  leitura ficam para a #30, dentro de `repositorios/`.
- ADR 0018 item 5 (`CANAVIS_PORT` configurável): a API não lê mais essa variável.

## Consequências

- Testes de caso de uso rodam sem DuckDB e sem arquivos.
- Pontos de extensão: #29 funções em `src/canavis/domain` consumidas por novos casos de uso;
  #30 novos controladores (estendem `ControladorBase`), casos de uso e métodos de porta,
  export do OpenAPI, endpoint de anos disponíveis, views somente leitura; #31
  `src/canavis/sources/intl` e um repositório novo em `repositorios/` lendo `data/external`;
  #34 `src/canavis/domain/regras` chamada por um caso de uso de insights.
- O Dockerfile e o `.env.example` ainda definem `CANAVIS_PORT` e `CANAVIS_LOG_LEVEL`, que a
  API ignora.
