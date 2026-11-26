import { createLink } from "@tanstack/react-router";
import { cva, type VariantProps } from "class-variance-authority";
import type { ComponentProps } from "react";

const linkTexto = cva("text-marca underline", {
  variants: {
    tamanho: {
      base: "",
      pequeno: "text-sm",
    },
  },
  defaultVariants: { tamanho: "base" },
});

export type AncoraProps = Omit<ComponentProps<"a">, "className" | "style"> &
  VariantProps<typeof linkTexto>;

function Ancora({ tamanho, children, ...props }: AncoraProps) {
  return (
    <a {...props} className={linkTexto({ tamanho })}>
      {children}
    </a>
  );
}

export const LinkTexto = createLink(Ancora);
