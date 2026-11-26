import { cva, type VariantProps } from "class-variance-authority";
import type { ComponentProps } from "react";

const texto = cva("", {
  variants: {
    tom: {
      padrao: "",
      secundario: "text-texto-secundario",
      erro: "text-abaixo-texto",
    },
    tamanho: {
      base: "",
      pequeno: "text-sm",
    },
  },
  defaultVariants: { tom: "padrao", tamanho: "base" },
});

export type TextoProps = Omit<ComponentProps<"p">, "className" | "style"> &
  VariantProps<typeof texto>;

export function Texto({ tom, tamanho, ...props }: TextoProps) {
  return <p className={texto({ tom, tamanho })} {...props} />;
}
