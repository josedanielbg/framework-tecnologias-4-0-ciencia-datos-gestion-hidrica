"""Integracion del dataset maestro de entrenamiento."""

from __future__ import annotations

import pandas as pd

from .config import DATA_URLS
from .io import read_excel_source, write_excel
from .transforms import normalize_columns, seasonal_mean_impute


def load_super_master_v3() -> pd.DataFrame:
    """Carga el dataset super maestro V3 publicado en GitHub."""

    return read_excel_source(DATA_URLS["super_master_v3"])


def prepare_super_master_v5(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica imputacion estacional para reservas hidraulicas si la columna existe."""

    result = df.copy()
    if "fecha" in result.columns:
        result["fecha"] = pd.to_datetime(result["fecha"], errors="coerce")
    if {"fecha", "VolumenUtilDiarioMasa"}.issubset(result.columns):
        result = seasonal_mean_impute(result, "fecha", "VolumenUtilDiarioMasa")
    return result


def normalize_super_master(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza columnas numericas excluyendo campos temporales."""

    numeric_columns = list(df.select_dtypes(include=["float64", "int64"]).columns)
    numeric_columns = [column for column in numeric_columns if column.lower() not in {"a\u00f1o_mes"}]
    if not numeric_columns:
        return df.copy()
    return normalize_columns(df, numeric_columns)


def audit_dataset(df: pd.DataFrame) -> dict[str, int]:
    """Calcula indicadores basicos de auditoria."""

    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "null_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }


def export_final_dataset(output_dir: str) -> dict[str, str]:
    """Carga, prepara, normaliza y exporta el dataset final."""

    raw = load_super_master_v3()
    prepared = prepare_super_master_v5(raw)
    normalized = normalize_super_master(prepared)
    path = write_excel(normalized, f"{output_dir}/Dataset_V5_Final_Normalizado.xlsx")
    return {"final_dataset": str(path)}
