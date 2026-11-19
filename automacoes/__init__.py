from .apps import (
    abrir_edge,
    abrir_steam,
    abrir_vscode,
    abrir_calculadora,
    abrir_chrome,
    abrir_whatsapp,
    abrir_spotify,
    abrir_discord,
    abrir_rocket_league,
    abrir_breakpoint,
    abrir_stormworks,
    abrir_motorfest,
    abrir_carx_street,
    abrir_pubg,
    abrir_watch_dogs_2,
    abrir_tlauncher,
    pausar_musica,
    continuar_musica,
    proxima_musica,
    musica_anterior,
    abrir_downloads,
    abrir_assistente,
    abrir_main,
    abrir_interface,
    abrir_caminho_generico,
    
)
from .tradutor import traduzir

from .site import criar_site

from .apps import abrir_projeto_sexta_feira

from .gmail import enviar_email

from .web import (
    abrir_youtube,
    abrir_google,
    pesquisar_google,
    pesquisar_youtube,
    pesquisar_spotify,
    extrair_pedido_spotify,
    abrir_video_youtube,
    extrair_consulta_video_youtube,
)

from .sistema import (
    desligar,
    reiniciar
)

from .volume import (
    obter_volume,
    definir_volume,
    aumentar_volume,
    diminuir_volume,
    falar_volume,
    mutar_volume,
    desmutar_volume,
    mutar_spotify,
    desmutar_spotify,
    mutar_discord,
    desmutar_discord
)

from .bluetooth import (
    bluetooth_ligar,
    bluetooth_desligar
)

from .contatos import (
    buscar_contato
)

from .whatsapp import (
    ligar_whatsapp,
    mandar_mensagem,
    desligar_ligacao
)

from .pesquisa import pesquisar_web

from ia.memoria import (
    adicionar_memoria,
    remover_memoria,
    obter_memorias,
    limpar_memoria,
    pesquisar_memoria
)
from automacoes.agenda import iniciar_monitor_agenda

from .tela import (
    apagar_tela,
    ligar_tela,
    bloquear_tela,
    estender_telas,
    duplicar_telas,
    tirar_print,
    obter_ultimo_print
)

from ia.qwen import (
    resumir_pesquisa,
    resolver_pesquisa_memoria,
    responder_com_memoria,
    analisar_imagem
)
import re

from automacoes.alarmes import reconhecer_temporizador

# ==========================================================
# CONFIRMAÇÃO DE AÇÕES PERIGOSAS
# ==========================================================

confirmacao_pendente = None


def pedir_confirmacao(acao, descricao, dados=None):
    global confirmacao_pendente

    confirmacao_pendente = {
        "acao": acao,
        "dados": dados
    }

    return (
        f"Confirma que quer {descricao}? "
        "Responda sim ou não."
    )

def normalizar_texto(texto):
    texto = texto.lower().strip()
    texto = re.sub(r"[.,!?;:]", "", texto)

    # Remove introduções comuns de fala antes de identificar a intenção.
    texto = re.sub(
        r"^(?:(?:jarvis)\s+)?(?:(?:por favor|por gentileza)\s+)?"
        r"(?:(?:você poderia|voce poderia|poderia|você pode|voce pode|"
        r"pode por favor|quero que você|quero que voce|eu gostaria que você|"
        r"eu gostaria que voce|eu quero)\s+)+",
        "",
        texto,
    )

    substituicoes = {
        "voce": "você",
        "memoria": "memória",
        "spotfy": "spotify",
        "spotifi": "spotify",
        "you tube": "youtube",
        "whats app": "whatsapp",
        "wats app": "whatsapp",
        "watsapp": "whatsapp",
        "blutuf": "bluetooth",
        "blu tuf": "bluetooth",
        "sextafeira": "sexta-feira",
        "sexta feira": "sexta-feira",
        "vs-code": "vs code",
        "car x street": "carx street",
        "tradução": "traduzir",
        "traducao": "traduzir",
    }

    for errado, correto in substituicoes.items():
        texto = re.sub(rf"\b{re.escape(errado)}\b", correto, texto)

    # Unifica formas comuns de pedir para abrir/iniciar e pesquisar/buscar.
    sinonimos = {
        "inicie": "iniciar",
        "inicia": "iniciar",
        "inicialize": "iniciar",
        "inicializa": "iniciar",
        "execute": "abrir",
        "executa": "abrir",
        "executar": "abrir",
        "rode": "abrir",
        "rodar": "abrir",
        "busque": "pesquise",
        "busca": "pesquise",
        "buscar": "pesquisar",
        "procure": "pesquise",
        "procura": "pesquise",
        "procurar": "pesquisar",
        "encontre": "pesquise",
        "encontrar": "pesquisar",
        "pesquisa": "pesquise",
        "traduz": "traduza",
        "traduzir": "traduza",
    }
    for errado, correto in sinonimos.items():
        texto = re.sub(rf"\b{errado}\b", correto, texto)

    for palavra in ["por favor", "por gentileza", "porfa", "pfv"]:
        texto = re.sub(rf"\b{re.escape(palavra)}\b", "", texto)

    for palavra in ["hey jarvis", "ei jarvis", "jarvis"]:
        texto = texto.replace(palavra, "")

    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def executar_comando(texto):
    global confirmacao_pendente

    texto = normalizar_texto(texto)

    if confirmacao_pendente is not None:

        # Resposta afirmativa
        if any(
            palavra in texto
            for palavra in [
                "sim",
                "confirmo",
                "confirmar",
                "pode",
                "pode sim",
                "pode fazer",
                "fazer",
            ]
        ):
            pendente = confirmacao_pendente
            confirmacao_pendente = None

            # Nova estrutura com dados
            if isinstance(pendente, dict):
                acao = pendente["acao"]
                dados = pendente.get("dados")
                if dados:
                    return acao(**dados)
                return acao()

            # Compatibilidade com confirmações antigas (callable)
            if callable(pendente):
                return pendente()

        # Resposta negativa
        if any(
            palavra in texto
            for palavra in [
                "não",
                "nao",
                "cancela",
                "cancele",
                "cancelar",
                "deixa",
                "deixa pra la",
                "deixa pra lá",
            ]
        ):
            confirmacao_pendente = None
            return "Ação cancelada."

        # Nenhuma resposta clara: pedir confirmação
        return "Preciso que você responda sim ou não."

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

    # ==========================================================
    # VOLUME - SPOTIFY
    # ==========================================================
    if "spotify" in texto and any(
        palavra in texto for palavra in ["muta", "mutar", "silencia", "silenciar"]
    ):
        return mutar_spotify()

    if "spotify" in texto and any(
        palavra in texto
        for palavra in [
            "desmuta",
            "desmutar",
            "desilencia",
            "desilenciar",
            "tira o mudo",
            "tira do mudo",
        ]
    ):
        return desmutar_spotify()

    # ==========================================================
    # VOLUME - DISCORD
    # ==========================================================
    if "discord" in texto and any(
        palavra in texto for palavra in ["muta", "mutar", "silencia", "silenciar"]
    ):
        return mutar_discord()

    if "discord" in texto and any(
        palavra in texto
        for palavra in [
            "desmuta",
            "desmutar",
            "desilencia",
            "desilenciar",
            "tira o mudo",
            "tira do mudo",
        ]
    ):
        return desmutar_discord()

    # ==========================================================
    # VOLUME GERAL
    # ==========================================================
    if any(
        palavra in texto
        for palavra in [
            "muta",
            "mutar",
            "silencia",
            "silenciar",
            "coloca no mudo",
            "coloca no silêncio",
            "coloca no silencio",
        ]
    ):
        return mutar_volume()

    if any(
        palavra in texto
        for palavra in [
            "desmuta",
            "desmutar",
            "desilencia",
            "desilenciar",
            "tira o mudo",
            "tira do mudo",
            "volta o som",
            "voltar o som",
        ]
    ):
        return desmutar_volume()

    # ==========================================================
    # PESQUISA NO YOUTUBE
    # ==========================================================
    if "youtube" in texto and any(
        palavra in texto for palavra in ["pesquisa", "pesquisar", "pesquise"]
    ):
        pesquisa = texto
        for palavra in [
            "pesquise",
            "pesquisar",
            "pesquisa",
            "no youtube",
            "no youtube por",
            "youtube",
        ]:
            pesquisa = pesquisa.replace(palavra, "")
        pesquisa = pesquisa.strip()
        if pesquisa:
            return pesquisar_youtube(pesquisa)

    # ==========================================================
    # PESQUISA NO SPOTIFY
    # ==========================================================
    if "spotify" in texto and any(
        palavra in texto for palavra in ["pesquisa", "pesquisar", "pesquise"]
    ):
        pesquisa = texto
        for palavra in [
            "pesquise",
            "pesquisar",
            "pesquisa",
            "no spotify",
            "no spotify por",
            "spotify",
            "spotfy",
        ]:
            pesquisa = pesquisa.replace(palavra, "")
        pesquisa = pesquisa.strip()
        if pesquisa:
            return pesquisar_spotify(pesquisa)

    # ==========================================================
    # PESQUISA NO GOOGLE
    # ==========================================================
    if "google" in texto and any(
        palavra in texto for palavra in ["pesquisa", "pesquisar", "pesquise"]
    ):
        pesquisa = texto
        for palavra in [
            "pesquise",
            "pesquisar",
            "pesquisa",
            "no google",
            "no google por",
            "google",
        ]:
            pesquisa = pesquisa.replace(palavra, "")
        pesquisa = pesquisa.strip()
        if pesquisa:
            return pesquisar_google(pesquisa)

    # ==========================================================
    # EDGE
    # ==========================================================
    gatilhos_edge = [
        "abra o edge",
        "abre o edge",
        "abrir o edge",
        "abra edge",
        "abre edge",
        "abrir edge",
    ]
    if any(gatilho in texto for gatilho in gatilhos_edge):
        return abrir_edge()

    # ==========================================================
    # ABRIR CHROME
    # ==========================================================
    if "chrome" in texto and any(
        p in texto for p in ["abrir", "abra", "abre", "iniciar", "inicia"]
    ):
        return abrir_chrome()

    # ==========================================================
    # STEAM
    # ==========================================================
    gatilhos_steam = [
        "abra a steam",
        "abre a steam",
        "abrir a steam",
        "abra steam",
        "abre steam",
        "abrir steam",
    ]
    if any(gatilho in texto for gatilho in gatilhos_steam):
        return abrir_steam()

    # ==========================================================
    # ABRIR VS CODE
    # ==========================================================
    if (
        ("vscode" in texto or "vs code" in texto or "visual studio code" in texto)
        and any(p in texto for p in ["abrir", "abra", "abre", "iniciar", "inicia"])
    ):
        return abrir_vscode()

    # ==========================================================
    # ABRIR CALCULADORA
    # ==========================================================
    if "calculadora" in texto and any(
        p in texto for p in ["abrir", "abra", "abre", "iniciar", "inicia"]
    ):
        return abrir_calculadora()

    # ==========================================================
    # ABRIR WHATSAPP
    # ==========================================================
    if "whatsapp" in texto and any(
        p in texto for p in ["abrir", "abra", "abre", "iniciar", "inicia"]
    ):
        return abrir_whatsapp()

    # ==========================================================
    # ABRIR SPOTIFY
    # ==========================================================
    if (
        "spotify" in texto
        and any(p in texto for p in ["abrir", "abra", "abre", "iniciar", "inicia"])
        and "pesquis" not in texto
    ):
        return abrir_spotify()

    # ==========================================================
    # ABRIR YOUTUBE
    # ==========================================================
    if (
        "youtube" in texto
        and any(p in texto for p in ["abrir", "abra", "abre", "acessar", "acesse"])
        and "pesquis" not in texto
    ):
        return abrir_youtube()

    # ==========================================================
    # ABRIR GOOGLE
    # ==========================================================
    if (
        "google" in texto
        and any(p in texto for p in ["abrir", "abra", "abre", "acessar", "acesse"])
        and "pesquis" not in texto
    ):
        return abrir_google()

    # ==========================================================
    # DESLIGAR / REINICIAR PC
    # ==========================================================
    if "desligar" in texto and ("pc" in texto or "computador" in texto):
        return pedir_confirmacao(desligar, "desligar o computador")

    if "reiniciar" in texto and ("pc" in texto or "computador" in texto):
        return pedir_confirmacao(reiniciar, "reiniciar o computador")

    # ==========================================================
    # JOGOS
    # ==========================================================
    if "breakpoint" in texto and any(
        p in texto for p in ["abrir", "abra", "abre", "iniciar", "inicia"]
    ):
        return abrir_breakpoint()

    if "stormworks" in texto and any(
        p in texto for p in ["abrir", "abra", "abre", "iniciar", "inicia"]
    ):
        return abrir_stormworks()

    if ("motorfest" in texto or "the crew motorfest" in texto) and any(
        p in texto for p in ["abrir", "abra", "abre", "iniciar", "inicia"]
    ):
        return abrir_motorfest()

    if ("carx street" in texto or "car x street" in texto) and any(
        p in texto for p in ["abrir", "abra", "abre", "iniciar", "inicia"]
    ):
        return abrir_carx_street()

    if "pubg" in texto and any(
        p in texto for p in ["abrir", "abra", "abre", "iniciar", "inicia"]
    ):
        return abrir_pubg()

    if ("watch dogs 2" in texto or "watch dogs" in texto) and any(
        p in texto for p in ["abrir", "abra", "abre", "iniciar", "inicia"]
    ):
        return abrir_watch_dogs_2()

    if "tlauncher" in texto and any(
        p in texto for p in ["abrir", "abra", "abre", "iniciar", "inicia"]
    ):
        return abrir_tlauncher()

    # ==========================================================
    # CRIAR SITE
    # ==========================================================
    if "crie um site" in texto or "criar um site" in texto or "cria um site" in texto:
        descricao = texto
        for palavra in ["crie um site", "criar um site", "cria um site"]:
            descricao = descricao.replace(palavra, "")
        descricao = descricao.strip()
        if descricao:
            return criar_site(descricao)

    # ==========================================================
    # DIA DA RESENHA
    # ==========================================================
    gatilhos_resenha = ["hoje e dia de resenha", "hoje é dia de resenha", "dia de resenha"]
    if any(gatilho in texto for gatilho in gatilhos_resenha):
        abrir_discord()
        abrir_rocket_league()
        return "Dia de resenha iniciado. Discord e Rocket League abrindo."

    # ==========================================================
    # MODO ESTUDO
    # ==========================================================
    if "modo estudo" in texto or "modo de estudo" in texto or "perfil estudo" in texto:
        abrir_vscode()
        abrir_chrome()
        return "Modo estudo ativado. VS Code e Chrome foram abertos."

    # ==========================================================
    # MODO FILME
    # ==========================================================
    if "modo filme" in texto or "modo cinema" in texto or "perfil filme" in texto:
        abrir_chrome()
        abrir_spotify()
        definir_volume(20)
        return "Modo filme ativado. Navegador e Spotify abertos. Volume ajustado para 20%."

    # ==========================================================
    # BLUETOOTH
    # ==========================================================
    if texto in [
        "desligar bluetooth",
        "desliga bluetooth",
        "desligue bluetooth",
        "desligar o bluetooth",
        "desliga o bluetooth",
        "desligue o bluetooth",
        "desativar bluetooth",
        "desativa bluetooth",
        "desative bluetooth",
        "desativar o bluetooth",
        "desativa o bluetooth",
        "desative o bluetooth",
    ]:
        return bluetooth_desligar()

    if texto in [
        "ligar bluetooth",
        "liga bluetooth",
        "ligue bluetooth",
        "ligar o bluetooth",
        "liga o bluetooth",
        "ligue o bluetooth",
        "ativar bluetooth",
        "ativa bluetooth",
        "ative bluetooth",
        "ativar o bluetooth",
        "ativa o bluetooth",
        "ative o bluetooth",
    ]:
        return bluetooth_ligar()

    # ==========================================================
    # WHATSAPP - MANDAR MENSAGEM
    # ==========================================================
    gatilhos_mensagem = [
        "manda mensagem para ",
        "manda mensagem pra ",
        "mandar mensagem para ",
        "mandar mensagem pra ",
        "mande mensagem para ",
        "mande mensagem pra ",
        "mandar uma mensagem para ",
        "mandar uma mensagem pra ",
        "mande uma mensagem para ",
        "mande uma mensagem pra ",
        "enviar mensagem para ",
        "enviar mensagem pra ",
        "envia mensagem para ",
        "envia mensagem pra ",
        "envie mensagem para ",
        "envie mensagem pra ",
        "enviar uma mensagem para ",
        "enviar uma mensagem pra ",
        "envia uma mensagem para ",
        "envia uma mensagem pra ",
        "envie uma mensagem para ",
        "envie uma mensagem pra ",
    ]

    gatilho = next((g for g in gatilhos_mensagem if g in texto), None)
    if gatilho:
        resto = texto.split(gatilho, 1)[1].strip()
        if " dizendo " in resto:
            nome, mensagem = resto.split(" dizendo ", 1)
        else:
            partes = resto.split(maxsplit=1)
            if len(partes) < 2:
                return "O que você quer mandar para esse contato?"
            nome = partes[0]
            mensagem = partes[1]

        nome = nome.strip()
        mensagem = mensagem.strip()
        contato = buscar_contato(nome)
        if contato is None:
            return f"Não encontrei o contato {nome}."
        return mandar_mensagem(contato["nome"], contato["telefone"], mensagem)

    # ==========================================================
    # WHATSAPP - DESLIGAR LIGAÇÃO
    # ==========================================================
    if any(
        gatilho in texto
        for gatilho in [
            "desliga a ligação",
            "desligar a ligação",
            "encerra a ligação",
            "encerrar a ligação",
        ]
    ):
        return desligar_ligacao()

    # ==========================================================
    # WHATSAPP - LIGAR PARA CONTATO
    # ==========================================================
    if "liga para " in texto or "ligar para " in texto:
        if "liga para " in texto:
            nome = texto.split("liga para ", 1)[1].strip()
        else:
            nome = texto.split("ligar para ", 1)[1].strip()

        contato = buscar_contato(nome)
        if contato is None:
            return f"Não encontrei o contato {nome}."
        return ligar_whatsapp(contato["nome"], contato["telefone"])

    # ==========================================================
    # PESQUISA WEB + RESUMO
    # ==========================================================
    gatilhos_pesquisa = [
        "pesquise ",
        "pesquisar ",
        "pesquisa ",
        "procure ",
        "procurar ",
        "procura ",
        "busque ",
        "buscar ",
        "busca ",
        "da uma olhada na internet ",
        "dá uma olhada na internet ",
    ]

    gatilho_pesquisa = next((g for g in gatilhos_pesquisa if texto.startswith(g)), None)
    if gatilho_pesquisa:
        pergunta = texto[len(gatilho_pesquisa):].strip()
        for remover in ["na internet ", "na internet", "na web ", "na web", "sobre "]:
            if pergunta.startswith(remover):
                pergunta = pergunta[len(remover):].strip()

        if not pergunta:
            return "O que você quer que eu pesquise?"

        memorias_encontradas = pesquisar_memoria(pergunta)
        if memorias_encontradas:
            print("🧠 Memória encontrada:")
            for memoria_item in memorias_encontradas:
                print("   •", memoria_item)
            pergunta = resolver_pesquisa_memoria(pergunta, memorias_encontradas)
            print("🔎 Termo resolvido:", pergunta)

        resultados = pesquisar_web(pergunta)
        if not resultados:
            return "Não encontrei resultados para essa pesquisa."

        return resumir_pesquisa(pergunta, resultados)

    # ==========================================================
    # MEMÓRIA - SALVAR
    # ==========================================================
    gatilhos_memoria_salvar = [
        "lembre que ",
        "guarde que ",
        "guarda que ",
        "salve que ",
        "salva que ",
        "memorize que ",
        "anote que ",
    ]
    gatilho = next((g for g in gatilhos_memoria_salvar if texto.startswith(g)), None)
    if gatilho:
        texto_memoria = texto[len(gatilho):].strip()
        if not texto_memoria:
            return "O que você quer que eu lembre?"
        adicionar_memoria(texto_memoria)
        return "Certo. Vou lembrar disso."

    # ==========================================================
    # MEMÓRIA - LISTAR
    # ==========================================================
    gatilhos_memoria_listar = [
        "listar",
        "liste",
        "lista",
        "mostrar memória",
        "mostrar memoria",
        "mostra memória",
        "mostra memoria",
        "me mostra a memória",
        "me mostra a memoria",
        "me mostre a memória",
        "me mostre a memoria",
        "listar memória",
        "listar memoria",
        "lista memória",
        "lista memoria",
        "o que você lembra",
        "o que voce lembra",
        "o que você lembra de mim",
        "o que voce lembra de mim",
        "o que você lembra sobre mim",
        "o que voce lembra sobre mim",
        "o que você sabe sobre mim",
        "o que voce sabe sobre mim",
        "o que tem na memória",
        "o que tem na memoria",
        "o que está na memória",
        "o que esta na memoria",
        "o que foi salvo na memória",
        "o que foi salvo na memoria",
        "me fala o que você lembra",
        "me fala o que voce lembra",
        "me diga o que você lembra",
        "me diga o que voce lembra",
    ]
    if any(gatilho in texto for gatilho in gatilhos_memoria_listar):
        memorias_salvas = obter_memorias()
        if not memorias_salvas:
            return "Ainda não tenho nada salvo na memória."
        return "Eu lembro que: " + "; ".join(memorias_salvas)

    # ==========================================================
    # MEMÓRIA - ESQUECER
    # ==========================================================
    gatilhos_memoria_esquecer = [
        "esqueça ",
        "esquece ",
        "esquecer ",
        "apague da memória ",
        "apaga da memória ",
        "remova da memória ",
        "remove da memória ",
        "delete da memória ",
    ]
    gatilho = next((g for g in gatilhos_memoria_esquecer if texto.startswith(g)), None)
    if gatilho:
        texto_memoria = texto[len(gatilho):].strip()
        if not texto_memoria:
            return "O que você quer que eu esqueça?"
        remover_memoria(texto_memoria)
        return "Certo. Esqueci isso."

    # ==========================================================
    # MEMÓRIA - CONSULTAR
    # ==========================================================
    gatilhos_memoria_consulta = [
        "qual é meu",
        "qual meu",
        "quais são meus",
        "quais meus",
        "você lembra qual",
        "voce lembra qual",
        "você lembra do meu",
        "voce lembra do meu",
        "você sabe qual",
        "voce sabe qual",
        "você lembra sobre",
        "voce lembra sobre",
    ]
    if any(gatilho in texto for gatilho in gatilhos_memoria_consulta):
        memorias_encontradas = pesquisar_memoria(texto)
        if memorias_encontradas:
            return responder_com_memoria(texto, memorias_encontradas)

    # ==========================================================
    # TELA
    # ==========================================================
    gatilhos_tela_desligar = [
        "desligar tela",
        "desliga tela",
        "desligue a tela",
        "desligar a tela",
        "apagar tela",
        "apaga tela",
        "apague a tela",
        "apagar a tela",
        "desligar monitor",
        "desliga monitor",
        "desligar o monitor",
        "desliga o monitor",
    ]
    if any(gatilho in texto for gatilho in gatilhos_tela_desligar):
        return apagar_tela()

    gatilhos_tela_ligar = [
        "ligar tela",
        "liga tela",
        "ligue a tela",
        "ligar a tela",
        "acender tela",
        "acende tela",
        "acenda a tela",
        "acender a tela",
        "ligar monitor",
        "liga monitor",
        "ligar o monitor",
        "liga o monitor",
    ]
    if any(gatilho in texto for gatilho in gatilhos_tela_ligar):
        return ligar_tela()

    gatilhos_tela_bloquear = [
        "bloquear tela",
        "bloqueia tela",
        "bloqueie a tela",
        "bloquear a tela",
        "bloquear computador",
        "bloqueia o computador",
        "bloqueie o computador",
        "travar tela",
        "trava tela",
        "trave a tela",
        "travar o computador",
    ]
    if any(gatilho in texto for gatilho in gatilhos_tela_bloquear):
        return bloquear_tela()

    # ==========================================================
    # TELA - ESTENDER / DUPLICAR
    # ==========================================================
    if any(palavra in texto for palavra in ["estend", "extend"]) and any(
        palavra in texto for palavra in ["tela", "telas", "monitor", "monitores"]
    ):
        return estender_telas()

    gatilhos_tela_estender = [
        "estender telas",
        "estende telas",
        "estender tela",
        "estende a tela",
        "estender as telas",
        "extender telas",
        "extender monitor",
        "extender o monitor",
        "extender tela",
        "modo estendido",
        "modo de tela estendido",
    ]
    if any(gatilho in texto for gatilho in gatilhos_tela_estender):
        return estender_telas()

    gatilhos_tela_duplicar = [
        "duplicar telas",
        "duplica telas",
        "duplicar tela",
        "duplicar as telas",
        "duplicar os monitores",
        "modo duplicado",
        "modo de tela duplicado",
    ]
    if any(gatilho in texto for gatilho in gatilhos_tela_duplicar):
        return duplicar_telas()

    # ==========================================================
    # PESQUISA NO YOUTUBE
    # ==========================================================
    gatilhos_youtube = [
        "pesquise no youtube ",
        "pesquisar no youtube ",
        "pesquisa no youtube ",
        "procure no youtube ",
        "procurar no youtube ",
        "procura no youtube ",
        "busque no youtube ",
        "buscar no youtube ",
        "busca no youtube ",
        "pesquise youtube ",
        "pesquisar youtube ",
        "pesquisa youtube ",
    ]
    gatilho_youtube = next((g for g in gatilhos_youtube if texto.startswith(g)), None)
    if gatilho_youtube:
        pesquisa = texto[len(gatilho_youtube):].strip()
        if not pesquisa:
            return "O que você quer pesquisar no YouTube?"
        return pesquisar_youtube(pesquisa)

    # ==========================================================
    # PESQUISA NO SPOTIFY
    # ==========================================================
    gatilhos_spotify = [
        "pesquise no spotify ",
        "pesquisar no spotify ",
        "pesquisa no spotify ",
        "procure no spotify ",
        "procurar no spotify ",
        "procura no spotify ",
        "busque no spotify ",
        "buscar no spotify ",
        "busca no spotify ",
        "pesquise spotify ",
        "pesquisar spotify ",
        "pesquisa spotify ",
    ]
    gatilho_spotify = next((g for g in gatilhos_spotify if texto.startswith(g)), None)
    if gatilho_spotify:
        pesquisa = texto[len(gatilho_spotify):].strip()
        if not pesquisa:
            return "O que você quer pesquisar no Spotify?"
        return pesquisar_spotify(pesquisa)

    # ==========================================================
    # TELA - PRINT
    # ==========================================================
    gatilhos_print = [
        "tirar print",
        "tira print",
        "tirar um print",
        "tira um print",
        "tirar screenshot",
        "tira screenshot",
        "tirar um screenshot",
        "tira um screenshot",
        "capturar tela",
        "captura de tela",
        "fazer print",
        "faz print",
        "fazer um print",
        "faz um print",
    ]
    if any(gatilho in texto for gatilho in gatilhos_print):
        return tirar_print()

    # ==========================================================
    # ANALISAR MINHA TELA
    # ==========================================================
    gatilhos_analisar_tela = [
        "analisa minha tela",
        "analise minha tela",
        "analisar minha tela",
        "analisa a minha tela",
        "analise a minha tela",
        "analisar a minha tela",
        "olha minha tela",
        "olhe minha tela",
        "o que tem na minha tela",
        "o que está na minha tela",
        "o que esta na minha tela",
    ]
    if any(gatilho in texto for gatilho in gatilhos_analisar_tela):
        print()
        print("📸 Capturando tela...")
        tirar_print()
        ultimo_print = obter_ultimo_print()
        if ultimo_print is None:
            return "Não consegui capturar a tela."
        print("🧠 Enviando tela para o Qwen-VL...")
        return analisar_imagem(
            ultimo_print,
            (
                "Analise minha tela cuidadosamente. "
                "Descreva o que está acontecendo e destaque "
                "erros, mensagens ou informações importantes. "
                "Responda de forma clara e direta."
            ),
        )

    # ==========================================================
    # CONTROLE DE MÍDIA
    # ==========================================================
    gatilhos_pausa = ["pausa a música", "pausa musica", "pausar música", "pausar musica", "pausa a musica", "pausar", "pausa"]
    if any(gatilho in texto for gatilho in gatilhos_pausa):
        return pausar_musica()

    gatilhos_continuar = [
        "continua musica",
        "continuar música",
        "continua a música",
        "continuar musica",
        "continua a musica",
        "continuar",
        "continua",
    ]
    if any(gatilho in texto for gatilho in gatilhos_continuar):
        return continuar_musica()

    gatilhos_proxima = [
        "próxima música",
        "proxima musica",
        "próxima",
        "proxima",
        "pula a música",
        "pula musica",
        "pular música",
        "pular musica",
    ]
    if any(gatilho in texto for gatilho in gatilhos_proxima):
        return proxima_musica()

    gatilhos_anterior = [
        "música anterior",
        "musica anterior",
        "volta a música",
        "volta musica",
        "voltar música",
        "voltar musica",
        "volta a musica",
    ]
    if any(gatilho in texto for gatilho in gatilhos_anterior):
        return musica_anterior()

    # ==========================================================
    # ABRIR PASTAS
    # ==========================================================
    gatilhos_downloads = [
        "abrir downloads",
        "abre downloads",
        "abra downloads",
        "abrir a pasta downloads",
        "abre a pasta downloads",
        "abra a pasta downloads",
    ]
    if any(gatilho in texto for gatilho in gatilhos_downloads):
        return abrir_downloads()

    gatilhos_assistente = [
        "abrir assistente",
        "abre assistente",
        "abra assistente",
        "abrir a pasta do assistente",
        "abre a pasta do assistente",
        "abra a pasta do assistente",
        "abrir projeto assistente",
        "abre projeto assistente",
    ]
    if any(gatilho in texto for gatilho in gatilhos_assistente):
        return abrir_assistente()

    # ==========================================================
    # ABRIR ARQUIVOS
    # ==========================================================
    gatilhos_main = [
        "abrir main",
        "abre main",
        "abra main",
        "abrir o main",
        "abre o main",
        "abra o main",
        "abrir main py",
        "abre main py",
        "abra main py",
    ]
    if any(gatilho in texto for gatilho in gatilhos_main):
        return abrir_main()

    gatilhos_interface = [
        "abrir interface",
        "abre interface",
        "abra interface",
        "abrir a interface",
        "abre a interface",
        "abra a interface",
        "abrir interface py",
        "abre interface py",
        "abra interface py",
    ]
    if any(gatilho in texto for gatilho in gatilhos_interface):
        return abrir_interface()

    # ==========================================================
    # ABRIR ARQUIVO GENERICAMENTE
    # ==========================================================
    gatilhos_abrir_arquivo = [
        "abrir o arquivo ",
        "abre o arquivo ",
        "abra o arquivo ",
        "abrir arquivo ",
        "abre arquivo ",
        "abra arquivo ",
        "abrir a pasta ",
        "abre a pasta ",
        "abra a pasta ",
    ]
    gatilho_abrir = next((g for g in gatilhos_abrir_arquivo if texto.startswith(g)), None)
    if gatilho_abrir:
        nome = texto[len(gatilho_abrir):].strip()
        if not nome:
            return "Qual arquivo ou pasta você quer abrir?"
        return abrir_caminho_generico(nome)
    
    # ==========================================================
    # TRADUTOR
    # ==========================================================

    # ==========================================================
# TRADUTOR
# ==========================================================

    como_dizer = re.match(
        r"como (?:se diz|se fala|falar) (.+?) (?:em|no|na) (.+)", texto
    )
    if como_dizer:
        return traduzir(como_dizer.group(1).strip(), como_dizer.group(2).strip())

    if "traduz" in texto or "traduza" in texto or "traduzir" in texto:

        texto_traducao = texto

        for palavra in ["traduza", "traduzir", "traduz", "tradução", "traducao"]:
            texto_traducao = texto_traducao.replace(palavra, "", 1)

        texto_traducao = texto_traducao.replace(" em ", " para ")
        texto_traducao = texto_traducao.replace(" pro ", " para ")
        texto_traducao = texto_traducao.replace(" pra ", " para ")
        texto_traducao = texto_traducao.replace(" ao ", " para ")

        if " para " in texto_traducao:
            partes = texto_traducao.rsplit(" para ", 1)

            texto_original = partes[0].strip()
            idioma = partes[1].strip()

            texto_original = re.sub(r"^(?:a frase|a palavra|a expressão|o texto)\s+", "", texto_original)
            texto_original = re.sub(r"^(?:para|do|da|de)\s+", "", texto_original)

            if texto_original and idioma:
                return traduzir(texto_original, idioma)

        return "Diga o texto e o idioma. Exemplo: traduza bom dia para inglês."
    
    # ==========================================================
    # E-MAIL
    # ==========================================================

    if "enviar email" in texto or "enviar e-mail" in texto:

        partes = texto.split(" para ", 1)

        if len(partes) < 2:
            return "Diga o endereço do destinatário."

        destinatario = partes[1].strip()

        if " dizendo " in destinatario:
            destinatario, mensagem = destinatario.split(" dizendo ", 1)

        elif " com a mensagem " in destinatario:
            destinatario, mensagem = destinatario.split(" com a mensagem ", 1)

        else:
            return "Diga também a mensagem. Exemplo: enviar email para exemplo@gmail.com dizendo olá."

        destinatario = destinatario.strip()
        mensagem = mensagem.strip()

        if not destinatario or not mensagem:
            return "Preciso do destinatário e da mensagem."

        return pedir_confirmacao(
            enviar_email,
            f"enviar o e-mail para {destinatario} com a mensagem: {mensagem}",
            {
                "destinatario": destinatario,
                "assunto": "Mensagem enviada pelo Jarvis",
                "mensagem": mensagem,
            },
        )

    # ==========================================================
    # TEMPORIZADOR / TIMER
    # ==========================================================
    resultado_temporizador = reconhecer_temporizador(texto)

    if resultado_temporizador is not None:
        return resultado_temporizador

    return None
