import type { ComponentProps } from "react";

export type CardProps = Omit<ComponentProps<"div">, "className" | "style">;

export function Card(props: CardProps) {
  return (
    <div
      className="space-y-2 rounded-(--radius-card) bg-superficie p-6 shadow-(--shadow-card)"
      {...props}
    />
  );
}
