import { cva, type VariantProps } from "class-variance-authority";
import type { ReactNode } from "react";
import { Card } from "@/components/ui/card";
import { Titulo } from "@/components/ui/titulo";

const amostra = cva("inline-block size-5 rounded-sm", {
  variants: {
    padrao: {
      etanol: "hachura-etanol",
      ausente: "hachura-ausente",
      marca: "bg-marca",
    },
  },
});

export interface ItemLegendaProps extends Required<VariantProps<typeof amostra>> {
  children: ReactNode;
}

export function ItemLegenda({ padrao, children }: ItemLegendaProps) {
  return (
    <li className="flex items-center gap-2">
      <span className={amostra({ padrao })} aria-hidden="true" />
      {children}
    </li>
  );
}

export interface LegendaProps {
  titulo: string;
  children: ReactNode;
}

export function Legenda({ titulo, children }: LegendaProps) {
  return (
    <Card>
      <Titulo nivel={2}>{titulo}</Titulo>
      <ul className="flex flex-wrap gap-6 text-sm">{children}</ul>
    </Card>
  );
}
