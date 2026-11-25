"""Lógica del recomendador (misma que el notebook "Entrega Final").

Se separa de la interfaz para poder usarla desde Streamlit, desde el
notebook o desde pruebas sin depender de input() ni de display().
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

CARACTERISTICAS = [
    "tempo", "energy", "danceability", "valence", "acousticness",
    "instrumentalness", "liveness", "speechiness", "loudness",
]

COLUMNAS_OBLIGATORIAS = ["track_id", "track_name", "artists", "duration_ms"] + CARACTERISTICAS

# Importancia de cada característica musical (deben sumar 1).
PESOS_CARACTERISTICAS = {
    "tempo": 0.40,
    "energy": 0.15,
    "danceability": 0.15,
    "valence": 0.10,
    "acousticness": 0.05,
    "instrumentalness": 0.05,
    "liveness": 0.03,
    "speechiness": 0.03,
    "loudness": 0.04,
}

# Rangos ORIENTATIVOS de BPM por zona de entrenamiento.
EJERCICIOS = {
    "1": ("Caminata", 90, 119),
    "2": ("Trote suave", 120, 139),
    "3": ("Running moderado", 140, 159),
    "4": ("Running intenso", 160, 179),
    "5": ("Intervalos / alta intensidad", 180, 200),
}


def limpiar_catalogo(df: pd.DataFrame) -> pd.DataFrame:
    """Mismos filtros que la celda "Preparar canciones para recomendar"."""
    faltantes = sorted(set(COLUMNAS_OBLIGATORIAS) - set(df.columns))
    if faltantes:
        raise ValueError(f"Faltan columnas en el catálogo: {faltantes}")

    columnas = COLUMNAS_OBLIGATORIAS + (["popularity"] if "popularity" in df.columns else [])
    rec = df[columnas].copy()
    if "popularity" not in rec.columns:
        rec["popularity"] = np.nan

    for columna in CARACTERISTICAS + ["duration_ms", "popularity"]:
        rec[columna] = pd.to_numeric(rec[columna], errors="coerce")
    rec = rec.dropna(subset=COLUMNAS_OBLIGATORIAS)

    rec["track_id"] = rec["track_id"].astype(str).str.strip()
    rec["track_name"] = rec["track_name"].astype(str)
    rec["artists"] = rec["artists"].astype(str)

    rec = rec[
        rec["tempo"].between(1, 250)
        & rec["duration_ms"].between(60_000, 900_000)
        & (rec["track_id"].str.len() >= 10)
    ]
    rec = (
        rec.sort_values("popularity", ascending=False, na_position="last")
        .drop_duplicates(subset="track_id")
        .reset_index(drop=True)
    )
    if len(rec) < 13:
        raise ValueError("Se necesitan al menos 13 canciones válidas para el recomendador.")
    return rec


@dataclass
class Resultado:
    playlist: pd.DataFrame
    ejercicio: str
    bpm_objetivo: tuple[int, int]
    bpm_utilizado: tuple[float, float]
    ampliacion_bpm: int
    minutos_totales: float
    centroide_pca: np.ndarray
    versiones_repetidas: int
    medio_tiempo: bool = False
    notas: list[str] = field(default_factory=list)


def _bpm_efectivo(tempo: np.ndarray, desde: float, hasta: float, medio_tiempo: bool) -> np.ndarray:
    """Si se acepta medio/doble tiempo, una canción de 85 BPM cuenta como 170."""
    if not medio_tiempo:
        return tempo
    efectivo = tempo.copy()
    for factor in (2.0, 0.5):
        fuera = (efectivo < desde) | (efectivo > hasta)
        alterno = tempo * factor
        usar = fuera & (alterno >= desde) & (alterno <= hasta)
        efectivo[usar] = alterno[usar]
    return efectivo


# Solo las candidatas más parecidas pasan al ordenamiento fino (con 1.2 M de canciones
# un rango de BPM puede tener cientos de miles). Basta y sobra para 10 canciones / 40 min.
MAX_CANDIDATAS = 3000


def leer_catalogo(ruta) -> pd.DataFrame:
    """Lee el parquet con textos en pyarrow sin pasar por objetos de Python (menos memoria)."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    texto = pd.StringDtype("pyarrow")
    tabla = pq.read_table(ruta)
    df = tabla.to_pandas(
        types_mapper={pa.string(): texto, pa.large_string(): texto}.get,
        self_destruct=True, split_blocks=True,
    )
    del tabla
    pa.default_memory_pool().release_unused()  # devolver al sistema los búferes de lectura
    return df


class Recomendador:
    def __init__(self, catalogo: pd.DataFrame):
        # Textos con pyarrow y números en float32: con ~1.2 M de canciones esto
        # reduce la memoria a menos de la mitad (Streamlit Cloud da ~1 GB).
        self.catalogo = catalogo.reset_index(drop=True)
        for columna in ["track_id", "track_name", "artists"]:
            self.catalogo[columna] = self.catalogo[columna].astype("string[pyarrow]")

        pesos = np.array([PESOS_CARACTERISTICAS[c] for c in CARACTERISTICAS])
        if not np.isclose(pesos.sum(), 1.0):
            raise ValueError("Los pesos deben sumar 1.")

        # Estandarizar columna por columna directo en float32 (equivale a StandardScaler
        # pero sin copias de 1.2 M x 9 en float64).
        n = len(self.catalogo)
        self.raiz_pesos = np.sqrt(pesos).astype(np.float32)
        self.media = np.empty(len(CARACTERISTICAS))
        self.desviacion = np.empty(len(CARACTERISTICAS))
        self.X_ponderado = np.empty((n, len(CARACTERISTICAS)), dtype=np.float32)
        for j, columna in enumerate(CARACTERISTICAS):
            valores = self.catalogo[columna].to_numpy(dtype=np.float64)
            self.media[j] = valores.mean()
            self.desviacion[j] = valores.std() or 1.0
            self.X_ponderado[:, j] = (valores - self.media[j]) / self.desviacion[j] * self.raiz_pesos[j]

        # PCA (≥90 % de varianza) para la visualización. Se ajusta con una muestra
        # aleatoria de 100 mil canciones: las componentes son prácticamente iguales
        # y evita una SVD sobre 1.2 M de filas al arrancar la app.
        muestra = np.random.default_rng(42).choice(n, size=min(n, 100_000), replace=False)
        self.pca = PCA(n_components=0.90, svd_solver="full")
        self.pca.fit(self.X_ponderado[muestra] / self.raiz_pesos)

    def coordenadas_pca(self, indices) -> np.ndarray:
        """Proyección PCA (sin pesos) de las filas indicadas."""
        return self.pca.transform(self.X_ponderado[np.asarray(indices)] / self.raiz_pesos)

    # ------------------------------------------------------------------ búsqueda
    def buscar(self, texto: str, limite: int = 15) -> pd.DataFrame:
        """Busca por título y/o artista. Ordena por popularidad (ya viene ordenado)."""
        texto = texto.strip()
        if not texto:
            return self.catalogo.iloc[0:0]
        # Cada palabra puede estar en el título o en el artista ("bad guy billie").
        nombres, artistas = self.catalogo["track_name"], self.catalogo["artists"]
        mascara = pd.Series(True, index=self.catalogo.index)
        for palabra in texto.split():
            mascara &= nombres.str.contains(palabra, case=False, regex=False) | artistas.str.contains(
                palabra, case=False, regex=False
            )
        return self.catalogo[mascara].head(limite)

    # ------------------------------------------------------------ recomendación
    def recomendar(
        self,
        ids_favoritas: list[str],
        opcion_ejercicio: str,
        minimo_canciones: int = 10,
        minimo_minutos: int = 40,
        medio_tiempo: bool = False,
    ) -> Resultado:
        if len(ids_favoritas) != 3 or len(set(ids_favoritas)) != 3:
            raise ValueError("Debes seleccionar exactamente 3 canciones diferentes.")
        if opcion_ejercicio not in EJERCICIOS:
            raise ValueError("Ejercicio inválido: elige un número del 1 al 5.")

        cat = self.catalogo
        favoritas = cat[cat["track_id"].isin(ids_favoritas)]
        if len(favoritas) != 3:
            raise ValueError("Una canción elegida no se encuentra en el catálogo.")

        indices_favoritas = favoritas.index.to_numpy()
        centroide_ponderado = self.X_ponderado[indices_favoritas].mean(axis=0)
        centroide_pca = self.coordenadas_pca(indices_favoritas).mean(axis=0)

        nombre, bpm_min, bpm_max = EJERCICIOS[opcion_ejercicio]
        objetivo_ms = minimo_minutos * 60 * 1000
        tempo = cat["tempo"].to_numpy(dtype=np.float64)
        duracion = cat["duration_ms"].to_numpy(dtype=np.float64)
        no_favorita = np.ones(len(cat), dtype=bool)
        no_favorita[indices_favoritas] = False

        # Ampliar gradualmente el rango si faltan canciones.
        for margen in (0, 10, 20, 40, 250):
            desde_bpm = max(1, bpm_min - margen)
            hasta_bpm = min(250, bpm_max + margen)
            bpm_ef = _bpm_efectivo(tempo, desde_bpm, hasta_bpm, medio_tiempo)
            indices_candidatos = np.flatnonzero((bpm_ef >= desde_bpm) & (bpm_ef <= hasta_bpm) & no_favorita)
            if len(indices_candidatos) >= minimo_canciones and duracion[indices_candidatos].sum() >= objetivo_ms:
                break
        else:
            raise ValueError("El catálogo no tiene suficientes canciones o minutos disponibles.")
        bpm_ef_candidatos = bpm_ef[indices_candidatos]

        # Similitud coseno ponderada contra el centroide de las favoritas.
        X_candidatos = self.X_ponderado[indices_candidatos].copy()
        if medio_tiempo:
            # Comparar con el tempo que se siente al correr, no con el reportado.
            i_tempo = CARACTERISTICAS.index("tempo")
            X_candidatos[:, i_tempo] = (
                (bpm_ef_candidatos - self.media[i_tempo]) / self.desviacion[i_tempo] * self.raiz_pesos[i_tempo]
            )
        similitud = cosine_similarity(X_candidatos, centroide_ponderado.reshape(1, -1)).ravel()
        del X_candidatos

        if len(similitud) > MAX_CANDIDATAS:
            mejores = np.argpartition(-similitud, MAX_CANDIDATAS)[:MAX_CANDIDATAS]
            indices_candidatos, similitud = indices_candidatos[mejores], similitud[mejores]
            bpm_ef_candidatos = bpm_ef_candidatos[mejores]

        candidatos = cat.iloc[indices_candidatos].copy()
        candidatos["bpm_efectivo"] = bpm_ef_candidatos
        candidatos["similitud_coseno"] = similitud

        # Criterios de desempate.
        bpm_ef = candidatos["bpm_efectivo"]
        candidatos["diferencia_bpm_objetivo"] = np.where(
            bpm_ef < bpm_min, bpm_min - bpm_ef, np.where(bpm_ef > bpm_max, bpm_ef - bpm_max, 0)
        )
        candidatos["diferencia_bpm_favoritas"] = (candidatos["tempo"] - favoritas["tempo"].mean()).abs()
        candidatos["diferencia_energy"] = (candidatos["energy"] - favoritas["energy"].mean()).abs()
        candidatos["diferencia_danceability"] = (
            candidatos["danceability"] - favoritas["danceability"].mean()
        ).abs()

        candidatos = candidatos.sort_values(
            by=[
                "similitud_coseno", "diferencia_bpm_objetivo", "diferencia_bpm_favoritas",
                "diferencia_energy", "diferencia_danceability", "popularity", "track_id",
            ],
            ascending=[False, True, True, True, True, False, True],
            na_position="last",
            kind="mergesort",
        )

        # Quitar versiones repetidas (mismo título y artista).
        def normalizar(serie: pd.Series) -> pd.Series:
            return serie.astype("string").str.casefold().str.strip().str.replace(r"\s+", " ", regex=True)

        clave = normalizar(candidatos["track_name"]) + "||" + normalizar(candidatos["artists"])
        total_antes = len(candidatos)
        candidatos = candidatos[~clave.duplicated(keep="first")]
        repetidas = total_antes - len(candidatos)

        # Tomar canciones hasta cumplir ambos mínimos.
        acumulado = candidatos["duration_ms"].cumsum().to_numpy()
        posicion = np.arange(1, len(candidatos) + 1)
        cumple = (posicion >= minimo_canciones) & (acumulado >= objetivo_ms)
        if not cumple.any():
            raise ValueError("Después de eliminar duplicados no hay suficientes canciones o minutos.")
        corte = int(np.argmax(cumple)) + 1
        playlist = candidatos.iloc[:corte].copy()

        playlist.insert(0, "orden", range(1, len(playlist) + 1))
        playlist["duracion"] = playlist["duration_ms"].apply(
            lambda ms: f"{int(ms // 60000)}:{int((ms % 60000) // 1000):02d}"
        )
        playlist["spotify_url"] = "https://open.spotify.com/track/" + playlist["track_id"].astype(str)

        notas = []
        if margen:
            notas.append(f"Se amplió el rango ±{margen} BPM para completar la playlist.")
        if medio_tiempo:
            n_alt = int((playlist["bpm_efectivo"] != playlist["tempo"]).sum())
            if n_alt:
                notas.append(f"{n_alt} canciones entran por medio/doble tiempo.")

        return Resultado(
            playlist=playlist,
            ejercicio=nombre,
            bpm_objetivo=(bpm_min, bpm_max),
            bpm_utilizado=(desde_bpm, hasta_bpm),
            ampliacion_bpm=margen,
            minutos_totales=float(playlist["duration_ms"].sum()) / 60000,
            centroide_pca=centroide_pca,
            versiones_repetidas=repetidas,
            medio_tiempo=medio_tiempo,
            notas=notas,
        )
