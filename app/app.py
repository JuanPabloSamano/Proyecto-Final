"""App web: elige 3 canciones + tu zona de entrenamiento → playlist para correr.

Ejecutar:  streamlit run app.py
"""

from __future__ import annotations

import os

# jemalloc libera mejor la memoria al leer el parquet de 1.2 M de canciones
# (medido: ~280 MB extra contra ~500 MB con el asignador del sistema).
os.environ.setdefault("ARROW_DEFAULT_MEMORY_POOL", "jemalloc")

from html import escape
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import spotify
from recomendador import EJERCICIOS, Recomendador, leer_catalogo

RUTA_CATALOGO = Path(__file__).parent / "data" / "catalogo.parquet"
RUTA_ESTILO = Path(__file__).parent / "estilo.css"

# Color y descripción de cada zona (como las zonas de frecuencia cardiaca: frío → caliente).
ZONAS = {
    "1": ("#5B9BFF", "Calentamiento o recuperación activa."),
    "2": ("#2ED3B7", "Ritmo conversacional para construir base aeróbica."),
    "3": ("#C8FF2E", "Ritmo constante de entrenamiento."),
    "4": ("#FFB020", "Tempo run: cadencia alta y esfuerzo fuerte."),
    "5": ("#FF4D4D", "Series cortas a máxima cadencia."),
}

st.set_page_config(page_title="Corre a tu Ritmo", page_icon="🏃", layout="centered")
st.markdown(f"<style>{RUTA_ESTILO.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


# --------------------------------------------------------------------------- datos
@st.cache_resource(show_spinner="Cargando catálogo y entrenando PCA…")
def cargar_recomendador() -> Recomendador:
    return Recomendador(leer_catalogo(RUTA_CATALOGO))


def config_spotify() -> dict | None:
    # load_if_toml_exists evita el aviso rojo de Streamlit cuando no hay secrets.toml.
    try:
        if not st.secrets.load_if_toml_exists() or "spotify" not in st.secrets:
            return None
        cfg = dict(st.secrets["spotify"])
    except Exception:
        return None
    return cfg if {"client_id", "client_secret", "redirect_uri"} <= cfg.keys() else None


def etiqueta(fila: pd.Series) -> str:
    return f"{fila['track_name']} — {fila['artists']}  ·  {fila['tempo']:.0f} BPM"


if not RUTA_CATALOGO.exists():
    st.error("No existe `data/catalogo.parquet`. Ejecuta primero `python preparar_catalogo.py` (ver README).")
    st.stop()

rec = cargar_recomendador()
cfg_spotify = config_spotify()


# ------------------------------------------------- regreso desde Spotify (OAuth)
parametros = st.query_params
if "code" in parametros and "state" in parametros and cfg_spotify:
    zona_ret, ids_ret = spotify.decodificar_estado(parametros["state"])
    code = parametros["code"]
    st.query_params.clear()  # el code solo se puede usar una vez
    with st.spinner("Creando tu playlist en Spotify…"):
        try:
            token = spotify.obtener_token(code, cfg_spotify["client_id"], cfg_spotify["client_secret"],
                                          cfg_spotify["redirect_uri"])
            nombre_zona = EJERCICIOS.get(zona_ret, ("Running",))[0]
            st.session_state["spotify_url"] = spotify.crear_playlist(
                token,
                nombre=f"🏃 {nombre_zona} — Corre a tu Ritmo",
                descripcion="Generada con PCA + similitud coseno a partir de 3 canciones favoritas.",
                track_ids=ids_ret,
            )
        except spotify.ErrorSpotify as e:
            st.session_state["spotify_error"] = str(e)
elif "error" in parametros:
    st.session_state["spotify_error"] = f"Spotify canceló la autorización: {parametros['error']}"
    st.query_params.clear()

if url := st.session_state.pop("spotify_url", None):
    st.success("¡Playlist creada en tu cuenta de Spotify!")
    st.link_button("Abrir playlist en Spotify", url, type="primary")
if err := st.session_state.pop("spotify_error", None):
    st.error(err)




def html(contenido: str) -> None:
    st.markdown(contenido, unsafe_allow_html=True)


def paso(numero: int, titulo: str, subtitulo: str) -> None:
    html(f'<div class="paso"><div class="n">{numero}</div><h3>{titulo}</h3></div>'
         f'<p class="paso-sub">{subtitulo}</p>')


# ---------------------------------------------------------------------- hero
html(f"""
<div class="hero">
  <svg class="pulso" viewBox="0 0 460 120" aria-hidden="true">
    <path d="M0 70 H120 L140 70 L155 30 L172 105 L190 15 L208 92 L222 70 H300 L315 52 L330 82 L342 70 H460"/>
  </svg>
  <div class="eyebrow">Proyecto · Datos Masivos</div>
  <h1>Corre a tu <span class="acento">Ritmo</span></h1>
  <p class="lead">Elige 3 canciones que te encanten y tu zona de entrenamiento.
  Te armamos una playlist con el BPM justo para tu cadencia.</p>
  <div class="chips">
    <div class="chip"><b>{len(rec.catalogo):,}</b> canciones</div>
    <div class="chip"><b>5</b> zonas de BPM</div>
    <div class="chip"><b>10+</b> canciones · <b>40+</b> min</div>
  </div>
</div>
""")


# --------------------------------------------------------- 1 · canciones
paso(1, "Tus 3 canciones favoritas", "Busca por título o artista y elige la versión correcta.")
columnas = st.columns(3)
ids_favoritas: list[str] = []
for i, col in enumerate(columnas, start=1):
    with col:
        texto = st.text_input(f"Canción {i}", key=f"busqueda_{i}", placeholder="🔍  Título o artista")
        if not texto:
            html('<div class="vacia">Aún sin elegir</div>')
            continue
        opciones = rec.buscar(texto)
        opciones = opciones[~opciones["track_id"].isin(ids_favoritas)]
        if opciones.empty:
            st.warning("Sin resultados en el catálogo.")
            continue
        elegido = st.selectbox(
            "Elige la versión", opciones.index, key=f"opcion_{i}",
            format_func=lambda idx: etiqueta(rec.catalogo.loc[idx]), label_visibility="collapsed",
        )
        fila = rec.catalogo.loc[elegido]
        ids_favoritas.append(fila["track_id"])
        html(f'<div class="cancion-ok"><div class="txt"><div class="t">{escape(fila["track_name"])}</div>'
             f'<div class="a">{escape(fila["artists"])}</div></div>'
             f'<span class="bpm">{fila["tempo"]:.0f} BPM</span></div>')


# ------------------------------------------------------------ 2 · zona
paso(2, "Tu zona de entrenamiento", "El rango de BPM de la playlist sigue la cadencia de cada zona.")
zona = st.segmented_control(
    "Zona", list(EJERCICIOS), default="3", required=True, key="zona_elegida",
    format_func=lambda k: f"Z{k} · {EJERCICIOS[k][0].split(' / ')[0]}",
    label_visibility="collapsed", width="stretch",
) or "3"
color_zona, desc_zona = ZONAS[zona]
nombre_zona, bpm_min, bpm_max = EJERCICIOS[zona]
segmentos = "".join(
    f'<div class="seg{" activo" if k == zona else ""}" style="background:{ZONAS[k][0]}"></div>' for k in EJERCICIOS
)
marcas = "".join(f"<span>{EJERCICIOS[k][1]}</span>" for k in EJERCICIOS)
html(f"""
<div class="escala"><div class="barra">{segmentos}</div><div class="marcas">{marcas}</div></div>
<div class="zona-info" style="border-left:4px solid {color_zona}">
  <span class="nombre" style="color:{color_zona}">{nombre_zona}</span>
  <span class="rango">{bpm_min}–{bpm_max} BPM</span>
  <span class="desc">{desc_zona}</span>
</div>
""")
st.write("")
medio_tiempo = st.toggle(
    "Aceptar canciones a medio o doble tiempo (p. ej. 85 BPM cuenta como 170)", value=False,
    help="Spotify a veces reporta el tempo a la mitad; correr a 170 pasos/min sobre una canción de 85 BPM "
         "se siente igual.",
)


# ------------------------------------------------------------- generar
st.write("")
listo = len(ids_favoritas) == 3
faltan = 3 - len(ids_favoritas)
texto_boton = "Generar mi playlist  →" if listo else f"Elige {faltan} canción{'es' if faltan > 1 else ''} más"
if st.button(texto_boton, type="primary", disabled=not listo, key="generar", width="stretch"):
    try:
        st.session_state["resultado"] = rec.recomendar(ids_favoritas, zona, medio_tiempo=medio_tiempo)
        st.session_state["favoritas"] = ids_favoritas
        st.session_state["zona"] = zona
    except ValueError as e:
        st.error(str(e))


# ------------------------------------------------------------ resultados
res = st.session_state.get("resultado")
if res is None:
    html('<div class="pie">Corre a tu Ritmo · Proyecto de Datos Masivos</div>')
    st.stop()

zona_res = st.session_state["zona"]
color_res = ZONAS[zona_res][0]
html(f"""
<div class="res-cabecera" style="--zona:{color_res}">
  <div class="eyebrow">Tu playlist · Z{zona_res}</div>
  <h2>{res.ejercicio}</h2>
  <div class="metricas">
    <div class="metrica"><div class="v">{len(res.playlist)}</div><div class="l">canciones</div></div>
    <div class="metrica"><div class="v">{res.minutos_totales:.0f} min</div><div class="l">duración total</div></div>
    <div class="metrica"><div class="v">{res.bpm_objetivo[0]}–{res.bpm_objetivo[1]}</div><div class="l">BPM objetivo</div></div>
    <div class="metrica"><div class="v">{res.playlist['similitud_coseno'].mean():.0%}</div><div class="l">similitud media</div></div>
  </div>
</div>
""")
for nota in res.notas:
    html(f'<p class="nota" style="--zona:{color_res}">{escape(nota)}</p>')

filas = []
for _, c in res.playlist.iterrows():
    similitud = max(0.0, min(1.0, float(c["similitud_coseno"])))
    filas.append(
        f'<div class="pista"><span class="num">{c["orden"]:02d}</span>'
        f'<div style="min-width:0"><div class="t">{escape(c["track_name"])}</div>'
        f'<div class="a">{escape(c["artists"])}</div></div>'
        f'<span class="bpm">{c["tempo"]:.0f} BPM</span>'
        f'<span class="dur">{c["duracion"]}</span>'
        f'<div class="sim"><div class="riel"><i style="width:{similitud:.0%}"></i></div>{similitud:.0%}</div>'
        f'<a class="play" href="{escape(c["spotify_url"])}" target="_blank" rel="noopener" '
        f'title="Abrir en Spotify" aria-label="Abrir {escape(c["track_name"])} en Spotify">▶</a></div>'
    )
html(f'<div class="lista" style="--zona:{color_res}">{"".join(filas)}</div>')

html('<div class="seccion">Empieza con la #1</div>')
st.iframe(f"https://open.spotify.com/embed/track/{res.playlist['track_id'].iloc[0]}?theme=0", height=152)

tabla = res.playlist[["orden", "track_name", "artists", "tempo", "duracion", "similitud_coseno", "spotify_url"]]
ids_playlist = res.playlist["track_id"].tolist()
c1, c2 = st.columns(2)
with c1:
    st.download_button(
        "⬇  Descargar CSV", tabla.to_csv(index=False).encode("utf-8-sig"),
        file_name="playlist_recomendada.csv", mime="text/csv", width="stretch",
    )
with c2:
    if cfg_spotify:
        estado = spotify.codificar_estado(zona_res, ids_playlist)
        st.link_button(
            "Guardar en mi Spotify",
            spotify.url_autorizacion(cfg_spotify["client_id"], cfg_spotify["redirect_uri"], estado),
            type="primary", width="stretch",
        )
    else:
        with st.popover("Guardar en Spotify", width="stretch"):
            st.write("Copia estos enlaces y pégalos dentro de una playlist en Spotify de escritorio:")
            st.code("\n".join(res.playlist["spotify_url"]), language=None)

# Proyección PC1–PC2 (ilustrativa: la similitud usa las 9 características ponderadas).
with st.expander("¿Cómo se eligieron? · Proyección PCA"):
    rng = np.random.default_rng(42)
    muestra = rng.choice(len(rec.catalogo), size=min(1500, len(rec.catalogo)), replace=False)
    fav_idx = rec.catalogo.index[rec.catalogo["track_id"].isin(st.session_state["favoritas"])]
    puntos = pd.concat([
        pd.DataFrame(rec.coordenadas_pca(muestra)[:, :2], columns=["PC1", "PC2"]).assign(tipo="Catálogo"),
        pd.DataFrame(rec.coordenadas_pca(res.playlist.index)[:, :2], columns=["PC1", "PC2"]).assign(tipo="Recomendadas"),
        pd.DataFrame(rec.coordenadas_pca(fav_idx)[:, :2], columns=["PC1", "PC2"]).assign(tipo="Tus favoritas"),
    ])
    tipos = ["Catálogo", "Recomendadas", "Tus favoritas"]
    puntos["orden_capa"] = puntos["tipo"].map({t: i for i, t in enumerate(tipos)})
    grafica = alt.Chart(puntos).mark_circle(opacity=0.9).encode(
        x=alt.X("PC1", axis=alt.Axis(grid=False)), y=alt.Y("PC2", axis=alt.Axis(grid=False)),
        color=alt.Color("tipo", scale=alt.Scale(domain=tipos, range=["#3A4556", color_res, "#FF6B5B"]),
                        legend=alt.Legend(title=None, orient="bottom")),
        size=alt.Size("tipo", scale=alt.Scale(domain=tipos, range=[14, 110, 300]), legend=None),
        order=alt.Order("orden_capa"),
        tooltip=["tipo"],
    ).properties(height=400, background="transparent").configure_view(strokeWidth=0)
    st.altair_chart(grafica, width="stretch")
    st.caption(
        f"El PCA conserva {rec.pca.n_components_} componentes ({rec.pca.explained_variance_ratio_.sum():.1%} de la "
        "varianza). La recomendación usa similitud coseno ponderada (BPM 40 %) contra el centroide de tus "
        "3 favoritas, dentro del rango de BPM de la zona."
    )

html('<div class="pie">Corre a tu Ritmo · Proyecto de Datos Masivos · '
     'PCA + similitud coseno sobre 9 características de audio</div>')
