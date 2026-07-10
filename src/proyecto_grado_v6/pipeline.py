"""Orquestacion del pipeline completo."""

from __future__ import annotations

from pathlib import Path

from .climate import audit_climate_master, build_climate_eda, build_climate_master
from .climate import add_climate_features, load_climate_nodes_from_github
from .hydrology import load_prepared_hydrology
from .integration import audit_dataset, export_final_dataset
from .io import ensure_dir, write_excel
from .macro_context import load_oni_proxy_from_github
from .water_quality import load_water_quality_top10


def run_pipeline(output_dir: str | Path = "data/processed") -> dict[str, object]:
    """Ejecuta el flujo reproducible usando las fuentes publicadas en GitHub."""

    output = ensure_dir(output_dir)
    artifacts: dict[str, object] = {}

    climate_nodes = load_climate_nodes_from_github()
    climate_eda = build_climate_eda(climate_nodes)
    climate_processed = add_climate_features(climate_eda)
    climate_master = build_climate_master(climate_processed)
    climate_path = write_excel(
        climate_master,
        output / "Dataset_Maestro_Multiestacion_LSTM_V1.xlsx",
    )
    artifacts["climate_master"] = str(climate_path)
    artifacts["climate_audit"] = audit_climate_master(climate_master)

    hydrology = load_prepared_hydrology("hydrology_v3")
    hydrology_path = write_excel(
        hydrology,
        output / "Serie_Tiempo_Niveles_Rio_Filtrado_V3.xlsx",
    )
    artifacts["hydrology_v3"] = str(hydrology_path)
    artifacts["hydrology_audit"] = audit_dataset(hydrology)

    water_quality = load_water_quality_top10()
    water_quality_path = write_excel(
        water_quality,
        output / "Calidad_Agua_Rio_Bogota_Top10_Mensual.xlsx",
    )
    artifacts["water_quality_top10"] = str(water_quality_path)
    artifacts["water_quality_audit"] = audit_dataset(water_quality)

    oni = load_oni_proxy_from_github()
    oni_path = write_excel(oni, output / "Proxy_Climatico_ONI_Mensual.xlsx")
    artifacts["oni_proxy"] = str(oni_path)
    artifacts["oni_audit"] = audit_dataset(oni)

    artifacts.update(export_final_dataset(str(output)))
    return artifacts
