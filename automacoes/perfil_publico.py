"""Ações permitidas quando a interface está no perfil público."""

from .apps import abrir_calculadora, abrir_chrome, abrir_edge
from .web import (
    abrir_google,
    abrir_youtube,
    pesquisar_google,
    pesquisar_youtube,
    pesquisar_spotify,
    extrair_pedido_spotify,
    abrir_video_youtube,
    extrair_consulta_video_youtube,
)
from . import normalizar_texto


def executar_comando_publico(texto):
    """Executa somente ações explícitas e não destrutivas do perfil público."""
    texto = normalizar_texto(texto)

    pedido_spotify = extrair_pedido_spotify(texto)
    if pedido_spotify is not None:
        acao_spotify, consulta_spotify = pedido_spotify
        if not consulta_spotify:
            return "Diga o nome da musica ou artista para pesquisar no Spotify."
        if acao_spotify == "play":
            from .spotify_player import tocar_spotify
            return tocar_spotify(consulta_spotify)
        return pesquisar_spotify(consulta_spotify)

    consulta_video = extrair_consulta_video_youtube(texto)
    if consulta_video is not None:
        if consulta_video:
            return abrir_video_youtube(consulta_video)
        return "Diga qual video voce quer abrir no YouTube."

    if "spotify" in texto:
        return "No perfil público, posso pesquisar no Spotify, mas não executar outros comandos dele."

    comandos_abrir = {
        "abrir calculadora": abrir_calculadora,
        "abrir a calculadora": abrir_calculadora,
        "abre calculadora": abrir_calculadora,
        "abra calculadora": abrir_calculadora,
        "abrir chrome": abrir_chrome,
        "abrir o chrome": abrir_chrome,
        "abre chrome": abrir_chrome,
        "abra chrome": abrir_chrome,
        "abrir edge": abrir_edge,
        "abrir o edge": abrir_edge,
        "abre edge": abrir_edge,
        "abra edge": abrir_edge,
        "abrir google": abrir_google,
        "abrir o google": abrir_google,
        "abre google": abrir_google,
        "abra google": abrir_google,
        "abrir youtube": abrir_youtube,
        "abrir o youtube": abrir_youtube,
        "abre youtube": abrir_youtube,
        "abra youtube": abrir_youtube,
    }
    acao = comandos_abrir.get(texto)
    if acao:
        return acao()

    gatilhos = (
        ("pesquise no google ", pesquisar_google),
        ("pesquisar no google ", pesquisar_google),
        ("pesquisa no google ", pesquisar_google),
        ("pesquise no youtube ", pesquisar_youtube),
        ("pesquisar no youtube ", pesquisar_youtube),
        ("pesquisa no youtube ", pesquisar_youtube),
    )
    for gatilho, pesquisar in gatilhos:
        if texto.startswith(gatilho):
            consulta = texto[len(gatilho):].strip()
            if consulta:
                return pesquisar(consulta)
            return "Diga o que você quer pesquisar."

    return None
