import type { ProducaoUF } from "./api";
import { formatarUmaCasa } from "./formato";

export function textoProducao(p: ProducaoUF): string {
  if (p.quantidade_produzida_t === null || p.produtividade_t_ha === null) {
    return `Em ${p.ano}, não há dado de produção de cana para ${p.nome}.`;
  }
  const milhoes = formatarUmaCasa(p.quantidade_produzida_t / 1_000_000);
  const produtividade = formatarUmaCasa(p.produtividade_t_ha);
  return `Em ${p.ano}, ${p.nome} produziu ${milhoes} milhões de toneladas de cana, com produtividade de ${produtividade} t/ha.`;
}
