"""Genera data/catalogo.parquet, el único archivo de datos que necesita la app.

Fuentes posibles:

  # 1) Tabla Gold de Databricks (usa variables de entorno, nunca el token en el código)
  export DATABRICKS_HOST=dbc-xxxx.cloud.databricks.com
  export DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxxx
  export DATABRICKS_TOKEN=dapi...
  python preparar_catalogo.py --databricks

  # 2) Uno o varios CSV con las columnas del dataset de Spotify (p. ej. dataset.csv)
  python preparar_catalogo.py --csv dataset.csv

  # 3) Catálogo sintético para probar la app sin datos reales
  python preparar_catalogo.py --demo
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd

from recomendador import CARACTERISTICAS, COLUMNAS_OBLIGATORIAS, limpiar_catalogo

SALIDA = Path(__file__).parent / "data" / "catalogo.parquet"

CONSULTA_GOLD = f"""
SELECT {", ".join(COLUMNAS_OBLIGATORIAS + ["popularity"])}
FROM workspace.default.gold_catalogo_recomendador
"""


def desde_databricks() -> pd.DataFrame:
    from databricks import sql  # pip install databricks-sql-connector

    columnas = COLUMNAS_OBLIGATORIAS + ["popularity"]
    lotes = []
    with sql.connect(
        server_hostname=os.environ["DATABRICKS_HOST"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        access_token=os.environ["DATABRICKS_TOKEN"],
    ) as conexion, conexion.cursor() as cursor:
        cursor.execute(CONSULTA_GOLD)
        while filas := cursor.fetchmany(50_000):
            lotes.append(pd.DataFrame(filas, columns=columnas))
            print(f"  {sum(len(l) for l in lotes):,} filas leídas…")
    return pd.concat(lotes, ignore_index=True)


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Acepta el CSV de Kaggle (dataset.csv) y el de 1.2M canciones (tracks_features.csv)."""
    if "track_id" not in df.columns and {"id", "name"} <= set(df.columns):
        df = df.rename(columns={"id": "track_id", "name": "track_name"})
    if "popularity" not in df.columns:
        df["popularity"] = np.nan
    artistas = df["artists"].astype(str)
    if artistas.str.startswith("[").mean() > 0.5:
        # "['Guns N' Roses', \"Slash\"]" → "Guns N' Roses, Slash"
        artistas = (
            artistas.str.replace(r"""['"]\s*,\s*['"]""", ", ", regex=True)
            .str.strip("[]")
            .str.strip("'\"")
        )
    df["artists"] = artistas.str.replace(";", ", ", regex=False)
    return df[[c for c in COLUMNAS_OBLIGATORIAS + ["popularity"] if c in df.columns]]


def desde_csv(rutas: list[str]) -> pd.DataFrame:
    partes = []
    for ruta in rutas:
        parte = normalizar_columnas(pd.read_csv(ruta))
        print(f"  {ruta}: {len(parte):,} filas")
        partes.append(parte)
    return pd.concat(partes, ignore_index=True)


def demo(n: int = 5_000, semilla: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(semilla)
    artistas = [f"Artista {i}" for i in range(400)]
    return pd.DataFrame({
        "track_id": [f"demo{i:018d}" for i in range(n)],
        "track_name": [f"Canción demo {i}" for i in range(n)],
        "artists": rng.choice(artistas, n),
        "duration_ms": rng.integers(150_000, 300_000, n),
        "popularity": rng.integers(0, 100, n),
        "tempo": rng.normal(122, 28, n).clip(60, 210),
        "energy": rng.beta(4, 2, n),
        "danceability": rng.beta(4, 3, n),
        "valence": rng.beta(2, 2, n),
        "acousticness": rng.beta(1, 4, n),
        "instrumentalness": rng.beta(0.5, 5, n),
        "liveness": rng.beta(1.5, 6, n),
        "speechiness": rng.beta(1, 10, n),
        "loudness": rng.normal(-7, 3, n).clip(-30, 0),
    })


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    fuente = parser.add_mutually_exclusive_group(required=True)
    fuente.add_argument("--databricks", action="store_true")
    fuente.add_argument("--csv", nargs="+", metavar="ARCHIVO")
    fuente.add_argument("--demo", action="store_true")
    parser.add_argument("--max-canciones", type=int, default=None,
                        help="Conservar solo las N más populares (útil si el parquet pesa demasiado para GitHub).")
    args = parser.parse_args()

    if args.databricks:
        crudo = desde_databricks()
    elif args.csv:
        crudo = desde_csv(args.csv)
    else:
        crudo = demo()

    # Las canciones con popularidad (dataset.csv) quedan primero y ganan en duplicados.
    catalogo = limpiar_catalogo(crudo)
    catalogo["artists"] = catalogo["artists"].str.replace(";", ", ", regex=False)
    if args.max_canciones:
        catalogo = catalogo.head(args.max_canciones)

    for columna in CARACTERISTICAS:
        catalogo[columna] = catalogo[columna].astype("float32")

    SALIDA.parent.mkdir(exist_ok=True)
    catalogo.to_parquet(SALIDA, index=False, compression="zstd")
    tamano = SALIDA.stat().st_size / 1e6
    print(f"Listo: {len(catalogo):,} canciones → {SALIDA} ({tamano:.1f} MB)")
    if tamano > 95:
        print("Aviso: GitHub rechaza archivos > 100 MB. Usa --max-canciones o Git LFS.")


if __name__ == "__main__":
    main()
