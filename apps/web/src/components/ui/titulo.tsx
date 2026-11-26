import { cva, type VariantProps } from "class-variance-authority";
import type { ComponentProps } from "react";

const titulo = cva("font-semibold", {
  variants: {
    nivel: {
      1: "text-(length:--text-xl)",
      2: "text-sm text-texto-secundario",
    },
  },
  defaultVariants: { nivel: 1 },
});

export type TituloProps = Omit<ComponentProps<"h1">, "className" | "style"> &
  Required<VariantProps<typeof titulo>>;

export function Titulo({ nivel, children, ...props }: TituloProps) {
  const Elemento = nivel === 1 ? "h1" : "h2";
  return (
    <Elemento className={titulo({ nivel })} {...props}>
      {children}
    </Elemento>
  );
}
