"""Procesamiento de niveles del rio."""

from __future__ import annotations

import pandas as pd

from .config import BasinBounds, DATA_URLS, DATOS_GOV_BASE_URL
from .io import fetch_json, read_excel_source, write_excel
from .transforms import normalize_columns


def fetch_hydrology_from_datos_gov(api_id: str = "pt9a-aamx", limit: int = 2000) -> pd.DataFrame:
    """Descarga niveles del rio desde datos.gov.co."""

    url = DATOS_GOV_BASE_URL.format(api_id=api_id)
    return pd.DataFrame(fetch_json(url, params={"$limit": limit}))


def prepare_hydrology_raw(df: pd.DataFrame, bounds: BasinBounds | None = None) -> pd.DataFrame:
    """Convierte tipos y filtra registros de la cuenca."""

    bounds = bounds or BasinBounds()
    result = df.copy()
    for column in ["latitud", "longitud", "valorobservado"]:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    result["fechaobservacion"] = pd.to_datetime(result["fechaobservacion"], errors="coerce")
    mask = (
        result["latitud"].between(bounds.lat_min, bounds.lat_max)
        & result["longitud"].between(bounds.lon_min, bounds.lon_max)
    )
    return result[mask].sort_values("fechaobservacion").copy()


def remove_hydrology_outliers(df: pd.DataFrame, max_value: float = 5.0) -> pd.DataFrame:
    """Elimina valores fuera del umbral tecnico definido en el notebook."""

    return df[df["valorobservado"] <= max_value].copy()


def monthly_hydrology(df: pd.DataFrame) -> pd.DataFrame:
    """Remuestrea niveles a promedio mensual."""

    result = df.copy()
    result["fechaobservacion"] = pd.to_datetime(result["fechaobservacion"])
    return (
        result.set_index("fechaobservacion")
        .resample("ME")["valorobservado"]
        .mean()
        .reset_index()
    )


def interpolate_and_normalize_hydrology(df: pd.DataFrame) -> pd.DataFrame:
    """Interpola nulos y agrega valor observado normalizado."""

    result = df.copy()
    result["valorobservado"] = (
        result["valorobservado"].interpolate(method="linear").bfill().ffill()
    )
    normalized = normalize_columns(result[["valorobservado"]], ["valorobservado"])
    result["valorobservado_norm"] = normalized["valorobservado"]
    return result


def load_prepared_hydrology(version: str = "hydrology_v3") -> pd.DataFrame:
    """Carga una version preparada de niveles publicada en GitHub."""

    return read_excel_source(DATA_URLS[version])


def export_hydrology_artifacts(output_dir: str, source: str = "github") -> dict[str, str]:
    """Exporta la serie mensual de niveles normalizada."""

    if source == "api":
        raw = fetch_hydrology_from_datos_gov()
        filtered = prepare_hydrology_raw(raw)
        monthly = monthly_hydrology(remove_hydrology_outliers(filtered))
        final = interpolate_and_normalize_hydrology(monthly)
    else:
        final = load_prepared_hydrology("hydrology_v3")
    path = write_excel(final, f"{output_dir}/Serie_Tiempo_Niveles_Rio_Filtrado_V3.xlsx")
    return {"hydrology_v3": str(path)}
