import type { ComponentProps } from "react";

export type PainelLeituraProps = Omit<ComponentProps<"p">, "className" | "style">;

export function PainelLeitura(props: PainelLeituraProps) {
  return <p className="leitura" {...props} />;
}
