"""Construccion de datasets limpios para modelado predictivo."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from .io import ensure_dir, read_csv_source, read_excel_source, write_excel


NODE_FILES = {
    "Bogota_Sabana": "Variables_Climaticas_Bogota_Sabana.xlsx",
    "Sopo_Sur": "Variables_Climaticas_Sopo_Sur.xlsx",
    "Tocancipa_Media": "Variables_Climaticas_Tocancipa_Media.xlsx",
    "Villapinzon_Alta": "Variables_Climaticas_Villapinzon_Alta.xlsx",
}

QUALITY_RENAMES = {
    "CONDUCTIVIDAD ELECTRICA": "calidad_conductividad",
    "DEMANDA QUIMICA DE OXIGENO (DQO)": "calidad_dqo",
    "FOSFORO REACTIVO DISUELTO": "calidad_fosforo_reactivo",
    "NITRATO": "calidad_nitrato",
    "NITRITO": "calidad_nitrito",
    "OXIGENO DISUELTO (OD)": "calidad_oxigeno_disuelto",
    "SOLIDOS SUSPENDIDOS TOTALES": "calidad_solidos_suspendidos",
    "TEMPERATURA": "calidad_temperatura",
    "TURBIDEZ": "calidad_turbidez",
    "pH": "calidad_ph",
}


def month_end(series: pd.Series) -> pd.Series:
    """Convierte fechas a fin de mes para alinear fuentes mensuales."""

    return pd.to_datetime(series, errors="coerce").dt.to_period("M").dt.to_timestamp("M")


def find_year_month_column(df: pd.DataFrame) -> str:
    """Detecta la columna YYYYMM aunque venga con codificacion distinta."""

    for column in df.columns:
        normalized = str(column).lower()
        if "mes" in normalized or "month" in normalized:
            return column
    return df.columns[0]


def load_climate_raw(raw_dir: str | Path) -> pd.DataFrame:
    """Carga variables climaticas crudas por nodo en formato mensual ancho."""

    raw = Path(raw_dir)
    frames = []
    for node, file_name in NODE_FILES.items():
        df = read_excel_source(raw / file_name)
        year_month_col = find_year_month_column(df)
        year_month = pd.to_numeric(df[year_month_col], errors="coerce")
        months = year_month % 100
        df = df[months.between(1, 12)].copy()
        year_month = pd.to_numeric(df[year_month_col], errors="coerce")
        df["fecha"] = pd.to_datetime(year_month.astype("Int64").astype(str), format="%Y%m")
        df["fecha"] = month_end(df["fecha"])
        keep = ["fecha", "Precipitacion_mm", "Temp_Max_C", "Temp_Min_C"]
        df = df[keep].rename(
            columns={
                "Precipitacion_mm": f"clima_precipitacion_mm_{node}",
                "Temp_Max_C": f"clima_temp_max_c_{node}",
                "Temp_Min_C": f"clima_temp_min_c_{node}",
            }
        )
        frames.append(df)

    climate = frames[0]
    for frame in frames[1:]:
        climate = climate.merge(frame, on="fecha", how="outer")
    return climate.sort_values("fecha").reset_index(drop=True)


def load_hydrology(raw_dir: str | Path) -> pd.DataFrame:
    """Carga la serie mensual de nivel del rio sin usar la columna normalizada."""

    df = read_excel_source(Path(raw_dir) / "Serie_Tiempo_Niveles_Rio_Filtrado_V3.xlsx")
    df["fecha"] = month_end(df["fechaobservacion"])
    return (
        df[["fecha", "valorobservado"]]
        .rename(columns={"valorobservado": "nivel_rio_m"})
        .sort_values("fecha")
        .reset_index(drop=True)
    )


def load_water_quality(raw_dir: str | Path) -> pd.DataFrame:
    """Carga parametros fisicoquimicos mensuales."""

    df = read_excel_source(Path(raw_dir) / "Calidad_Agua_Rio_Bogota_Top10_Mensual.xlsx")
    df["fecha"] = month_end(df["fecha"])
    return df.rename(columns=QUALITY_RENAMES).sort_values("fecha").reset_index(drop=True)


def load_oni(raw_dir: str | Path) -> pd.DataFrame:
    """Carga proxy climatico ONI mensual."""

    df = read_excel_source(Path(raw_dir) / "Proxy_Climatico_ONI_Mensual.xlsx")
    df["fecha"] = month_end(df["Fecha"])
    return df[["fecha", "ONI"]].rename(columns={"ONI": "oni"}).sort_values("fecha")


def load_reservoirs(raw_dir: str | Path) -> pd.DataFrame:
    """Carga reservas hidraulicas del agregado Bogota a frecuencia mensual."""

    path = Path(raw_dir) / "ReservasHidráulicasenMasa.csv"
    if not path.exists():
        path = Path(raw_dir) / "ReservasHidr%C3%A1ulicasenMasa.csv"
    df = read_csv_source(path)
    df = df[df["CodigoEmbalse"] == "AGREGADO_BOGOTA"].copy()
    df["fecha"] = month_end(df["Fecha"])
    numeric_cols = [
        "CapacidadUtilMasa",
        "VolumenUtilDiarioMasa",
        "VolumenTotalMasa",
        "VertimientosMasa",
    ]
    monthly = df.groupby("fecha", as_index=False)[numeric_cols].mean()
    return monthly.rename(
        columns={
            "CapacidadUtilMasa": "reservas_capacidad_util_masa",
            "VolumenUtilDiarioMasa": "reservas_volumen_util_diario_masa",
            "VolumenTotalMasa": "reservas_volumen_total_masa",
            "VertimientosMasa": "reservas_vertimientos_masa",
        }
    ).sort_values("fecha")


def merge_monthly_sources(raw_dir: str | Path, start: str = "2015-01-01") -> pd.DataFrame:
    """Fusiona las fuentes con una fila por mes y sin expandir fechas duplicadas."""

    required_frames = [
        load_climate_raw(raw_dir),
        load_hydrology(raw_dir),
        load_water_quality(raw_dir),
        load_oni(raw_dir),
    ]
    data = required_frames[0]
    for frame in required_frames[1:]:
        data = data.merge(frame, on="fecha", how="inner")

    reservoirs = load_reservoirs(raw_dir)
    data = data.merge(reservoirs, on="fecha", how="left")
    data = data[data["fecha"] >= pd.Timestamp(start)].copy()
    return data.sort_values("fecha").drop_duplicates("fecha").reset_index(drop=True)


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega variables temporales ciclicas y categoricas simples."""

    result = df.copy()
    result["mes"] = result["fecha"].dt.month
    result["trimestre"] = result["fecha"].dt.quarter
    result["temporada_lluvia"] = result["mes"].isin([3, 4, 5, 10, 11]).astype(int)
    return result


def add_basin_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega promedios espaciales simples de clima para reducir dimensionalidad."""

    result = df.copy()
    precip_cols = [column for column in result.columns if column.startswith("clima_precipitacion")]
    tmax_cols = [column for column in result.columns if column.startswith("clima_temp_max")]
    tmin_cols = [column for column in result.columns if column.startswith("clima_temp_min")]
    result["clima_precipitacion_media_cuenca"] = result[precip_cols].mean(axis=1)
    result["clima_temp_max_media_cuenca"] = result[tmax_cols].mean(axis=1)
    result["clima_temp_min_media_cuenca"] = result[tmin_cols].mean(axis=1)
    return result


def add_lags_and_rollings(
    df: pd.DataFrame,
    columns: Iterable[str],
    lags: Iterable[int] = (1, 2, 3, 6),
    windows: Iterable[int] = (3, 6),
) -> pd.DataFrame:
    """Agrega rezagos y promedios moviles sin mirar al futuro."""

    result = df.copy()
    for column in columns:
        for lag in lags:
            result[f"{column}_lag{lag}"] = result[column].shift(lag)
        for window in windows:
            result[f"{column}_roll{window}_mean"] = result[column].shift(1).rolling(window).mean()
    return result


def add_missing_indicators_and_fill(
    df: pd.DataFrame,
    columns: Iterable[str],
    fill_value: float = 0.0,
) -> tuple[pd.DataFrame, list[str]]:
    """Marca ausencias estructurales y rellena sin mirar al futuro."""

    result = df.copy()
    indicators = []
    for column in columns:
        if column in result.columns and result[column].isna().any():
            indicator = f"{column}_was_missing"
            result[indicator] = result[column].isna().astype(int)
            result[column] = result[column].fillna(fill_value)
            indicators.append(indicator)
    return result, indicators


def build_model_dataset(
    raw_dir: str | Path = "data/raw",
    output_dir: str | Path = "data/processed",
    horizon_months: int = 1,
) -> dict[str, object]:
    """Construye dataset limpio y dataset listo para modelado supervisado."""

    output = ensure_dir(output_dir)
    clean = merge_monthly_sources(raw_dir)
    clean = add_basin_aggregates(clean)
    clean = add_time_features(clean)

    optional_columns = [column for column in clean.columns if column.startswith("reservas_")]
    clean, missing_indicator_cols = add_missing_indicators_and_fill(clean, optional_columns)

    lag_columns = [
        column
        for column in clean.columns
        if column != "fecha"
        and column not in {"mes", "trimestre", "temporada_lluvia"}
        and not column.endswith("_was_missing")
        and pd.api.types.is_numeric_dtype(clean[column])
    ]
    model = add_lags_and_rollings(clean, lag_columns)
    model[f"target_nivel_rio_m_t_plus_{horizon_months}"] = model["nivel_rio_m"].shift(
        -horizon_months
    )
    model = model.dropna(subset=[f"target_nivel_rio_m_t_plus_{horizon_months}"]).copy()

    numeric_cols = [
        column
        for column in model.columns
        if column != "fecha" and pd.api.types.is_numeric_dtype(model[column])
    ]
    model = model.dropna(subset=numeric_cols).copy()

    model["split"] = chronological_split(model)

    clean_path = write_excel(clean, output / "Dataset_Modelado_Mensual_Limpio.xlsx")
    model_path = write_excel(model, output / "Dataset_Modelado_Mensual_Supervisado.xlsx")
    csv_path = output / "Dataset_Modelado_Mensual_Supervisado.csv"
    model.to_csv(csv_path, index=False)

    compact = build_compact_model_dataset(clean, horizon_months=horizon_months)
    compact_path = write_excel(compact, output / "Dataset_Modelado_Mensual_Compacto.xlsx")
    compact_csv_path = output / "Dataset_Modelado_Mensual_Compacto.csv"
    compact.to_csv(compact_csv_path, index=False)

    return {
        "clean_dataset": str(clean_path),
        "model_dataset": str(model_path),
        "model_dataset_csv": str(csv_path),
        "compact_dataset": str(compact_path),
        "compact_dataset_csv": str(compact_csv_path),
        "rows_clean": int(len(clean)),
        "rows_model": int(len(model)),
        "rows_compact": int(len(compact)),
        "date_min": str(model["fecha"].min().date()) if len(model) else None,
        "date_max": str(model["fecha"].max().date()) if len(model) else None,
        "missing_indicators": missing_indicator_cols,
        "target": f"target_nivel_rio_m_t_plus_{horizon_months}",
    }


def chronological_split(df: pd.DataFrame) -> pd.Series:
    """Crea split temporal robusto aun cuando la serie sea corta."""

    n_rows = len(df)
    train_end = max(1, int(n_rows * 0.7))
    validation_end = max(train_end + 1, int(n_rows * 0.85))
    split = pd.Series("test", index=df.index)
    split.iloc[:train_end] = "train"
    split.iloc[train_end:validation_end] = "validation"
    return split


def build_compact_model_dataset(df: pd.DataFrame, horizon_months: int = 1) -> pd.DataFrame:
    """Construye una matriz supervisada compacta para modelos base."""

    base = df.copy()
    lag_columns = [
        "nivel_rio_m",
        "clima_precipitacion_media_cuenca",
        "clima_temp_max_media_cuenca",
        "clima_temp_min_media_cuenca",
        "calidad_dqo",
        "calidad_oxigeno_disuelto",
        "calidad_turbidez",
        "calidad_ph",
        "oni",
        "reservas_volumen_util_diario_masa",
    ]
    lag_columns = [column for column in lag_columns if column in base.columns]
    compact = add_lags_and_rollings(base, lag_columns, lags=(1, 2, 3), windows=(3,))
    compact[f"target_nivel_rio_m_t_plus_{horizon_months}"] = compact["nivel_rio_m"].shift(
        -horizon_months
    )
    selected_current = [
        "fecha",
        "mes",
        "trimestre",
        "temporada_lluvia",
        "nivel_rio_m",
        "clima_precipitacion_media_cuenca",
        "clima_temp_max_media_cuenca",
        "clima_temp_min_media_cuenca",
        "calidad_dqo",
        "calidad_oxigeno_disuelto",
        "calidad_turbidez",
        "calidad_ph",
        "oni",
        "reservas_volumen_util_diario_masa",
        "reservas_volumen_util_diario_masa_was_missing",
        f"target_nivel_rio_m_t_plus_{horizon_months}",
    ]
    generated = [
        column
        for column in compact.columns
        if any(column.startswith(f"{source}_lag") for source in lag_columns)
        or any(column.startswith(f"{source}_roll") for source in lag_columns)
    ]
    keep = [column for column in selected_current if column in compact.columns] + generated
    compact = compact[keep].dropna().copy()
    numeric_cols = [
        column
        for column in compact.columns
        if column != "fecha" and pd.api.types.is_numeric_dtype(compact[column])
    ]
    compact[numeric_cols] = compact[numeric_cols].ffill().fillna(0)
    compact["split"] = chronological_split(compact)
    return compact
