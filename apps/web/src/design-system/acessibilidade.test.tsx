import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider, createMemoryHistory } from "@tanstack/react-router";
import { cleanup, render, screen } from "@testing-library/react";
import axe from "axe-core";
import { afterEach, describe, expect, it, vi } from "vitest";
import { criarRouter } from "@/router";

function renderizar(url: string) {
  const router = criarRouter(createMemoryHistory({ initialEntries: [url] }));
  return render(
    <QueryClientProvider client={new QueryClient()}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  );
}

async function violacoes(container: HTMLElement) {
  const resultado = await axe.run(container, {
    rules: { "color-contrast": { enabled: false } },
  });
  return resultado.violations.map((v) => `${v.id}: ${v.help}`);
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("acessibilidade com axe-core", () => {
  it("/ não tem violações", async () => {
    const { container } = renderizar("/");
    await screen.findByRole("heading", { level: 1, name: "CanaVis" });
    expect(await violacoes(container)).toEqual([]);
  });

  it("/uf/PB?ano=2021 não tem violações", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            sigla: "PB",
            territorio_id: "uf:25",
            nome: "Paraíba",
            ano: 2021,
            produtividade_t_ha: 55.653875,
            quantidade_produzida_t: 5630113,
            area_colhida_ha: 101163,
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );
    const { container } = renderizar("/uf/PB?ano=2021");
    await screen.findByText("55,7 t/ha");
    expect(await violacoes(container)).toEqual([]);
  });
});
