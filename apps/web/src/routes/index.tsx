import { Link } from "@tanstack/react-router";

export function TelaInicio() {
  return (
    <main className="mx-auto max-w-3xl space-y-4 p-6">
      <h1 className="text-(length:--text-xl) font-semibold">CanaVis</h1>
      <p className="leitura">
        Benchmarking regional da produção de cana-de-açúcar na Paraíba. Esta é a fatia vertical
        mínima da Etapa 3.
      </p>
      <Link
        to="/uf/$sigla"
        params={{ sigla: "PB" }}
        search={{ ano: 2021 }}
        className="text-marca underline"
      >
        Ver a Paraíba em 2021
      </Link>
    </main>
  );
}
