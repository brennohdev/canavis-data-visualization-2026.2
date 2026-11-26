import { Texto } from "@/components/ui/texto";

export function Carregando() {
  return (
    <Texto role="status" aria-busy="true">
      Carregando dados…
    </Texto>
  );
}

export function ErroCarga({ mensagem }: { mensagem?: string }) {
  return (
    <Texto role="alert" tom="erro">
      {mensagem ?? "Não foi possível carregar estes dados."}
    </Texto>
  );
}
