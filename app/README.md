# 🏃 Corre a tu Ritmo

App web (Streamlit) del proyecto de Datos Masivos: eliges **3 canciones** y tu **zona de entrenamiento**, y te
devuelve una playlist de **≥10 canciones y ≥40 minutos**. Opcionalmente la guarda en tu cuenta de Spotify.

Método (igual que el notebook *Entrega Final*): `StandardScaler` → similitud coseno ponderada (BPM 40 %)
contra el centroide de las 3 favoritas, filtrando por el rango de BPM de la zona y ampliándolo si faltan
canciones. El PCA (≥90 % de varianza) se usa para la visualización.

Catálogo publicado: **1,250,006 canciones únicas** (dataset.csv + tracks_features.csv, sin duplicados).

## Estructura

| Archivo | Qué hace |
|---|---|
| `recomendador.py` | Lógica pura: limpieza, escalado, PCA, búsqueda y `recomendar()` |
| `preparar_catalogo.py` | Genera `data/catalogo.parquet` desde Databricks, CSV o datos demo |
| `app.py` | Interfaz web |
| `spotify.py` | OAuth + creación de la playlist en Spotify |

## Correr en local

```bash
pip install -r requirements-preparar.txt

# Opción A: desde la tabla Gold de Databricks
export DATABRICKS_HOST=dbc-xxxx.cloud.databricks.com
export DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxxx
export DATABRICKS_TOKEN=dapi...
python preparar_catalogo.py --databricks

# Opción B: desde los CSV (dataset.csv de Kaggle + tracks_features.csv de 1.2 M canciones)
python preparar_catalogo.py --csv dataset.csv tracks_features.csv

streamlit run app.py
```

> Si el parquet pesa más de 100 MB GitHub no lo acepta: usa `--max-canciones 300000` (se quedan las más
> populares) o Git LFS.

## Conectar Spotify (opcional)

1. Entra a <https://developer.spotify.com/dashboard> → **Create app**. Marca *Web API*.
2. **Redirect URI**: `http://127.0.0.1:8501` en local (Spotify no acepta `localhost`), y la URL de
   Streamlit Cloud (`https://<tu-app>.streamlit.app`) cuando la publiquen.
3. En **User Management** agrega el correo de Spotify de cada persona que vaya a usarla.
   En Development Mode el máximo es **5 usuarios** y el dueño de la app necesita **Premium**.
4. Copia `.streamlit/secrets.toml.example` a `.streamlit/secrets.toml` y llena `client_id`,
   `client_secret` y `redirect_uri`. **No subas ese archivo a GitHub** (ya está en `.gitignore`).
5. Abre la app en `http://127.0.0.1:8501` (la misma URL del Redirect URI).

Sin secretos configurados, el botón *Guardar en Spotify* muestra los enlaces para pegarlos a mano en una
playlist de Spotify de escritorio.

## Publicar (Streamlit Community Cloud)

1. Sube este folder a GitHub (con `data/catalogo.parquet`).
2. En <https://share.streamlit.io> → *New app* → elige el repo y `app.py`.
3. En *Settings → Secrets* pega el contenido de tu `secrets.toml`, con el `redirect_uri` de la URL pública.
