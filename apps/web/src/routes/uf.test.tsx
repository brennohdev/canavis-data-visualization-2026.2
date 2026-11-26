import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "@tanstack/react-router";
import { cleanup, render, screen } from "@testing-library/react";
import { createMemoryHistory } from "@tanstack/react-router";
import { afterEach, describe, expect, it, vi } from "vitest";
import { criarRouter } from "@/router";

function renderizar(url: string) {
  const router = criarRouter(createMemoryHistory({ initialEntries: [url] }));
  const client = new QueryClient();
  return render(
    <QueryClientProvider client={client}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  );
}

function responder(status: number, corpo: unknown) {
  return vi.fn().mockResolvedValue(
    new Response(JSON.stringify(corpo), {
      status,
      headers: { "Content-Type": "application/json" },
    }),
  );
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("rota /uf/PB?ano=2021", () => {
  it("mostra o KPI e o texto dinâmico vindos da API", async () => {
    const fetchMock = responder(200, {
      sigla: "PB",
      territorio_id: "uf:25",
      nome: "Paraíba",
      ano: 2021,
      produtividade_t_ha: 55.653875,
      quantidade_produzida_t: 5630113,
      area_colhida_ha: 101163,
    });
    vi.stubGlobal("fetch", fetchMock);

    const { container } = renderizar("/uf/PB?ano=2021");

    expect(await screen.findByText("55,7 t/ha")).toBeInTheDocument();
    expect(container.querySelector("[data-kpi]")).toHaveTextContent("55,7 t/ha");
    expect(screen.getByText(/produziu 5,6 milhões de toneladas/)).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith("/api/v1/uf/PB/producao?ano=2021");
  });

  it("mostra a mensagem em português quando a API responde 503", async () => {
    vi.stubGlobal("fetch", responder(503, { detail: "Dados indisponíveis no momento." }));
    renderizar("/uf/PB?ano=2021");
    expect(await screen.findByRole("alert")).toHaveTextContent("Dados indisponíveis no momento.");
  });

  it("usa o ano padrão quando o ano da URL é inválido", async () => {
    const fetchMock = responder(404, { detail: "Sem dados." });
    vi.stubGlobal("fetch", fetchMock);
    renderizar("/uf/PB?ano=abc");
    await screen.findByRole("alert");
    expect(fetchMock).toHaveBeenCalledWith("/api/v1/uf/PB/producao?ano=2021");
  });

  it("exibe a legenda de exemplo com as hachuras dos tokens", async () => {
    vi.stubGlobal("fetch", responder(503, { detail: "x" }));
    const { container } = renderizar("/uf/PB?ano=2021");
    await screen.findByRole("alert");
    expect(container.querySelector(".hachura-etanol")).not.toBeNull();
    expect(container.querySelector(".hachura-ausente")).not.toBeNull();
    expect(screen.getByText("Etanol")).toBeInTheDocument();
    expect(screen.getByText("Dado ausente")).toBeInTheDocument();
  });
});
