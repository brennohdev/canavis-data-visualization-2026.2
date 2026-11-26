import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

const css = readFileSync(path.resolve(import.meta.dirname, "../styles/tokens.css"), "utf8");

const cores = new Map<string, string>(
  [...css.matchAll(/--color-([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})/g)].map((m) => [m[1], m[2]]),
);

function cor(nome: string): string {
  const valor = cores.get(nome);
  if (!valor) throw new Error(`Token --color-${nome} não encontrado em tokens.css`);
  return valor;
}

function luminancia(hex: string): number {
  const [r, g, b] = [1, 3, 5]
    .map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
    .map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function razao(a: string, b: string): number {
  const [claro, escuro] = [luminancia(cor(a)), luminancia(cor(b))].sort((x, y) => y - x);
  return (claro + 0.05) / (escuro + 0.05);
}

const textos: [string, string, number][] = [
  ["texto", "fundo", 15.55],
  ["texto-secundario", "fundo", 6.62],
  ["marca", "fundo", 5.7],
  ["abaixo-texto", "fundo", 6.08],
  ["acucar-texto", "fundo", 6.91],
  ["neutro-dado-texto", "fundo", 5.62],
  ["superficie", "marca", 6.38],
  ["superficie", "acucar-texto", 7.74],
  ["texto", "abaixo", 4.61],
];

const formas: [string, number][] = [
  ["marca", 5.7],
  ["abaixo", 3.37],
  ["serie-2", 3.26],
  ["acucar", 4.74],
  ["etanol", 4.17],
  ["neutro-dado", 4.08],
  ["eixo", 3.3],
  ["foco", 5.99],
  ["contorno-area", 6.62],
  ["rampa-6", 8.71],
];

describe("contraste dos tokens (WCAG 2.1 AA)", () => {
  it.each(textos)("texto %s sobre %s tem pelo menos 4,5:1", (primeiro, segundo, esperado) => {
    const medido = razao(primeiro, segundo);
    expect(medido).toBeGreaterThanOrEqual(4.5);
    expect(medido).toBeCloseTo(esperado, 1);
  });

  it.each(formas)("forma %s sobre fundo tem pelo menos 3:1", (nome, esperado) => {
    const medido = razao(nome, "fundo");
    expect(medido).toBeGreaterThanOrEqual(3);
    expect(medido).toBeCloseTo(esperado, 1);
  });
});
