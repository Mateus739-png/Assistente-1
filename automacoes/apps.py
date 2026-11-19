import os
import subprocess
import ctypes
import time

VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_PLAY_PAUSE = 0xB3


def abrir_programa(nome, mensagem, argumentos=()):
    argumentos = list(argumentos)
    try:
        subprocess.Popen([nome, *argumentos])
        return mensagem
    except FileNotFoundError:
        caminhos = {
            "steam": [
                r"C:\Program Files (x86)\Steam\steam.exe",
                r"C:\Program Files\Steam\steam.exe",
            ],
            "code": [
                r"C:\Program Files\Microsoft VS Code\Code.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
            ],
            "edge": [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ],
            "chrome": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ],
        }
        for caminho in caminhos.get(nome, []):
            if os.path.isfile(caminho):
                try:
                    subprocess.Popen([caminho, *argumentos])
                    return mensagem
                except OSError as erro:
                    print(f"Erro ao iniciar {nome} em {caminho}: {erro}")
                    break
        print(f"Programa n\u00e3o encontrado: {nome}")
        return f"N\u00e3o consegui abrir {nome}."
    except OSError as erro:
        print(f"Erro ao abrir {nome}: {erro}")
        return f"N\u00e3o consegui abrir {nome}."

def abrir_link(link, mensagem):
    try:
        os.startfile(link)
        return mensagem
    except (OSError, AttributeError) as erro:
        print(f"Erro ao abrir {link}: {erro}")
        return f"Não consegui abrir {link}."

def abrir_edge():
    return abrir_programa(
        "edge",
        "Abrindo o Edge."
    )


def abrir_chrome():
    return abrir_programa(
        "chrome",
        "Abrindo o Google Chrome."
    )


def abrir_calculadora():
    return abrir_programa(
        "calc.exe",
        "Abrindo a calculadora."
    )


def abrir_steam():
    return abrir_programa("steam", "Abrindo a Steam.")

def abrir_vscode():
    return abrir_programa("code", "Abrindo o VS Code.")

def abrir_whatsapp():
    return abrir_link(
        "https://web.whatsapp.com",
        "Abrindo o WhatsApp."
    )

def abrir_spotify():
    executavel = r"C:\Users\User\AppData\Roaming\Spotify\Spotify.exe"
    try:
        subprocess.Popen([executavel])
        return "Abrindo o Spotify."
    except OSError as erro:
        print(f"Erro ao abrir Spotify em {executavel}: {erro}")
        try:
            os.startfile("spotify:")
            return "Abrindo o Spotify."
        except (OSError, AttributeError) as erro_uri:
            print(f"Erro ao abrir o Spotify pelo protocolo: {erro_uri}")
            return "N\u00e3o consegui abrir o Spotify."

def abrir_discord():
    return abrir_link(
        "discord://",
        "Abrindo o Discord."
    )


# ==========================================================
# JOGOS STEAM
# ==========================================================

def abrir_rocket_league():
    return abrir_link(
        "steam://rungameid/252950",
        "Abrindo o Rocket League."
    )


def abrir_breakpoint():
    return abrir_link(
        "steam://rungameid/2231380",
        "Abrindo o Ghost Recon Breakpoint."
    )


def abrir_stormworks():
    return abrir_link(
        "steam://rungameid/573090",
        "Abrindo o Stormworks."
    )


def abrir_motorfest():
    return abrir_link(
        "steam://rungameid/2698940",
        "Abrindo o The Crew Motorfest."
    )


def abrir_carx_street():
    return abrir_link(
        "steam://rungameid/1119730",
        "Abrindo o CarX Street."
    )


def abrir_pubg():
    return abrir_link(
        "steam://rungameid/578080",
        "Abrindo o PUBG."
    )


def abrir_watch_dogs_2():
    return abrir_link(
        "steam://rungameid/447040",
        "Abrindo o Watch Dogs 2."
    )


# ==========================================================
# TLAUNCHER
# ==========================================================

def abrir_tlauncher():
    try:
        os.startfile("TLauncher")
        return "Abrindo o TLauncher."
    except Exception as erro:
        print(f"⚠️ Erro ao abrir TLauncher: {erro}")
        return "Não consegui abrir o TLauncher."


# ==========================================================
# PROJETO SEXTA-FEIRA
# ==========================================================

def abrir_projeto_sexta_feira():
    pasta = r"C:\SextaFeira"
    arquivos = [
        os.path.join(pasta, "main.py"),
        os.path.join(pasta, "teste_wake.py"),
        os.path.join(pasta, "vts.py"),
        os.path.join(pasta, "ia", "tts.py"),
    ]
    if not os.path.isdir(pasta):
        return f"N\u00e3o encontrei a pasta do projeto: {pasta}."

    arquivos_existentes = [arquivo for arquivo in arquivos if os.path.isfile(arquivo)]
    resultado = abrir_programa(
        "code",
        "Projeto Sexta-feira iniciado. VS Code est\u00e1 abrindo.",
        [pasta, *arquivos_existentes],
    )
    if resultado.startswith("N\u00e3o consegui"):
        return resultado

    resultado_link = abrir_link("https://chatgpt.com", "ChatGPT est\u00e1 abrindo.")
    if resultado_link.startswith("N\u00e3o consegui"):
        return resultado_link
    return "Projeto Sexta-feira iniciado. VS Code e ChatGPT est\u00e3o abrindo."

def _pressionar_tecla_midia(tecla):
    ctypes.windll.user32.keybd_event(
        tecla,
        0,
        0,
        0
    )

    ctypes.windll.user32.keybd_event(
        tecla,
        0,
        2,
        0
    )


def pausar_musica():
    _pressionar_tecla_midia(
        VK_MEDIA_PLAY_PAUSE
    )

    return "Música pausada."


def continuar_musica():
    _pressionar_tecla_midia(
        VK_MEDIA_PLAY_PAUSE
    )

    return "Música continuada."


def proxima_musica():
    _pressionar_tecla_midia(
        VK_MEDIA_NEXT_TRACK
    )

    return "Pulando para a próxima música."


def musica_anterior():
    _pressionar_tecla_midia(
        VK_MEDIA_PREV_TRACK
    )

    time.sleep(0.3)

    _pressionar_tecla_midia(
        VK_MEDIA_PREV_TRACK
    )

    return "Voltando para a música anterior."

# ==========================================================
# ABRIR ARQUIVO / PASTA GENERICAMENTE
# ==========================================================

from .caminhos import (
    PASTA_ASSISTENTE,
    PASTA_DOWNLOADS,
    encontrar_caminho,
    abrir_caminho_generico,
)


def _abrir_local(caminho, descricao):
    try:
        os.startfile(str(caminho))
        return f"Abrindo {descricao}."
    except (OSError, AttributeError) as erro:
        print(f"Erro ao abrir {caminho}: {erro}")
        return f"Não consegui abrir {descricao}."


def abrir_downloads():
    return _abrir_local(PASTA_DOWNLOADS, "a pasta Downloads")


def abrir_assistente():
    return _abrir_local(PASTA_ASSISTENTE, "a pasta do Assistente")


def abrir_main():
    return _abrir_local(PASTA_ASSISTENTE / "main.py", "o main.py")


def abrir_interface():
    return _abrir_local(PASTA_ASSISTENTE / "interface.py", "a interface")
