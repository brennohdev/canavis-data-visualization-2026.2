import { describe, expect, it } from "vitest";
import type { ProducaoUF } from "./api";
import { buscaUfSchema } from "./busca";
import { formatarInteiro, formatarToneladasPorHa } from "./formato";
import { textoProducao } from "./texto";

const pb2021: ProducaoUF = {
  sigla: "PB",
  territorio_id: "uf:25",
  nome: "Paraíba",
  ano: 2021,
  produtividade_t_ha: 55.653875,
  quantidade_produzida_t: 5630113,
  area_colhida_ha: 101163,
};

describe("formato pt-BR", () => {
  it("usa vírgula decimal e ponto de milhar", () => {
    expect(formatarToneladasPorHa(55.653875)).toBe("55,7 t/ha");
    expect(formatarInteiro(5630113)).toBe("5.630.113");
  });

  it("nunca transforma ausente em zero", () => {
    expect(formatarInteiro(null)).toBe("dado ausente");
    expect(formatarToneladasPorHa(null)).toBe("dado ausente");
  });
});

describe("textoProducao", () => {
  it("descreve a produção sem verbos de causa", () => {
    expect(textoProducao(pb2021)).toBe(
      "Em 2021, Paraíba produziu 5,6 milhões de toneladas de cana, com produtividade de 55,7 t/ha.",
    );
  });

  it("avisa quando o valor está ausente", () => {
    const texto = textoProducao({ ...pb2021, produtividade_t_ha: null });
    expect(texto).toContain("não há dado");
  });
});

describe("buscaUfSchema (ano na URL)", () => {
  it("aceita ano válido", () => {
    expect(buscaUfSchema.parse({ ano: "2015" })).toEqual({ ano: 2015 });
    expect(buscaUfSchema.parse({ ano: 2003 })).toEqual({ ano: 2003 });
  });

  it("cai no padrão 2021 quando ausente ou inválido", () => {
    expect(buscaUfSchema.parse({})).toEqual({ ano: 2021 });
    expect(buscaUfSchema.parse({ ano: "abc" })).toEqual({ ano: 2021 });
    expect(buscaUfSchema.parse({ ano: 1999 })).toEqual({ ano: 2021 });
    expect(buscaUfSchema.parse({ ano: 2024 })).toEqual({ ano: 2021 });
  });
});
