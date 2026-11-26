import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import ts from "typescript";
import { describe, expect, it } from "vitest";

const raiz = path.resolve(import.meta.dirname, "..");

function listarArquivos(pasta: string): string[] {
  return readdirSync(pasta, { withFileTypes: true }).flatMap((entrada) => {
    const caminho = path.join(pasta, entrada.name);
    if (entrada.isDirectory()) return listarArquivos(caminho);
    return /\.(ts|tsx)$/.test(entrada.name) ? [caminho] : [];
  });
}

function acharComentarios(arquivo: string): string[] {
  const texto = readFileSync(arquivo, "utf8");
  const scanner = ts.createScanner(
    ts.ScriptTarget.ES2022,
    false,
    arquivo.endsWith(".tsx") ? ts.LanguageVariant.JSX : ts.LanguageVariant.Standard,
    texto,
  );
  const achados: string[] = [];
  let token = scanner.scan();
  while (token !== ts.SyntaxKind.EndOfFileToken) {
    if (
      token === ts.SyntaxKind.SingleLineCommentTrivia ||
      token === ts.SyntaxKind.MultiLineCommentTrivia
    ) {
      const linha = texto.slice(0, scanner.getTokenStart()).split("\n").length;
      achados.push(`${path.relative(raiz, arquivo)}:${linha}`);
    }
    token = scanner.scan();
  }
  return achados;
}

describe("código-fonte sem comentários", () => {
  it("não há comentário em nenhum .ts ou .tsx de src", () => {
    const achados = listarArquivos(raiz).flatMap(acharComentarios);
    expect(achados).toEqual([]);
  });
});
