"""Guardar la playlist en la cuenta de Spotify del usuario (OAuth Authorization Code).

No guarda nada en servidor: las canciones viajan en el parámetro `state`
del OAuth, así la playlist sobrevive a la redirección de Spotify.

Notas de la API (2026):
- Las apps en Development Mode requieren que el dueño tenga Premium y solo
  admiten 5 usuarios autorizados (se agregan en el Dashboard de Spotify).
- Los endpoints de playlists se renombraron de /tracks a /items; aquí se
  intenta primero la ruta nueva y luego la antigua.
"""

from __future__ import annotations

import base64
from urllib.parse import urlencode

import requests

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API = "https://api.spotify.com/v1"
SCOPES = "playlist-modify-private playlist-modify-public"


class ErrorSpotify(RuntimeError):
    pass


def codificar_estado(zona: str, track_ids: list[str]) -> str:
    return f"{zona}|{','.join(track_ids)}"


def decodificar_estado(estado: str) -> tuple[str, list[str]]:
    zona, _, ids = estado.partition("|")
    return zona, [i for i in ids.split(",") if i]


def url_autorizacion(client_id: str, redirect_uri: str, estado: str) -> str:
    return AUTH_URL + "?" + urlencode({
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": SCOPES,
        "state": estado,
        "show_dialog": "false",
    })


def obtener_token(code: str, client_id: str, client_secret: str, redirect_uri: str) -> str:
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    r = requests.post(
        TOKEN_URL,
        data={"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri},
        headers={"Authorization": f"Basic {basic}"},
        timeout=15,
    )
    if r.status_code != 200:
        raise ErrorSpotify(f"No se pudo obtener el token ({r.status_code}): {r.text[:200]}")
    return r.json()["access_token"]


def _post(token: str, rutas: list[str], cuerpo: dict) -> dict:
    """Intenta cada ruta en orden; útil para los endpoints renombrados."""
    ultimo = None
    for ruta in rutas:
        r = requests.post(API + ruta, json=cuerpo, headers={"Authorization": f"Bearer {token}"}, timeout=15)
        if r.status_code in (200, 201):
            return r.json()
        ultimo = r
        if r.status_code not in (403, 404, 405, 410):
            break
    raise ErrorSpotify(f"Spotify respondió {ultimo.status_code}: {ultimo.text[:200]}")


def crear_playlist(token: str, nombre: str, descripcion: str, track_ids: list[str]) -> str:
    """Crea una playlist privada y devuelve su URL."""
    me = requests.get(API + "/me", headers={"Authorization": f"Bearer {token}"}, timeout=15)
    if me.status_code != 200:
        raise ErrorSpotify(
            f"No se pudo leer el perfil ({me.status_code}). "
            "¿El usuario está agregado en el Dashboard de Spotify (Development Mode)?"
        )
    user_id = me.json()["id"]

    playlist = _post(
        token,
        ["/me/playlists", f"/users/{user_id}/playlists"],
        {"name": nombre, "description": descripcion, "public": False},
    )
    uris = [f"spotify:track:{t}" for t in track_ids]
    for i in range(0, len(uris), 100):
        _post(token, [f"/playlists/{playlist['id']}/items", f"/playlists/{playlist['id']}/tracks"],
              {"uris": uris[i:i + 100]})
    return playlist["external_urls"]["spotify"]
