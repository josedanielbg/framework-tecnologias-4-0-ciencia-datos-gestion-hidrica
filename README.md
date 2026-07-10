# Proyecto Grado V6 - Pipeline de datos Rio Bogota

Repositorio profesionalizado a partir del notebook `dataProyectoV6.ipynb`.
El objetivo es convertir las celdas de Colab en un pipeline modular para
preparar datos climaticos, hidrologicos, de calidad de agua y macrocontexto
para entrenamiento LSTM.

## Estructura

```text
.
├── data/
│   ├── raw/              # Datos locales crudos, ignorados por Git
│   └── processed/        # Artefactos generados, ignorados por Git
├── notebooks/            # Notebook original para referencia y demo
├── scripts/              # Scripts ejecutables
├── src/proyecto_grado_v6 # Codigo fuente modular
├── tests/                # Pruebas unitarias de transformaciones clave
├── requirements.txt
└── pyproject.toml
```

## Fuentes de datos

Los datos se consumen desde el repositorio publico:

https://github.com/jriatiga/dataset/tree/main/proyectoGradoV3

El codigo centraliza las rutas en `src/proyecto_grado_v6/config.py`. La carpeta
`data/` queda en `.gitignore` para evitar subir Excel, CSV o artefactos pesados.

## Instalacion

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Ejecucion

Opcion con paquete instalado:

```bash
proyecto-grado-v6 --output-dir data/processed
```

Opcion directa:

```bash
python scripts/run_pipeline.py
```

El pipeline escribe los principales artefactos en `data/processed/`:

- `Dataset_Maestro_Multiestacion_LSTM_V1.xlsx`
- `Serie_Tiempo_Niveles_Rio_Filtrado_V3.xlsx`
- `Calidad_Agua_Rio_Bogota_Top10_Mensual.xlsx`
- `Proxy_Climatico_ONI_Mensual.xlsx`
- `Dataset_V5_Final_Normalizado.xlsx`

## Pruebas

```bash
python -m unittest discover tests
```

## Notas de migracion desde Colab

- La logica repetible vive en `src/proyecto_grado_v6/`.
- El notebook original se conserva en `notebooks/` como evidencia y demo.
- Las descargas externas se manejan desde funciones reutilizables.
- Los datos locales y resultados generados no se versionan.
- Las transformaciones con riesgo de regresion tienen pruebas unitarias.

## Licencia

Definir la licencia antes de publicar el repositorio.
