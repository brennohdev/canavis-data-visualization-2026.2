const inteiro = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });
const umaCasa = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

export const ausente = "dado ausente";

export function formatarInteiro(valor: number | null): string {
  return valor === null ? ausente : inteiro.format(valor);
}

export function formatarUmaCasa(valor: number | null): string {
  return valor === null ? ausente : umaCasa.format(valor);
}

export function formatarToneladasPorHa(valor: number | null): string {
  return valor === null ? ausente : `${umaCasa.format(valor)} t/ha`;
}
