from __future__ import annotations

import argparse
import sys
from pathlib import Path

from canavis.logging import get_logger
from canavis.sources.intl import job

_log = get_logger(__name__)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="canavis-intl", description="Ingestão dos dados internacionais do CanaVis."
    )
    sub = parser.add_subparsers(dest="comando", required=True)
    refresh = sub.add_parser("refresh", help="Baixa as fontes e regrava os snapshots.")
    reprocess = sub.add_parser("reprocess", help="Reconstrói os snapshots a partir do bruto salvo.")
    for p in (refresh, reprocess):
        p.add_argument("--fonte", action="append", help="Limita a uma fonte (repetível).")
        p.add_argument("--saida", type=Path, default=None, help="Pasta dos snapshots.")
    refresh.add_argument("--tentativas", type=int, default=2, help="Tentativas por fonte.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.comando == "refresh":
        manifesto = job.refresh(fontes=args.fonte, saida=args.saida, tentativas=args.tentativas)
        for fonte_id, entrada in sorted(manifesto["fontes"].items()):
            print(
                f"{fonte_id:10s} status={entrada['status']:6s} linhas={entrada['linhas']:>7} "
                f"sha256={entrada['sha256']} erro={entrada['erro']}"
            )
        selecionadas = args.fonte or list(manifesto["fontes"])
        ok = [f for f in selecionadas if manifesto["fontes"].get(f, {}).get("status") == "ok"]
        return 0 if ok else 1
    comparacao = job.reprocess(fontes=args.fonte, saida=args.saida)
    for fonte_id, item in sorted(comparacao.items()):
        rotulo = "igual" if item["igual"] else "DIFERENTE"
        print(f"{fonte_id:10s} {rotulo:9s} anterior={item['anterior']} novo={item['novo']}")
    return 0 if any(item["novo"] for item in comparacao.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
