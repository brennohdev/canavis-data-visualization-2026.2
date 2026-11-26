import {
  createRootRoute,
  createRoute,
  createRouter,
  Outlet,
  type RouterHistory,
} from "@tanstack/react-router";
import { buscaUfSchema } from "@/lib/busca";
import { TelaInicio } from "@/routes/index";
import { TelaUF } from "@/routes/uf";

const raiz = createRootRoute({ component: Outlet });

const inicio = createRoute({ getParentRoute: () => raiz, path: "/", component: TelaInicio });

const uf = createRoute({
  getParentRoute: () => raiz,
  path: "/uf/$sigla",
  validateSearch: (busca: Record<string, unknown>) => buscaUfSchema.parse(busca),
  component: function RotaUF() {
    const { sigla } = uf.useParams();
    const { ano } = uf.useSearch();
    return <TelaUF sigla={sigla.toUpperCase()} ano={ano} />;
  },
});

const arvoreDeRotas = raiz.addChildren([inicio, uf]);

export function criarRouter(history?: RouterHistory) {
  return createRouter({ routeTree: arvoreDeRotas, history });
}

declare module "@tanstack/react-router" {
  interface Register {
    router: ReturnType<typeof criarRouter>;
  }
}
