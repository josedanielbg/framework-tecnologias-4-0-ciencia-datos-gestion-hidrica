"""Construye datasets mensuales limpios para entrenamiento."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from proyecto_grado_v6.model_dataset import build_model_dataset  # noqa: E402


if __name__ == "__main__":
    result = build_model_dataset(
        raw_dir=PROJECT_ROOT / "data" / "raw",
        output_dir=PROJECT_ROOT / "data" / "processed",
    )
    print(json.dumps(result, indent=2, ensure_ascii=True))
