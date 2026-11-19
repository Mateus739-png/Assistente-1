"""Configuracoes locais do Jarvis e da integracao opcional com a API Spotify."""

# No Spotify Developer Dashboard, cadastre exatamente este Redirect URI:
# http://127.0.0.1:8765/callback
# O fluxo PKCE usa apenas o Client ID; nao coloque Client Secret aqui.
SPOTIFY_CLIENT_ID = ""
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8765/callback"
