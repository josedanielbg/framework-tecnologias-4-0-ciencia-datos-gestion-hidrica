"""Descarga de datos fuente a la carpeta data/raw."""

from __future__ import annotations

from pathlib import Path
import json
from urllib.parse import quote
from urllib.parse import unquote
from urllib.request import urlopen

from .config import SOURCE_CONTENTS_API
from .io import ensure_dir


def raw_filename(file_name: str) -> str:
    """Convierte nombres URL-encoded a nombres legibles en disco."""

    return unquote(file_name)


def safe_url(url: str) -> str:
    """Codifica caracteres no ASCII conservando los separadores de URL."""

    return quote(url, safe=":/?&=%")


def download_file(url: str, output_path: str | Path, timeout: int = 60) -> Path:
    """Descarga un archivo remoto manteniendo validacion HTTP."""

    path = Path(output_path)
    ensure_dir(path.parent)
    with urlopen(safe_url(url), timeout=timeout) as response:
        path.write_bytes(response.read())
    return path


def fetch_source_manifest(api_url: str = SOURCE_CONTENTS_API) -> list[dict[str, str]]:
    """Consulta GitHub Contents API para listar los archivos fuente reales."""

    with urlopen(api_url, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return [
        {
            "name": item["name"],
            "download_url": item["download_url"],
        }
        for item in payload
        if item.get("type") == "file" and item.get("download_url")
    ]


def download_raw_data(output_dir: str | Path = "data/raw") -> dict[str, str]:
    """Descarga todos los archivos fuente del directorio remoto proyectoGradoV3."""

    output = ensure_dir(output_dir)
    downloaded: dict[str, str] = {}
    for item in fetch_source_manifest():
        file_name = raw_filename(item["name"])
        target = output / file_name
        downloaded[file_name] = str(download_file(item["download_url"], target))
    return downloaded
