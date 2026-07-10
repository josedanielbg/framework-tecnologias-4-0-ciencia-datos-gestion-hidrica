"""Procesamiento de variables climaticas para los nodos de la cuenca."""

from __future__ import annotations

import pandas as pd

from .config import DATA_URLS, NASA_POWER_URL, NODE_COORDINATES
from .io import fetch_json, read_excel_source, write_excel
from .transforms import normalize_columns, valid_year_month_mask

YEAR_MONTH_COLUMN = "A\u00f1o_Mes"
CLIMATE_COLUMNS = ["Precipitacion_mm", "Temp_Max_C", "Temp_Min_C"]


def fetch_nasa_power_node(
    node_name: str,
    lat: float,
    lon: float,
    start: int = 2015,
    end: int = 2025,
) -> pd.DataFrame:
    """Descarga clima mensual desde NASA POWER para un nodo."""

    url = NASA_POWER_URL.format(lat=lat, lon=lon, start=start, end=end)
    data = fetch_json(url)
    parameters = data["properties"]["parameter"]
    frame = pd.DataFrame(
        {
            "Precipitacion_mm": pd.Series(parameters["PRECTOTCORR"]),
            "Temp_Max_C": pd.Series(parameters["T2M_MAX"]),
            "Temp_Min_C": pd.Series(parameters["T2M_MIN"]),
        }
    ).reset_index(names=YEAR_MONTH_COLUMN)
    frame["Nodo"] = node_name
    return clean_climate_frame(frame)


def fetch_nasa_power_nodes() -> dict[str, pd.DataFrame]:
    """Descarga clima mensual para todos los nodos definidos."""

    return {
        name: fetch_nasa_power_node(name, coords["lat"], coords["lon"])
        for name, coords in NODE_COORDINATES.items()
    }


def load_climate_nodes_from_github() -> dict[str, pd.DataFrame]:
    """Carga los cuatro Excel climaticos publicados en GitHub."""

    mapping = {
        "Villapinzon_Alta": DATA_URLS["climate_villapinzon"],
        "Tocancipa_Media": DATA_URLS["climate_tocancipa"],
        "Sopo_Sur": DATA_URLS["climate_sopo"],
        "Bogota_Sabana": DATA_URLS["climate_bogota"],
    }
    return {name: clean_climate_frame(read_excel_source(url)) for name, url in mapping.items()}


def clean_climate_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra meses invalidos y tipa columnas climaticas."""

    result = df.copy()
    result = result[valid_year_month_mask(result[YEAR_MONTH_COLUMN])].copy()
    result[YEAR_MONTH_COLUMN] = pd.to_numeric(result[YEAR_MONTH_COLUMN], errors="coerce").astype(
        "int64"
    )
    for column in CLIMATE_COLUMNS:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    return result


def build_climate_eda(nodes: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Une nodos climaticos en formato largo para EDA y feature engineering."""

    frames = []
    for node_name, frame in nodes.items():
        current = clean_climate_frame(frame)
        current["Nodo"] = node_name
        current["Fecha"] = pd.to_datetime(current[YEAR_MONTH_COLUMN].astype(str), format="%Y%m")
        frames.append(current)
    return pd.concat(frames, ignore_index=True)


def add_climate_features(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega diferencias, rezagos y normalizacion por columnas base."""

    result = df.copy().sort_values(["Nodo", YEAR_MONTH_COLUMN])
    for column in CLIMATE_COLUMNS:
        result[f"{column}_diff"] = result.groupby("Nodo")[column].diff()
    result["Prec_Lag1"] = result.groupby("Nodo")["Precipitacion_mm"].shift(1)
    columns_to_scale = ["Precipitacion_mm", "Temp_Max_C", "Temp_Min_C", "Prec_Lag1"]
    return normalize_columns(result, columns_to_scale)


def build_climate_master(df: pd.DataFrame) -> pd.DataFrame:
    """Crea el dataset maestro multiestacion usado por el modelo LSTM."""

    master = df.pivot(
        index=YEAR_MONTH_COLUMN,
        columns="Nodo",
        values=["Precipitacion_mm", "Prec_Lag1"],
    )
    master.columns = [f"{metric}_{node}" for metric, node in master.columns]
    return master.fillna(0).reset_index()


def audit_climate_master(df: pd.DataFrame, expected_columns: int = 8) -> dict[str, int]:
    """Devuelve metricas de auditoria del maestro climatico."""

    feature_columns = [column for column in df.columns if column != YEAR_MONTH_COLUMN]
    outside_range = ((df[feature_columns] < 0) | (df[feature_columns] > 1)).sum().sum()
    return {
        "rows": int(df.shape[0]),
        "feature_columns": int(len(feature_columns)),
        "expected_feature_columns": expected_columns,
        "null_values": int(df.isna().sum().sum()),
        "outside_0_1_range": int(outside_range),
    }


def export_climate_artifacts(output_dir: str) -> dict[str, str]:
    """Construye y exporta los artefactos climaticos principales."""

    nodes = load_climate_nodes_from_github()
    eda = build_climate_eda(nodes)
    processed = add_climate_features(eda)
    master = build_climate_master(processed)
    path = write_excel(master, f"{output_dir}/Dataset_Maestro_Multiestacion_LSTM_V1.xlsx")
    return {"climate_master": str(path)}
