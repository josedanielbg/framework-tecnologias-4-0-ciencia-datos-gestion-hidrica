"""Transformaciones reutilizables del pipeline."""

from __future__ import annotations

import pandas as pd


def valid_year_month_mask(series: pd.Series) -> pd.Series:
    """Valida enteros YYYYMM descartando meses fuera del rango 1..12."""

    values = pd.to_numeric(series, errors="coerce")
    months = values % 100
    return months.between(1, 12)


def add_monthly_date_from_year_month(
    df: pd.DataFrame,
    column: str = "Ano_Mes",
    output_column: str = "fecha",
) -> pd.DataFrame:
    """Agrega una fecha mensual desde un identificador YYYYMM."""

    result = df.copy()
    result[output_column] = pd.to_datetime(result[column].astype(str), format="%Y%m")
    return result


def clean_numeric_text(series: pd.Series) -> pd.Series:
    """Convierte textos numericos con simbolos como <, > y comas decimales."""

    cleaned = (
        series.astype(str)
        .str.replace("<", "", regex=False)
        .str.replace(">", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")


def normalize_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Escala columnas numericas al rango [0, 1] usando MinMaxScaler."""

    result = df.copy()
    values = result[columns].fillna(0)
    try:
        from sklearn.preprocessing import MinMaxScaler

        scaler = MinMaxScaler()
        result[columns] = scaler.fit_transform(values)
    except ModuleNotFoundError:
        mins = values.min()
        ranges = values.max() - mins
        ranges = ranges.replace(0, 1)
        result[columns] = (values - mins) / ranges
    return result


def seasonal_mean_impute(df: pd.DataFrame, date_column: str, value_column: str) -> pd.DataFrame:
    """Imputa nulos usando el promedio historico del mismo mes calendario."""

    result = df.copy()
    dates = pd.to_datetime(result[date_column])
    result[value_column] = result.groupby(dates.dt.month)[value_column].transform(
        lambda values: values.fillna(values.mean())
    )
    return result
