import { PainelLeitura } from "@/components/dados/painel-leitura";
import { Pagina } from "@/components/ui/pagina";
import { LinkTexto } from "@/components/ui/link-texto";
import { Titulo } from "@/components/ui/titulo";

export function TelaInicio() {
  return (
    <Pagina>
      <Titulo nivel={1}>CanaVis</Titulo>
      <PainelLeitura>
        Benchmarking regional da produção de cana-de-açúcar na Paraíba. Esta é a fatia vertical
        mínima da Etapa 3.
      </PainelLeitura>
      <LinkTexto to="/uf/$sigla" params={{ sigla: "PB" }} search={{ ano: 2021 }}>
        Ver a Paraíba em 2021
      </LinkTexto>
    </Pagina>
  );
}
