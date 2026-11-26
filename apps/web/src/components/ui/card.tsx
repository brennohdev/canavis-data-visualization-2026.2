import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";

// Componente no padrão shadcn/ui, com as cores vindas de tokens.css.
export function Card({ className, ...props }: ComponentProps<"div">) {
  return (
    <div
      className={cn("rounded-(--radius-card) bg-superficie p-6 shadow-(--shadow-card)", className)}
      {...props}
    />
  );
}
