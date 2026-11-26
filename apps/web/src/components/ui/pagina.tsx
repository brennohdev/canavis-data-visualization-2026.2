import type { ComponentProps } from "react";

export type PaginaProps = Omit<ComponentProps<"main">, "className" | "style">;

export function Pagina(props: PaginaProps) {
  return <main className="mx-auto max-w-3xl space-y-6 p-6" {...props} />;
}
