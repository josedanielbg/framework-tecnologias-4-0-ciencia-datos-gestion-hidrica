"""Descarga los datos base del repositorio fuente a data/raw."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from proyecto_grado_v6.raw_data import download_raw_data  # noqa: E402


if __name__ == "__main__":
    files = download_raw_data(PROJECT_ROOT / "data" / "raw")
    print(json.dumps(files, indent=2, ensure_ascii=True))
