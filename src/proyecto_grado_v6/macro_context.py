"""Variables macroclimaticas y de reservas hidraulicas."""

from __future__ import annotations

from io import StringIO

import pandas as pd

from .config import DATA_URLS, NOAA_ONI_URL
from .io import read_csv_source, read_excel_source, write_excel


def load_oni_proxy_from_github() -> pd.DataFrame:
    """Carga el proxy ONI mensual ya publicado en GitHub."""

    return read_excel_source(DATA_URLS["oni_proxy"])


def fetch_oni_from_noaa() -> pd.DataFrame:
    """Descarga y normaliza el historico ONI oficial de NOAA."""

    import requests

    response = requests.get(NOAA_ONI_URL, timeout=30)
    response.raise_for_status()
    raw = pd.read_csv(StringIO(response.text), delim_whitespace=True)
    month_columns = [column for column in raw.columns if column.upper() != "YR"]
    melted = raw.melt(id_vars=["YR"], value_vars=month_columns, var_name="month", value_name="ONI")
    month_lookup = {name: idx for idx, name in enumerate(month_columns, start=1)}
    melted["fecha"] = pd.to_datetime(
        {
            "year": melted["YR"],
            "month": melted["month"].map(month_lookup),
            "day": 1,
        }
    )
    return melted[["fecha", "ONI"]].sort_values("fecha").reset_index(drop=True)


def load_reservoirs_from_github() -> pd.DataFrame:
    """Carga reservas hidraulicas desde GitHub."""

    return read_csv_source(DATA_URLS["reservoirs"])


def export_macro_artifacts(output_dir: str) -> dict[str, str]:
    """Exporta el proxy ONI mensual."""

    oni = load_oni_proxy_from_github()
    path = write_excel(oni, f"{output_dir}/Proxy_Climatico_ONI_Mensual.xlsx")
    return {"oni_proxy": str(path)}
