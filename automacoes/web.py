import webbrowser
import os
import re
import subprocess
import time
import ctypes
from urllib.parse import quote


def abrir_youtube():
    webbrowser.open("https://www.youtube.com")
    return "Abrindo o YouTube."


def abrir_google():
    webbrowser.open("https://www.google.com")
    return "Abrindo o Google."


def pesquisar_google(pesquisa):
    url = "https://www.google.com/search?q=" + quote(pesquisa)
    webbrowser.open(url)
    return f"Pesquisando {pesquisa} no Google."


def pesquisar_youtube(pesquisa):
    url = "https://www.youtube.com/results?search_query=" + quote(pesquisa)
    webbrowser.open(url)
    return f"Pesquisando {pesquisa} no YouTube."


def abrir_video_youtube(pesquisa):
    """Abre o primeiro resultado de vídeo para a consulta no YouTube."""
    pesquisa = pesquisa.strip()
    if not pesquisa:
        return "Diga qual video voce quer abrir no YouTube."

    url_busca = "https://www.youtube.com/results?search_query=" + quote(pesquisa)
    navegador = None
    link_video = None
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.edge.options import Options
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        opcoes = Options()
        opcoes.add_argument("--headless")
        opcoes.add_argument("--disable-gpu")
        opcoes.add_argument("--window-size=1280,900")
        navegador = webdriver.Edge(options=opcoes)
        navegador.get(url_busca)
        resultados = WebDriverWait(navegador, 12).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "ytd-video-renderer a#video-title")
            )
        )
        for resultado in resultados:
            candidato = resultado.get_attribute("href")
            if candidato and "youtube.com/watch" in candidato:
                link_video = candidato
                break
    except Exception as erro:
        print(f"Erro ao localizar video no YouTube: {erro}")
    finally:
        if navegador is not None:
            try:
                navegador.quit()
            except Exception as erro:
                print(f"Erro ao encerrar a busca do YouTube: {erro}")

    if link_video:
        webbrowser.open(link_video)
        return f"Abrindo o primeiro video encontrado para {pesquisa} no YouTube."

    webbrowser.open(url_busca)
    return f"Nao consegui localizar um video automaticamente; abri a busca por {pesquisa}."


def pesquisar_spotify(pesquisa):
    pesquisa = pesquisa.strip()
    if not pesquisa:
        return "Diga o nome da música, artista ou podcast para pesquisar no Spotify."

    consulta_codificada = quote(pesquisa)
    uri = "spotify:search:" + consulta_codificada
    url = "https://open.spotify.com/search/" + consulta_codificada

    try:
        os.startfile(uri)
    except (OSError, AttributeError):
        executavel = r"C:\Users\User\AppData\Roaming\Spotify\Spotify.exe"
        try:
            subprocess.Popen([executavel, uri])
        except OSError:
            webbrowser.open(url)

    return f"Pesquisando {pesquisa} no Spotify."


def _titulo_janela(hwnd, user32):
    tamanho = user32.GetWindowTextLengthW(hwnd)
    if tamanho <= 0:
        return ""
    buffer = ctypes.create_unicode_buffer(tamanho + 1)
    user32.GetWindowTextW(hwnd, buffer, tamanho + 1)
    return buffer.value


class _KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.c_size_t),
    ]


class _MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long), ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong), ("dwExtraInfo", ctypes.c_size_t),
    ]


class _HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong), ("wParamL", ctypes.c_ushort), ("wParamH", ctypes.c_ushort)]


class _INPUTUNION(ctypes.Union):
    _fields_ = [("mi", _MOUSEINPUT), ("ki", _KEYBDINPUT), ("hi", _HARDWAREINPUT)]


class _INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("union", _INPUTUNION)]


def _evento_teclado(user32, tecla=0, scan=0, flags=0):
    entrada = _INPUT(
        type=1,
        union=_INPUTUNION(ki=_KEYBDINPUT(tecla, scan, flags, 0, 0)),
    )
    enviados = user32.SendInput(1, ctypes.byref(entrada), ctypes.sizeof(_INPUT))
    if enviados != 1:
        raise OSError("O Windows nao aceitou a entrada de teclado.")


def _pressionar_tecla(user32, tecla):
    _evento_teclado(user32, tecla=tecla)
    _evento_teclado(user32, tecla=tecla, flags=0x0002)


def _digitar_texto(user32, texto):
    for caractere in texto:
        codigos = caractere.encode("utf-16-le")
        for indice in range(0, len(codigos), 2):
            unidade = int.from_bytes(codigos[indice:indice + 2], "little")
            _evento_teclado(user32, scan=unidade, flags=0x0004)
            _evento_teclado(user32, scan=unidade, flags=0x0004 | 0x0002)


def _focar_janela_spotify():
    if os.name != "nt":
        return None

    user32 = ctypes.windll.user32
    janelas = []
    janela_ativa = user32.GetForegroundWindow()
    if "spotify" in _titulo_janela(janela_ativa, user32).casefold():
        return user32, janela_ativa

    callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    @callback_type
    def localizar(hwnd, _parametro):
        if user32.IsWindowVisible(hwnd) and "spotify" in _titulo_janela(hwnd, user32).casefold():
            janelas.append(hwnd)
        return True

    user32.EnumWindows(localizar, 0)
    if not janelas:
        return None

    user32.ShowWindow(janelas[0], 5)
    user32.SetForegroundWindow(janelas[0])
    time.sleep(0.2)
    janela_ativa = user32.GetForegroundWindow()
    if "spotify" not in _titulo_janela(janela_ativa, user32).casefold():
        return None
    return user32, janela_ativa


def pesquisar_e_tocar_spotify(pesquisa, atraso=6):
    """Abre o app, espera sua inicializacao e toca a primeira sugestao via Ctrl+K/Enter."""
    pesquisa = pesquisa.strip()
    if not pesquisa:
        return "Diga o nome da musica ou artista que quer tocar."

    from .apps import abrir_spotify
    resultado_abertura = abrir_spotify()
    if resultado_abertura.startswith("N"):
        return resultado_abertura

    time.sleep(atraso)
    janela = _focar_janela_spotify()
    if janela is None:
        return "O Spotify foi chamado, mas nao consegui focar a janela para selecionar a musica."

    user32, _hwnd = janela
    try:
        # Ctrl+K abre a busca rapida do cliente Spotify.
        _evento_teclado(user32, tecla=0x11)
        try:
            _pressionar_tecla(user32, 0x4B)
        finally:
            _evento_teclado(user32, tecla=0x11, flags=0x0002)
        time.sleep(0.25)
        _digitar_texto(user32, pesquisa)
        time.sleep(0.8)
        _pressionar_tecla(user32, 0x0D)
        return f"Busquei {pesquisa} e enviei Enter para iniciar a faixa no Spotify."
    except OSError as erro:
        print(f"Erro ao enviar a busca ao Spotify: {erro}")
        return f"Abri o Spotify, mas nao consegui selecionar {pesquisa}."


def extrair_consulta_spotify(texto):
    """Extrai o termo de buscas faladas ou pedidos de reprodução no Spotify."""
    texto = texto.casefold().strip()
    if not re.search(r"\bspotify\b", texto):
        return None

    acoes = (
        "toque", "tocar", "toca", "tocando", "reproduza", "reproduzir",
        "reproduz", "coloque", "coloca", "pesquise", "pesquisar", "pesquisa",
        "busque", "buscar", "procure", "procurar", "encontre", "encontrar",
    )
    padrao = r"\b(" + "|".join(acoes) + r")\b"
    correspondencia = re.search(padrao, texto)
    if not correspondencia:
        return None

    consulta = texto[correspondencia.end():]
    consulta = re.sub(
        r"\b(?:no aplicativo do spotify|no aplicativo spotify|no app do spotify|"
        r"no app spotify|no spotify|na spotify|spotify)\b",
        " ",
        consulta,
    )
    consulta = re.sub(r"\b(?:a musica|uma musica|musica|a faixa|a canção)\b", " ", consulta)
    return " ".join(consulta.split())


def extrair_pedido_spotify(texto):
    consulta = extrair_consulta_spotify(texto)
    if consulta is None:
        return None
    verbos_reproducao = (
        "toque", "tocar", "toca", "reproduza", "reproduzir", "reproduz",
    )
    acao = "play" if re.search(
        r"\b(" + "|".join(verbos_reproducao) + r")\b", texto.casefold()
    ) else "search"
    return acao, consulta


def extrair_consulta_video_youtube(texto):
    """Extrai o conteudo pedido para abrir um video direto no YouTube."""
    texto = texto.casefold().strip()
    if not re.search(r"\byoutube\b", texto):
        return None

    acoes_reproducao = (
        "toque", "tocar", "toca", "reproduza", "reproduzir", "reproduz",
        "assista", "assistir", "assiste", "veja", "ver",
    )
    acao = re.search(r"\b(" + "|".join(acoes_reproducao) + r")\b", texto)
    marcador_video = re.search(r"\bv[i\u00ed]deo\b|\bclipe\b", texto)

    if acao:
        inicio = acao.end()
    elif marcador_video:
        inicio = marcador_video.end()
    else:
        return None

    consulta = texto[inicio:]
    consulta = re.sub(r"\b(?:no youtube|no you tube|youtube|pelo youtube)\b", " ", consulta)
    consulta = re.sub(
        r"^\s*(?:(?:um|uma|o|a)\s+)?(?:(?:video|v[i\u00ed]deo|clipe|"
        r"musica|m[u\u00fa]sica|faixa)\s+)?(?:de|do|da)\s+",
        "",
        consulta,
    )
    consulta = re.sub(r"^\s*(?:(?:um|uma|o|a)\s+)?(?:video|v[i\u00ed]deo|clipe|musica|m[u\u00fa]sica|faixa)\s+", "", consulta)
    return " ".join(consulta.split())
