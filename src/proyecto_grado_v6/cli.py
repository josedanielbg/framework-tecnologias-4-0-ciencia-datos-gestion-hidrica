"""Interfaz de linea de comandos del proyecto."""

from __future__ import annotations

import argparse
import json

from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ejecuta el pipeline del proyecto V6.")
    parser.add_argument(
        "--output-dir",
        default="data/processed",
        help="Carpeta donde se escriben los artefactos generados.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    artifacts = run_pipeline(args.output_dir)
    print(json.dumps(artifacts, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
