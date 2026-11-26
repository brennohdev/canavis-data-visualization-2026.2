import { Card } from "@/components/ui/card";
import { Texto } from "@/components/ui/texto";

export interface KpiProps {
  rotulo: string;
  valor: string;
  detalhe?: { rotulo: string; valor: string };
}

export function Kpi({ rotulo, valor, detalhe }: KpiProps) {
  return (
    <Card>
      <Texto tom="secundario" tamanho="pequeno">
        {rotulo}
      </Texto>
      <p data-kpi className="text-(length:--text-xl) font-semibold">
        {valor}
      </p>
      {detalhe && (
        <Texto tom="secundario" tamanho="pequeno">
          {detalhe.rotulo}: <span className="num">{detalhe.valor}</span>
        </Texto>
      )}
    </Card>
  );
}
