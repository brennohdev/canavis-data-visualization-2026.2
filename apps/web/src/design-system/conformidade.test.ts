import path from "node:path";
import { ESLint } from "eslint";
import { describe, expect, it } from "vitest";

const raiz = path.resolve(import.meta.dirname, "../..");
const eslint = new ESLint({
  cwd: raiz,
  overrideConfigFile: path.join(raiz, "eslint.config.js"),
});

async function mensagens(codigo: string, arquivo: string) {
  const [resultado] = await eslint.lintText(codigo, { filePath: path.join(raiz, arquivo) });
  return resultado.messages.map((m) => `${m.ruleId}: ${m.message}`);
}

const rota = "src/routes/x.tsx";
const componente = "src/components/ui/x.tsx";

describe("regras de padronização em rotas", () => {
  it("rejeita className", async () => {
    const achados = await mensagens('export const A = () => <p className="x">a</p>;', rota);
    expect(achados.join("\n")).toContain("Rotas não recebem className");
  });

  it("rejeita style", async () => {
    const achados = await mensagens("export const A = () => <p style={{}}>a</p>;", rota);
    expect(achados.join("\n")).toContain("Rotas não recebem style");
  });

  it.each(["clsx", "class-variance-authority", "tailwind-merge", "@/lib/utils"])(
    "rejeita o import de %s",
    async (origem) => {
      const achados = await mensagens(`import * as m from "${origem}";\nexport { m };`, rota);
      expect(achados.join("\n")).toContain("Montar classes só é permitido em src/components");
    },
  );

  it("rejeita cor da paleta padrão do Tailwind", async () => {
    for (const classe of ["bg-red-500", "text-gray-700", "bg-white"]) {
      const achados = await mensagens(`export const c = "${classe}";`, rota);
      expect(achados.join("\n")).toContain("Cor da paleta padrão do Tailwind");
    }
  });

  it("rejeita hex literal", async () => {
    const achados = await mensagens('export const c = "#2f6b3c";', rota);
    expect(achados.join("\n")).toContain("Cor hexadecimal literal");
  });

  it("rejeita token só de forma usado como texto", async () => {
    for (const classe of ["text-serie-2", "text-abaixo", "text-neutro-dado"]) {
      const achados = await mensagens(`export const c = "${classe}";`, rota);
      expect(achados.join("\n")).toContain("só de forma");
    }
  });

  it("aceita o token de texto e um componente com variante", async () => {
    expect(await mensagens('export const c = "text-abaixo-texto";', rota)).toEqual([]);
    expect(
      await mensagens('export const A = () => <Texto tom="erro">a</Texto>;', rota),
    ).toEqual([]);
  });
});

describe("regras de padronização em componentes", () => {
  it("aceita className", async () => {
    expect(
      await mensagens('export const A = () => <p className="text-abaixo-texto">a</p>;', componente),
    ).toEqual([]);
  });

  it("continua rejeitando cor fora dos tokens", async () => {
    const achados = await mensagens('export const c = "bg-red-500";', componente);
    expect(achados.join("\n")).toContain("Cor da paleta padrão do Tailwind");
  });
});
