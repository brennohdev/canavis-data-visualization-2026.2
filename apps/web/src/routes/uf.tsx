import { useQuery } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { Card } from "@/components/ui/card";
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
    <main className="mx-auto max-w-3xl space-y-6 p-6">
      <Link to="/" className="text-sm text-marca underline">
        Início
      </Link>
      <h1 className="text-(length:--text-xl) font-semibold">
        Produção de cana: {sigla} em {ano}
      </h1>

      {consulta.isPending && <p role="status">Carregando…</p>}

      {consulta.isError && (
        <p role="alert" className="text-abaixo-texto">
          {consulta.error instanceof ErroApi
            ? consulta.error.message
            : "Não foi possível carregar os dados."}
        </p>
      )}

      {consulta.isSuccess && (
        <>
          <Card className="space-y-2">
            <p className="text-sm text-texto-secundario">Produtividade</p>
            <p data-kpi className="text-(length:--text-xl) font-semibold">
              {formatarToneladasPorHa(consulta.data.produtividade_t_ha)}
            </p>
            <p className="text-sm text-texto-secundario">
              Quantidade produzida:{" "}
              <span className="num">{formatarInteiro(consulta.data.quantidade_produzida_t)} t</span>
            </p>
          </Card>
          <p className="leitura">{textoProducao(consulta.data)}</p>
        </>
      )}

      <Legenda />
    </main>
  );
}

// Tela de exemplo dos tokens: cor sempre acompanhada de hachura e rótulo.
export function Legenda() {
  return (
    <Card>
      <h2 className="mb-3 text-sm font-semibold text-texto-secundario">Legenda de exemplo</h2>
      <ul className="flex flex-wrap gap-6 text-sm">
        <li className="flex items-center gap-2">
          <span className="hachura-etanol inline-block size-5 rounded-sm" aria-hidden="true" />
          Etanol
        </li>
        <li className="flex items-center gap-2">
          <span className="hachura-ausente inline-block size-5 rounded-sm" aria-hidden="true" />
          Dado ausente
        </li>
        <li className="flex items-center gap-2">
          <span className="inline-block size-5 rounded-sm bg-marca" aria-hidden="true" />
          Paraíba
        </li>
      </ul>
    </Card>
  );
}
