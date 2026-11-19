"""Reproducao do primeiro resultado do Spotify via OAuth PKCE."""

import base64
import hashlib
import json
import os
import secrets
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

import requests

from .apps import abrir_spotify
from .web import pesquisar_e_tocar_spotify


API = "https://api.spotify.com/v1"
AUTHORIZATION_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPES = "user-read-playback-state user-modify-playback-state user-read-private"
TOKEN_FILE = (
    Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    / "NexoAI"
    / "spotify-token.json"
)


def _configuracao():
    from config import SPOTIFY_CLIENT_ID, SPOTIFY_REDIRECT_URI

    if not SPOTIFY_CLIENT_ID.strip():
        raise RuntimeError(
            "Configure SPOTIFY_CLIENT_ID em config.py e cadastre o redirect URI "
            "http://127.0.0.1:8765/callback no Spotify Developer Dashboard."
        )
    return SPOTIFY_CLIENT_ID.strip(), SPOTIFY_REDIRECT_URI


def _salvar_token(token):
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(token), encoding="utf-8")


def _ler_token():
    try:
        return json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _pedir_autorizacao(client_id, redirect_uri):
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).decode("ascii").rstrip("=")
    state = secrets.token_urlsafe(24)
    resultado = {}

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            recebido = parse_qs(urlparse(self.path).query)
            self.server.oauth_result = {
                "code": recebido.get("code", [None])[0],
                "state": recebido.get("state", [None])[0],
                "error": recebido.get("error", [None])[0],
            }
            corpo = b"Autorizacao recebida. Pode fechar esta aba e voltar ao Jarvis."
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

        def log_message(self, formato, *args):
            return

    try:
        servidor = HTTPServer(("127.0.0.1", 8765), CallbackHandler)
    except OSError as erro:
        raise RuntimeError(
            "Nao consegui abrir a porta local 8765 para concluir o login do Spotify."
        ) from erro

    servidor.timeout = 180
    parametros = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": SCOPES,
        "state": state,
        "code_challenge_method": "S256",
        "code_challenge": challenge,
    }
    webbrowser.open(f"{AUTHORIZATION_URL}?{urlencode(parametros)}")
    try:
        servidor.handle_request()
        resultado = getattr(servidor, "oauth_result", None) or resultado
    finally:
        servidor.server_close()

    if resultado.get("state") != state:
        raise RuntimeError("A validacao de seguranca do login Spotify falhou ou expirou.")
    if resultado.get("error"):
        raise RuntimeError("O acesso ao Spotify foi cancelado.")
    if not resultado.get("code"):
        raise RuntimeError("O login Spotify expirou antes de ser autorizado.")

    resposta = requests.post(
        TOKEN_URL,
        data={
            "client_id": client_id,
            "grant_type": "authorization_code",
            "code": resultado["code"],
            "redirect_uri": redirect_uri,
            "code_verifier": verifier,
        },
        timeout=20,
    )
    resposta.raise_for_status()
    token = resposta.json()
    token["expires_at"] = time.time() + token.get("expires_in", 3600)
    _salvar_token(token)
    return token


def _access_token():
    client_id, redirect_uri = _configuracao()
    token = _ler_token()
    if token and token.get("access_token") and token.get("expires_at", 0) > time.time() + 60:
        return token["access_token"]

    if token and token.get("refresh_token"):
        resposta = requests.post(
            TOKEN_URL,
            data={
                "client_id": client_id,
                "grant_type": "refresh_token",
                "refresh_token": token["refresh_token"],
            },
            timeout=20,
        )
        if resposta.ok:
            renovado = resposta.json()
            renovado["refresh_token"] = renovado.get("refresh_token", token["refresh_token"])
            renovado["expires_at"] = time.time() + renovado.get("expires_in", 3600)
            _salvar_token(renovado)
            return renovado["access_token"]

    return _pedir_autorizacao(client_id, redirect_uri)["access_token"]


def _dispositivo(headers):
    """Aguarda o cliente abrir e escolhe o computador quando disponivel."""
    for tentativa in range(12):
        resposta = requests.get(f"{API}/me/player/devices", headers=headers, timeout=15)
        resposta.raise_for_status()
        dispositivos = resposta.json().get("devices", [])
        disponiveis = [item for item in dispositivos if not item.get("is_restricted")]
        computadores = [
            item for item in disponiveis
            if item.get("type", "").casefold() == "computer"
        ]
        candidatos = computadores or disponiveis
        dispositivo = next((item for item in candidatos if item.get("is_active")), None)
        if dispositivo is None and candidatos:
            dispositivo = candidatos[0]
            transferencia = requests.put(
                f"{API}/me/player",
                headers=headers,
                json={"device_ids": [dispositivo["id"]], "play": False},
                timeout=15,
            )
            transferencia.raise_for_status()
            time.sleep(1.2)
        if dispositivo:
            return dispositivo["id"]
        if tentativa < 11:
            time.sleep(1)
    return None


def tocar_spotify(consulta):
    """Busca a faixa mais relevante e pede ao Spotify para inicia-la."""
    consulta = consulta.strip()
    if not consulta:
        return "Diga o nome da musica ou artista que quer tocar."

    try:
        token = _access_token()
        cabecalho = {"Authorization": f"Bearer {token}"}
        busca = requests.get(
            f"{API}/search",
            headers=cabecalho,
            params={"q": consulta, "type": "track", "limit": 5, "market": "BR"},
            timeout=20,
        )
        busca.raise_for_status()
        faixas = busca.json().get("tracks", {}).get("items", [])
        faixa = next((item for item in faixas if item.get("is_playable", True)), None)
        if faixa is None:
            return f"Nao encontrei uma faixa reproduzivel para {consulta}."

        abrir_spotify()
        device_id = _dispositivo(cabecalho)
        if not device_id:
            return pesquisar_e_tocar_spotify(consulta)
        reproduzir = requests.put(
            f"{API}/me/player/play",
            headers=cabecalho,
            params={"device_id": device_id},
            json={"uris": [faixa["uri"]]},
            timeout=20,
        )
        if reproduzir.status_code == 204:
            artista = ", ".join(item["name"] for item in faixa.get("artists", []))
            return f"Tocando {faixa['name']} - {artista} no Spotify."

        if reproduzir.status_code == 404:
            return (
                "Nao encontrei um dispositivo Spotify ativo. Abra o Spotify, espere carregar "
                "e tente novamente."
            )
        if reproduzir.status_code == 403:
            return pesquisar_e_tocar_spotify(consulta)
        reproduzir.raise_for_status()
        return "Nao consegui iniciar a musica no Spotify."
    except requests.RequestException as erro:
        print(f"Erro na API do Spotify: {erro}")
        return pesquisar_e_tocar_spotify(consulta)
    except (RuntimeError, OSError, ValueError) as erro:
        print(f"Integracao Spotify indisponivel: {erro}")
        return pesquisar_e_tocar_spotify(consulta)
