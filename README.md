# Framework para la Aplicacion de Tecnologias 4.0 y Ciencia de Datos en la Gestion Hidrica


El objetivo es crear  un pipeline modular para
preparar datos climaticos, hidrologicos, de calidad de agua y macrocontexto
para entrenamiento LSTM y generar predicciones con estos

## Autores

- Jose Barreto
- Juan Riataga

## Estructura

```text
.
|-- data/
|   |-- raw/              # Datos locales crudos, ignorados por Git
|   `-- processed/        # Artefactos generados, ignorados por Git
|-- notebooks/            # Notebook original para referencia y demo
|-- scripts/              # Scripts ejecutables
|-- src/proyecto_grado_v6 # Codigo fuente modular
|-- tests/                # Pruebas unitarias de transformaciones clave
|-- requirements.txt
`-- pyproject.toml
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

Para descargar una copia local de los datos fuente del repositorio original:

```bash
python scripts/download_raw_data.py
```

## Ejecucion desde GitHub web

1. Entra al repositorio en GitHub.
2. Abre la pestana `Actions`.
3. Selecciona el workflow `Run pipeline`.
4. Haz clic en `Run workflow`.
5. Cuando termine, abre la ejecucion y descarga los artifacts `raw-data` y
   `processed-data`.

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

## Equivalencia con el notebook

El repositorio conserva el notebook original en `notebooks/` y extrae el nucleo
reproducible a funciones. El pipeline genera los artefactos principales del
notebook usando las mismas fuentes de datos publicadas en GitHub y las mismas
reglas de transformacion documentadas en las celdas.

No se migraron como parte del nucleo las celdas puramente narrativas, las
visualizaciones exploratorias ni los graficos de apoyo. Esas celdas quedan en el
notebook original para consulta.

## Notas de migracion desde Colab

- La logica repetible vive en `src/proyecto_grado_v6/`.
- El notebook original se conserva en `notebooks/` como evidencia y demo.
- Las descargas externas se manejan desde funciones reutilizables.
- Los datos locales y resultados generados no se versionan.
- Las transformaciones con riesgo de regresion tienen pruebas unitarias.

## Licencia

Sin licencia por ahora.
