"""Configuracion central de fuentes de datos y nodos."""

from __future__ import annotations

from dataclasses import dataclass

RAW_BASE_URL = (
    "https://raw.githubusercontent.com/jriatiga/dataset/refs/heads/main/"
    "proyectoGradoV3"
)

NODE_COORDINATES = {
    "Villapinzon_Alta": {"lat": 5.21, "lon": -73.60},
    "Tocancipa_Media": {"lat": 4.96, "lon": -73.00},
    "Sopo_Sur": {"lat": 4.70, "lon": -73.95},
    "Bogota_Sabana": {"lat": 4.60, "lon": -74.15},
}

DATA_FILES = {
    "climate_villapinzon": "Variables_Climaticas_Villapinzon_Alta.xlsx",
    "climate_tocancipa": "Variables_Climaticas_Tocancipa_Media.xlsx",
    "climate_sopo": "Variables_Climaticas_Sopo_Sur.xlsx",
    "climate_bogota": "Variables_Climaticas_Bogota_Sabana.xlsx",
    "climate_master": "Dataset_Maestro_Multiestacion_LSTM_V1.xlsx",
    "hydrology_v1": "Serie_Tiempo_Niveles_Rio_Filtrado.xlsx",
    "hydrology_v2": "Serie_Tiempo_Niveles_Rio_Filtrado_V2.xlsx",
    "hydrology_v3": "Serie_Tiempo_Niveles_Rio_Filtrado_V3.xlsx",
    "water_quality_v1": "Calidad_Agua_Rio_Bogota_V1.xlsx",
    "water_quality_top10": "Calidad_Agua_Rio_Bogota_Top10_Mensual.xlsx",
    "human_consumption_quality": "Calidad_Agua_Consumo_Humano.xlsx",
    "oni_proxy": "Proxy_Climatico_ONI_Mensual.xlsx",
    "super_master_v3": "Dataset_Super_Maestro_Entrenamiento_V3.xlsx",
    "reservoirs": "ReservasHidr%C3%A1ulicasenMasa.csv",
}

DATA_URLS = {key: f"{RAW_BASE_URL}/{name}" for key, name in DATA_FILES.items()}

NASA_POWER_URL = (
    "https://power.larc.nasa.gov/api/temporal/monthly/point"
    "?parameters=PRECTOTCORR,T2M_MAX,T2M_MIN&community=AG"
    "&longitude={lon}&latitude={lat}&format=JSON&start={start}&end={end}"
)

NOAA_ONI_URL = (
    "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/"
    "detrend.nino34.ascii.txt"
)

DATOS_GOV_BASE_URL = "https://www.datos.gov.co/resource/{api_id}.json"


@dataclass(frozen=True)
class BasinBounds:
    """Caja geografica usada en el notebook para aislar la cuenca."""

    lat_min: float = 4.0
    lat_max: float = 5.5
    lon_min: float = -74.5
    lon_max: float = -73.5

