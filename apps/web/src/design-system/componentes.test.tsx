import { RouterProvider, createMemoryHistory, createRootRoute, createRouter } from "@tanstack/react-router";
import { cleanup, render, screen } from "@testing-library/react";
import type { ComponentProps } from "react";
import { afterEach, describe, expect, expectTypeOf, it } from "vitest";
import { Carregando, ErroCarga } from "@/components/dados/estado-consulta";
import { Kpi } from "@/components/dados/kpi";
import { ItemLegenda, Legenda } from "@/components/dados/legenda";
import { PainelLeitura } from "@/components/dados/painel-leitura";
import { Card } from "@/components/ui/card";
import { LinkTexto } from "@/components/ui/link-texto";
import { Pagina } from "@/components/ui/pagina";
import { Texto } from "@/components/ui/texto";
import { Titulo } from "@/components/ui/titulo";

afterEach(cleanup);

describe("Titulo", () => {
  it("nível 1 é h1 em 28 px", () => {
    render(<Titulo nivel={1}>Título</Titulo>);
    const titulo = screen.getByRole("heading", { level: 1 });
    expect(titulo).toHaveClass("text-(length:--text-xl)", "font-semibold");
  });

  it("nível 2 é h2 secundário", () => {
    render(<Titulo nivel={2}>Subtítulo</Titulo>);
    const titulo = screen.getByRole("heading", { level: 2 });
    expect(titulo).toHaveClass("text-sm", "text-texto-secundario", "font-semibold");
  });
});

describe("Texto", () => {
  it.each([
    ["padrao", "base", []],
    ["secundario", "pequeno", ["text-texto-secundario", "text-sm"]],
    ["erro", "base", ["text-abaixo-texto"]],
  ] as const)("tom %s e tamanho %s", (tom, tamanho, classes) => {
    render(
      <Texto tom={tom} tamanho={tamanho}>
        conteúdo
      </Texto>,
    );
    const texto = screen.getByText("conteúdo");
    for (const classe of classes) expect(texto).toHaveClass(classe);
  });
});

describe("LinkTexto", () => {
  function renderizar(tamanho: "base" | "pequeno") {
    const raiz = createRootRoute({
      component: () => (
        <LinkTexto to="/" tamanho={tamanho}>
          voltar
        </LinkTexto>
      ),
    });
    const router = createRouter({
      routeTree: raiz,
      history: createMemoryHistory({ initialEntries: ["/"] }),
    });
    render(<RouterProvider router={router} />);
  }

  it("tamanho base usa a cor da marca com sublinhado", async () => {
    renderizar("base");
    const link = await screen.findByRole("link", { name: "voltar" });
    expect(link).toHaveClass("text-marca", "underline");
    expect(link).not.toHaveClass("text-sm");
  });

  it("tamanho pequeno acrescenta text-sm", async () => {
    renderizar("pequeno");
    expect(await screen.findByRole("link", { name: "voltar" })).toHaveClass("text-sm");
  });
});

describe("ItemLegenda e Legenda", () => {
  it.each([
    ["etanol", "hachura-etanol"],
    ["ausente", "hachura-ausente"],
    ["marca", "bg-marca"],
  ] as const)("padrão %s usa %s e esconde a amostra", (padrao, classe) => {
    const { container } = render(
      <ul>
        <ItemLegenda padrao={padrao}>Rótulo</ItemLegenda>
      </ul>,
    );
    const amostra = container.querySelector("span");
    expect(amostra).toHaveClass(classe);
    expect(amostra).toHaveAttribute("aria-hidden", "true");
    expect(screen.getByText("Rótulo")).toBeInTheDocument();
  });

  it("Legenda mostra o título e a lista", () => {
    render(
      <Legenda titulo="Legenda de teste">
        <ItemLegenda padrao="marca">Paraíba</ItemLegenda>
      </Legenda>,
    );
    expect(screen.getByRole("heading", { level: 2, name: "Legenda de teste" })).toBeInTheDocument();
    expect(screen.getByRole("list")).toBeInTheDocument();
  });
});

describe("Kpi", () => {
  it("marca o valor com data-kpi e o detalhe com .num", () => {
    const { container } = render(
      <Kpi
        rotulo="Produtividade"
        valor="55,7 t/ha"
        detalhe={{ rotulo: "Quantidade produzida", valor: "5.630.113 t" }}
      />,
    );
    expect(container.querySelector("[data-kpi]")).toHaveTextContent("55,7 t/ha");
    expect(container.querySelector(".num")).toHaveTextContent("5.630.113 t");
    expect(screen.getByText("Produtividade")).toHaveClass("text-texto-secundario");
  });

  it("dispensa o detalhe", () => {
    const { container } = render(<Kpi rotulo="Área" valor="1" />);
    expect(container.querySelector(".num")).toBeNull();
  });
});

describe("PainelLeitura, Card e Pagina", () => {
  it("PainelLeitura usa a classe leitura", () => {
    render(<PainelLeitura>texto</PainelLeitura>);
    expect(screen.getByText("texto")).toHaveClass("leitura");
  });

  it("Card usa superfície, raio e sombra dos tokens", () => {
    render(<Card data-testid="card">x</Card>);
    expect(screen.getByTestId("card")).toHaveClass(
      "bg-superficie",
      "rounded-(--radius-card)",
      "shadow-(--shadow-card)",
    );
  });

  it("Pagina é o landmark main", () => {
    render(<Pagina>x</Pagina>);
    expect(screen.getByRole("main")).toHaveClass("max-w-3xl");
  });

  it("Card não aceita className nem style", () => {
    expectTypeOf<ComponentProps<typeof Card>>().not.toHaveProperty("className");
    expectTypeOf<ComponentProps<typeof Card>>().not.toHaveProperty("style");
  });
});

describe("estados de consulta", () => {
  it("Carregando anuncia status ocupado", () => {
    render(<Carregando />);
    const estado = screen.getByRole("status");
    expect(estado).toHaveAttribute("aria-busy", "true");
    expect(estado).toHaveTextContent("Carregando dados…");
  });

  it("ErroCarga usa a mensagem recebida em tom de erro", () => {
    render(<ErroCarga mensagem="Dados indisponíveis." />);
    const alerta = screen.getByRole("alert");
    expect(alerta).toHaveTextContent("Dados indisponíveis.");
    expect(alerta).toHaveClass("text-abaixo-texto");
  });

  it("ErroCarga cai na microcopy padrão sem mensagem", () => {
    render(<ErroCarga />);
    expect(screen.getByRole("alert")).toHaveTextContent("Não foi possível carregar estes dados.");
  });
});
