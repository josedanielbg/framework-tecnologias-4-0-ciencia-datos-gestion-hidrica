"""Funciones de entrada/salida para fuentes remotas y archivos locales."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def ensure_dir(path: str | Path) -> Path:
    """Crea un directorio si no existe y retorna su ruta como Path."""

    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def read_excel_source(source: str | Path, **kwargs: Any) -> pd.DataFrame:
    """Lee un Excel local o remoto manteniendo una sola puerta de entrada."""

    return pd.read_excel(source, **kwargs)


def read_csv_source(source: str | Path, **kwargs: Any) -> pd.DataFrame:
    """Lee un CSV local o remoto manteniendo una sola puerta de entrada."""

    return pd.read_csv(source, **kwargs)


def fetch_json(url: str, params: dict[str, Any] | None = None, timeout: int = 30) -> Any:
    """Descarga JSON con validacion explicita de errores HTTP."""

    import requests

    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def write_excel(df: pd.DataFrame, output_path: str | Path, index: bool = False) -> Path:
    """Escribe un DataFrame en Excel y crea la carpeta destino si hace falta."""

    path = Path(output_path)
    ensure_dir(path.parent)
    df.to_excel(path, index=index)
    return path
