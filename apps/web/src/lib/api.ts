// Tipos escritos à mão para a fatia vertical; a Task 6 passa a gerá-los
// do OpenAPI com openapi-typescript.
export interface ProducaoUF {
  sigla: string;
  territorio_id: string;
  nome: string;
  ano: number;
  produtividade_t_ha: number | null;
  quantidade_produzida_t: number | null;
  area_colhida_ha: number | null;
}

export class ErroApi extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export async function buscarProducaoUF(sigla: string, ano: number): Promise<ProducaoUF> {
  const resposta = await fetch(
    `/api/v1/uf/${encodeURIComponent(sigla)}/producao?ano=${encodeURIComponent(String(ano))}`,
  );
  if (!resposta.ok) {
    let mensagem = "Não foi possível carregar os dados.";
    try {
      const corpo = (await resposta.json()) as { detail?: unknown };
      if (typeof corpo.detail === "string") mensagem = corpo.detail;
    } catch {
      // corpo sem JSON: mantém a mensagem padrão
    }
    throw new ErroApi(resposta.status, mensagem);
  }
  return (await resposta.json()) as ProducaoUF;
}
