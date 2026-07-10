"""Ejecuta el pipeline sin instalar el paquete en modo editable."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from proyecto_grado_v6.pipeline import run_pipeline  # noqa: E402


if __name__ == "__main__":
    artifacts = run_pipeline(PROJECT_ROOT / "data" / "processed")
    print(json.dumps(artifacts, indent=2, ensure_ascii=True))
