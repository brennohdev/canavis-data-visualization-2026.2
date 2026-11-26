import { useQuery } from "@tanstack/react-query";
import { Carregando, ErroCarga } from "@/components/dados/estado-consulta";
import { Kpi } from "@/components/dados/kpi";
import { ItemLegenda, Legenda } from "@/components/dados/legenda";
import { PainelLeitura } from "@/components/dados/painel-leitura";
import { LinkTexto } from "@/components/ui/link-texto";
import { Pagina } from "@/components/ui/pagina";
import { Titulo } from "@/components/ui/titulo";
import { buscarProducaoUF, ErroApi } from "@/lib/api";
import { formatarInteiro, formatarToneladasPorHa } from "@/lib/formato";
import { textoProducao } from "@/lib/texto";

export function TelaUF({ sigla, ano }: { sigla: string; ano: number }) {
  const consulta = useQuery({
    queryKey: ["producao-uf", sigla, ano],
    queryFn: () => buscarProducaoUF(sigla, ano),
    retry: false,
  });

  return (
    <Pagina>
      <LinkTexto to="/" tamanho="pequeno">
        Início
      </LinkTexto>
      <Titulo nivel={1}>
        Produção de cana: {sigla} em {ano}
      </Titulo>
      {consulta.isPending && <Carregando />}
      {consulta.isError && (
        <ErroCarga
          mensagem={consulta.error instanceof ErroApi ? consulta.error.message : undefined}
        />
      )}
      {consulta.isSuccess && (
        <>
          <Kpi
            rotulo="Produtividade"
            valor={formatarToneladasPorHa(consulta.data.produtividade_t_ha)}
            detalhe={{
              rotulo: "Quantidade produzida",
              valor: `${formatarInteiro(consulta.data.quantidade_produzida_t)} t`,
            }}
          />
          <PainelLeitura>{textoProducao(consulta.data)}</PainelLeitura>
        </>
      )}
      <Legenda titulo="Legenda de exemplo">
        <ItemLegenda padrao="etanol">Etanol</ItemLegenda>
        <ItemLegenda padrao="ausente">Dado ausente</ItemLegenda>
        <ItemLegenda padrao="marca">Paraíba</ItemLegenda>
      </Legenda>
    </Pagina>
  );
}
