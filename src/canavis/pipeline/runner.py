from __future__ import annotations

from canavis.logging import get_logger
from canavis.pipeline.build import build_all
from canavis.pipeline.extract import extract_all
from canavis.pipeline.transform import transform_all

_log = get_logger(__name__)

_STAGES = {
    "extract": extract_all,
    "transform": transform_all,
    "build": build_all,
}


def run(stages: list[str] | None = None) -> None:
    selected = stages or list(_STAGES)
    for stage in selected:
        if stage not in _STAGES:
            raise KeyError(f"Estágio '{stage}' desconhecido. Opções: {list(_STAGES)}")
        _log.info("=== estágio: %s ===", stage)
        _STAGES[stage]()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Pipeline de dados do projeto canavis.")
    parser.add_argument(
        "--stage",
        action="append",
        choices=list(_STAGES),
        help="Executa apenas os estágios indicados (padrão: todos, em ordem).",
    )
    args = parser.parse_args()
    run(args.stage)


if __name__ == "__main__":
    main()
