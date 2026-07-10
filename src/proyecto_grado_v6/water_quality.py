"""Procesamiento de calidad de agua."""

from __future__ import annotations

import pandas as pd

from .config import DATA_URLS, DATOS_GOV_BASE_URL
from .io import fetch_json, read_excel_source, write_excel
from .transforms import clean_numeric_text


def fetch_quality_from_datos_gov(api_id: str = "62gv-3857", limit: int = 5000) -> pd.DataFrame:
    """Descarga un dataset de calidad de agua desde datos.gov.co."""

    url = DATOS_GOV_BASE_URL.format(api_id=api_id)
    return pd.DataFrame(fetch_json(url, params={"$limit": limit}))


def load_water_quality_v1() -> pd.DataFrame:
    """Carga la version V1 publicada en GitHub."""

    return read_excel_source(DATA_URLS["water_quality_v1"])


def load_water_quality_top10() -> pd.DataFrame:
    """Carga la matriz mensual top 10 de parametros fisicoquimicos."""

    return read_excel_source(DATA_URLS["water_quality_top10"])


def clean_parameter_value(df: pd.DataFrame, value_column: str) -> pd.DataFrame:
    """Limpia valores fisicoquimicos expresados como texto."""

    result = df.copy()
    result[value_column] = clean_numeric_text(result[value_column])
    return result


def monthly_quality_mean(
    df: pd.DataFrame,
    date_column: str,
    value_column: str,
    group_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Agrupa calidad de agua a frecuencia mensual."""

    group_columns = group_columns or []
    result = df.copy()
    result[date_column] = pd.to_datetime(result[date_column], errors="coerce")
    result["fecha"] = result[date_column].dt.to_period("M").dt.to_timestamp()
    return result.groupby(["fecha", *group_columns], as_index=False)[value_column].mean()


def export_quality_artifacts(output_dir: str) -> dict[str, str]:
    """Exporta la matriz de calidad de agua usada para integracion."""

    quality = load_water_quality_top10()
    path = write_excel(quality, f"{output_dir}/Calidad_Agua_Rio_Bogota_Top10_Mensual.xlsx")
    return {"water_quality_top10": str(path)}
