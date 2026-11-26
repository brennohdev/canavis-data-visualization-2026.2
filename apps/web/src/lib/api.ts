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
    const corpo = (await resposta.json().catch(() => null)) as { detail?: unknown } | null;
    const mensagem =
      typeof corpo?.detail === "string" ? corpo.detail : "Não foi possível carregar os dados.";
    throw new ErroApi(resposta.status, mensagem);
  }
  return (await resposta.json()) as ProducaoUF;
}
