import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

import threading
import math
from concurrent.futures import ThreadPoolExecutor

import os
import logging
import hashlib
import hmac

from automacoes import (
    executar_comando,
    tirar_print,
    obter_ultimo_print,
)
from automacoes.perfil_publico import executar_comando_publico

from ia.qwen import (
    perguntar,
    analisar_imagem,
)

from ia.tts import falar

from audio.gravacao import gravar_audio, gravar_aula_teams, classificar_comando_aula, gravar_aula_continua
from ia.whisper import transcrever

# ==========================================================
# LOG DO JARVIS
# ==========================================================

PASTA_LOGS = os.path.join(
    os.path.dirname(__file__),
    "logs",
)

os.makedirs(PASTA_LOGS, exist_ok=True)

ARQUIVO_LOG = os.path.join(
    PASTA_LOGS,
    "jarvis.log",
)

logging.basicConfig(
    filename=ARQUIVO_LOG,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

LARGURA = 1000
ALTURA = 700
HASH_SENHA_PERFIL = "88f964f6d945d6cf01603f3353fb18e597e843df0adb6ee376c0c2dd22dee453"


class JarvisInterface:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jarvis")
        self.root.geometry("1200x750")
        self.root.minsize(900, 600)

        try:
            self.root.state("zoomed")
        except Exception:
            pass

        self.executor = ThreadPoolExecutor(max_workers=4)
        self.tts_lock = threading.Lock()
        self.tarefas_ativas = 0
        self.tarefas_lock = threading.Lock()
        self.gravacao_aula_thread = None
        self.gravacao_aula_stop = None
        self.perfil_atual = "P" + chr(250) + "blico"

        self.criar_estilo()
        self.criar_interface()
        self.atualizar_status("Pronto")

    # ======================================================
    # ESTILO
    # ======================================================

    def criar_estilo(self):
        try:
            ttk.Style().theme_use("clam")
        except Exception:
            pass

    def criar_interface(self):
        sidebar_bg = "#f1f0eb"
        main_bg = "#fbfaf8"
        texto = "#282724"
        suave = "#85837c"
        painel = "#ffffff"

        self.root.configure(bg=main_bg)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0, minsize=238)
        self.root.grid_columnconfigure(1, weight=1)

        sidebar = tk.Frame(self.root, bg=sidebar_bg, width=238)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(4, weight=1)
        sidebar.grid_columnconfigure(0, weight=1)

        marca = tk.Frame(sidebar, bg=sidebar_bg)
        marca.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 17))
        logo = tk.Canvas(marca, width=29, height=29, bg=sidebar_bg, highlightthickness=0)
        logo.pack(side="left", padx=(0, 10))
        self._pilula(logo, 1, 1, 28, 28, 8, "#191918")
        logo.create_text(14, 14, text="N", fill="#ffffff", font=("Segoe UI", 11, "bold"))
        tk.Label(marca, text="Nexo AI", font=("Segoe UI", 10, "bold"),
                 fg=texto, bg=sidebar_bg).pack(side="left")

        self.botao_nova_conversa = tk.Canvas(
            sidebar,
            width=218,
            height=40,
            bg=sidebar_bg,
            highlightthickness=0,
            cursor="hand2",
        )
        self.botao_nova_conversa.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 24))
        self._desenhar_botao_nova_conversa()
        self.botao_nova_conversa.bind("<Button-1>", lambda evento: self.nova_conversa())
        self.botao_nova_conversa.bind(
            "<Enter>", lambda evento: self._desenhar_botao_nova_conversa(hover=True)
        )
        self.botao_nova_conversa.bind(
            "<Leave>", lambda evento: self._desenhar_botao_nova_conversa()
        )

        tk.Label(sidebar, text="RECENTES", font=("Segoe UI", 7, "bold"),
                 fg="#99968e", bg=sidebar_bg, anchor="w").grid(
            row=2, column=0, sticky="ew", padx=20, pady=(0, 8)
        )
        self.recentes_vazio = tk.Label(
            sidebar,
            text="Suas conversas aparecerao aqui.",
            font=("Segoe UI", 8),
            fg=suave,
            bg=sidebar_bg,
            anchor="w",
            wraplength=195,
            justify="left",
        )
        self.recentes_vazio.grid(row=3, column=0, sticky="new", padx=20, pady=4)

        tk.Frame(sidebar, bg="#dfddd6", height=1).grid(
            row=5, column=0, sticky="ew", padx=10, pady=(0, 0)
        )
        usuario = tk.Frame(sidebar, bg=sidebar_bg)
        usuario.grid(row=6, column=0, sticky="ew", padx=16, pady=14)
        avatar = tk.Canvas(usuario, width=32, height=32, bg=sidebar_bg, highlightthickness=0)
        avatar.pack(side="left", padx=(0, 10))
        avatar.create_oval(1, 1, 31, 31, fill="#dedbd2", outline="")
        avatar.create_text(16, 16, text="M", fill="#68665f", font=("Segoe UI", 8, "bold"))
        dados_usuario = tk.Frame(usuario, bg=sidebar_bg)
        dados_usuario.pack(side="left")
        tk.Label(dados_usuario, text="Mateus", font=("Segoe UI", 8, "bold"),
                 fg=texto, bg=sidebar_bg, anchor="w").pack(anchor="w")
        tk.Label(dados_usuario, text="Jarvis local", font=("Segoe UI", 7),
                 fg=suave, bg=sidebar_bg, anchor="w").pack(anchor="w", pady=(2, 0))

        principal = tk.Frame(self.root, bg=main_bg)
        principal.grid(row=0, column=1, sticky="nsew")
        principal.grid_rowconfigure(1, weight=1)
        principal.grid_columnconfigure(0, weight=1)

        cabecalho = tk.Frame(principal, bg=main_bg, height=52)
        cabecalho.grid(row=0, column=0, sticky="ew")
        cabecalho.grid_propagate(False)
        self.status_label = tk.Label(
            cabecalho, text="Pronto", font=("Segoe UI", 8), fg=suave, bg=main_bg
        )
        self.status_label.pack(side="right", padx=(8, 17))
        self.botao_perfil = tk.Canvas(
            cabecalho,
            width=132,
            height=34,
            bg=main_bg,
            highlightthickness=0,
            cursor="hand2",
        )
        self._pilula(self.botao_perfil, 1, 1, 131, 33, 16, painel, "#e6e3dc", 1)
        self.texto_perfil_id = self.botao_perfil.create_text(
            66, 17, text=self._texto_perfil(), fill="#59574f", font=("Segoe UI", 8)
        )
        self.botao_perfil.bind("<Button-1>", self.alterar_perfil)
        self.botao_perfil.pack(side="right", padx=(0, 16), pady=8)

        conversa = tk.Frame(principal, bg=main_bg)
        conversa.grid(row=1, column=0, sticky="nsew")
        conversa.grid_rowconfigure(0, weight=1)
        conversa.grid_columnconfigure(0, weight=1)

        self.chat = tk.Text(
            conversa,
            bg=main_bg,
            fg=texto,
            insertbackground=texto,
            font=("Segoe UI", 10),
            wrap="word",
            relief="flat",
            borderwidth=0,
            padx=100,
            pady=25,
            spacing1=5,
            spacing3=8,
            state="disabled",
            cursor="arrow",
            selectbackground="#dedbd2",
        )
        self.chat.grid(row=0, column=0, sticky="nsew")
        self.chat.tag_configure("autor_usuario", font=("Segoe UI", 9, "bold"),
                                foreground="#5d5a53", spacing1=16, spacing3=4)
        self.chat.tag_configure("autor_jarvis", font=("Segoe UI", 9, "bold"),
                                foreground="#292825", spacing1=16, spacing3=4)
        self.chat.tag_configure("mensagem", font=("Segoe UI", 10), foreground=texto,
                                lmargin1=0, lmargin2=0, spacing3=10)
        self.chat_scroll = ttk.Scrollbar(conversa, orient="vertical", command=self.chat.yview)
        self.chat.configure(yscrollcommand=self.chat_scroll.set)
        self.chat_scroll.grid(row=0, column=1, sticky="ns")
        self.chat_visible = True

        self.boas_vindas = tk.Frame(conversa, bg=main_bg)
        self.boas_vindas.place(relx=0.5, rely=0.47, anchor="center")
        icone = tk.Canvas(self.boas_vindas, width=36, height=36, bg=main_bg, highlightthickness=0)
        icone.pack(anchor="w", pady=(0, 15))
        self._pilula(icone, 1, 1, 35, 35, 9, "#191918")
        icone.create_text(18, 18, text="N", fill="#ffffff", font=("Segoe UI", 13, "bold"))
        tk.Label(self.boas_vindas, text="Ol" + chr(225) + ", Mateus",
                 font=("Segoe UI", 9), fg=suave, bg=main_bg, anchor="w").pack(anchor="w")
        tk.Label(self.boas_vindas, text="Como posso ajudar hoje?",
                 font=("Segoe UI", 25), fg=texto, bg=main_bg, anchor="w").pack(
            anchor="w", pady=(5, 8)
        )
        tk.Label(
            self.boas_vindas,
            text="Converse, crie e descubra novas ideias. Escreva, fale ou mostre o que\nest" + chr(225) + " pensando.",
            font=("Segoe UI", 9), fg=suave, bg=main_bg, justify="left", anchor="w",
        ).pack(anchor="w")

        rodape = tk.Frame(principal, bg=main_bg)
        rodape.grid(row=2, column=0, sticky="ew", padx=125, pady=(8, 5))
        rodape.grid_columnconfigure(0, weight=1)
        self.entrada_frame = tk.Canvas(rodape, height=54, bg=main_bg, highlightthickness=0)
        self.entrada_frame.grid(row=0, column=0, sticky="ew")
        self.entrada = tk.Entry(
            self.entrada_frame, bg=painel, fg=texto, insertbackground=texto,
            font=("Segoe UI", 9), relief="flat", borderwidth=0,
        )
        self.entrada.insert(0, "Escreva sua mensagem...")
        self.entrada.configure(fg="#aaa79f")
        self.entrada.bind("<FocusIn>", lambda evento: self.limpar_placeholder())
        self.entrada.bind("<Return>", lambda evento: self.enviar_texto())
        self.entrada_window = self.entrada_frame.create_window(
            55, 27, window=self.entrada, anchor="w", width=250, height=30
        )

        self.botao_print = tk.Canvas(self.entrada_frame, width=34, height=34,
                                     bg=painel, highlightthickness=0, cursor="hand2")
        self.botao_print.create_text(17, 17, text=chr(128247), font=("Segoe UI Emoji", 13), fill="#55534d")
        self.botao_print.bind("<Button-1>", lambda evento: self.iniciar_analise_print())
        self.botao_print_window = self.entrada_frame.create_window(
            27, 27, window=self.botao_print, anchor="center"
        )

        self.botao_voz = tk.Canvas(self.entrada_frame, width=34, height=34,
                                   bg=painel, highlightthickness=0, cursor="hand2")
        self.botao_voz.create_text(17, 17, text=chr(127908), font=("Segoe UI Emoji", 13), fill="#55534d")
        self.botao_voz.bind("<Button-1>", lambda evento: self.iniciar_voz())
        self.botao_voz_window = self.entrada_frame.create_window(
            0, 27, window=self.botao_voz, anchor="center"
        )

        self.botao_enviar = tk.Canvas(self.entrada_frame, width=34, height=34,
                                      bg=painel, highlightthickness=0, cursor="hand2")
        self.botao_enviar.create_oval(1, 1, 33, 33, fill="#d8d5ce", outline="")
        self.botao_enviar.create_text(17, 16, text=chr(8593), fill="#ffffff",
                                      font=("Segoe UI", 15, "bold"))
        self.botao_enviar.bind("<Button-1>", lambda evento: self.enviar_texto())
        self.botao_enviar_window = self.entrada_frame.create_window(
            0, 27, window=self.botao_enviar, anchor="center"
        )
        self.entrada_frame.bind("<Configure>", self._desenhar_compositor)
        self._desenhar_compositor()

        ferramentas = tk.Frame(rodape, bg=main_bg)
        ferramentas.grid(row=1, column=0, sticky="w", pady=(3, 0))
        self.botao_aula = tk.Button(
            ferramentas, text="Gravar aula", command=self.iniciar_aula_teams,
            bg=main_bg, fg="#77746d", activebackground="#efeee9",
            activeforeground=texto, relief="flat", font=("Segoe UI", 7),
            padx=5, pady=2, cursor="hand2",
        )
        self.botao_aula.pack(side="left")
        self.botao_aula.configure(state="disabled")
        self.botao_print.configure(state="disabled")

        tk.Label(
            principal,
            text="A Nexo pode cometer erros. Verifique informacoes importantes.",
            font=("Segoe UI", 7), fg="#aaa79f", bg=main_bg,
        ).grid(row=3, column=0, pady=(0, 7))

    @staticmethod
    def _pilula(canvas, x1, y1, x2, y2, raio, preenchimento, contorno=None, largura=1):
        pontos = []
        cantos = (
            (x2 - raio, y1 + raio, -90, 0),
            (x2 - raio, y2 - raio, 0, 90),
            (x1 + raio, y2 - raio, 90, 180),
            (x1 + raio, y1 + raio, 180, 270),
        )
        for cx, cy, inicio, fim in cantos:
            for passo in range(9):
                angulo = math.radians(inicio + (fim - inicio) * passo / 8)
                pontos.extend((cx + raio * math.cos(angulo),
                               cy + raio * math.sin(angulo)))
        return canvas.create_polygon(
            *pontos,
            smooth=False,
            fill=preenchimento,
            outline=contorno or preenchimento,
            width=largura,
            tags=("forma",),
        )

    def _texto_perfil(self):
        nome = "P" + chr(250) + "blico" if self.perfil_atual == ("P" + chr(250) + "blico") else "Privado"
        icone = chr(127760) if self.perfil_atual == ("P" + chr(250) + "blico") else chr(128274)
        return f"{icone}  {nome}  v"

    def _desenhar_botao_nova_conversa(self, hover=False):
        canvas = self.botao_nova_conversa
        canvas.delete("all")
        preenchimento = "#e9e7e1" if hover else "#faf9f6"
        self._pilula(canvas, 1, 1, 217, 39, 10, preenchimento, "#e4e1d9", 1)
        canvas.create_text(17, 20, text=chr(9998), anchor="w", fill="#646159",
                           font=("Segoe UI Symbol", 11))
        canvas.create_text(38, 20, text="Nova conversa", anchor="w", fill="#34332f",
                           font=("Segoe UI", 9))

    def _desenhar_compositor(self, evento=None):
        if not hasattr(self, "entrada_frame") or not hasattr(self, "botao_enviar_window"):
            return
        canvas = self.entrada_frame
        largura = max(canvas.winfo_width(), 250)
        altura = max(canvas.winfo_height(), 54)
        canvas.delete("forma")
        self._pilula(canvas, 1, 1, largura - 1, altura - 1, altura / 2,
                     "#ffffff", "#e3e0d9", 1)
        canvas.tag_lower("forma")
        canvas.coords(self.entrada_window, 55, altura / 2)
        canvas.itemconfigure(self.entrada_window, width=max(80, largura - 155))
        canvas.coords(self.botao_print_window, 27, altura / 2)
        canvas.coords(self.botao_voz_window, largura - 77, altura / 2)
        canvas.coords(self.botao_enviar_window, largura - 31, altura / 2)

    def limpar_placeholder(self):
        if self.entrada.get() == "Escreva sua mensagem...":
            self.entrada.delete(0, "end")
        self.entrada.configure(fg="#282724")

    def alterar_perfil(self, evento=None):
        perfil_publico_atual = self.perfil_atual == ("P" + chr(250) + "blico")
        senha = simpledialog.askstring(
            "Trocar perfil",
            "Digite a senha para trocar de perfil:",
            show="*",
            parent=self.root,
        )
        senha_valida = senha is not None and hmac.compare_digest(
            hashlib.sha256(senha.encode("utf-8")).hexdigest(),
            HASH_SENHA_PERFIL,
        )
        if not senha_valida:
            if senha is not None:
                messagebox.showerror(
                    "Senha incorreta",
                    "A senha informada nao esta correta.",
                    parent=self.root,
                )
            return

        publico = not perfil_publico_atual
        self.perfil_atual = ("P" + chr(250) + "blico") if publico else "Privado"
        estado = "disabled" if publico else "normal"
        self.botao_aula.configure(state=estado)
        self.botao_print.configure(state=estado)
        self.botao_perfil.itemconfigure(self.texto_perfil_id, text=self._texto_perfil())
        self.atualizar_status(("Perfil p" + chr(250) + "blico") if publico else "Perfil privado")

    def atualizar_status(self, estado, descricao=""):
        if not hasattr(self, "status_label"):
            return
        texto = estado.upper()
        if "ERRO" in texto:
            cor = "#f28b82"
        elif "OUVINDO" in texto or "TRANSCR" in texto:
            cor = "#a8c7fa"
        elif "PENSANDO" in texto or "EXECUTANDO" in texto or "PROCESSANDO" in texto:
            cor = "#e3c27a"
        else:
            cor = "#a0a0a0"
        self.root.after(0, lambda: self.status_label.configure(text=estado, fg=cor))

    def atualizar_estado(self, estado):
        texto = estado.upper()
        if "ERRO" in texto:
            status = "Erro"
        elif "OUVINDO" in texto:
            status = "Ouvindo..."
        elif "TRANSCR" in texto:
            status = "Transcrevendo..."
        elif "PENSANDO" in texto:
            status = "Pensando..."
        elif "EXECUTANDO" in texto:
            status = "Executando..."
        elif "FALANDO" in texto:
            status = "Falando..."
        elif "PROCESSANDO" in texto:
            status = "Processando"
        else:
            status = "Pronto"
        self.atualizar_status(status)

    def nova_conversa(self):
        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")
        self.chat_visible = True
        self.boas_vindas.place(relx=0.5, rely=0.47, anchor="center")
        self.entrada.delete(0, "end")
        self.entrada.focus_set()
        self.atualizar_status("Nova conversa")

    def iniciar_tarefa(self):
        with self.tarefas_lock:
            self.tarefas_ativas += 1
            tarefas = self.tarefas_ativas

        self.atualizar_estado(f"🟡 PROCESSANDO ({tarefas})")

    def finalizar_tarefa(self):
        with self.tarefas_lock:
            self.tarefas_ativas = max(0, self.tarefas_ativas - 1)
            tarefas = self.tarefas_ativas

        if tarefas == 0:
            self.atualizar_estado("🟢 ONLINE")
        else:
            self.atualizar_estado(f"🟡 PROCESSANDO ({tarefas})")

    # ======================================================
    # CHAT
    # ======================================================

    def adicionar_mensagem(self, autor, mensagem):
        logging.info("TEXTO | %s", mensagem)
        if self.chat_visible:
            self.boas_vindas.place_forget()
            self.chat_visible = False

        self.chat.configure(state="normal")
        if autor == ("VOC" + chr(202)):
            nome = "Voc" + chr(234)
            tag_autor = "autor_usuario"
        else:
            nome = "Jarvis"
            tag_autor = "autor_jarvis"

        self.chat.insert("end", nome + "\n", tag_autor)
        self.chat.insert("end", str(mensagem) + "\n", "mensagem")
        self.chat.see("end")
        self.chat.configure(state="disabled")

    # ======================================================
    # TEXTO
    # ======================================================

    def enviar_texto(self):
        texto = self.entrada.get().strip()

        if not texto or texto == "Escreva sua mensagem...":
            return

        self.entrada.delete(0, "end")
        self.adicionar_mensagem("VOCÊ", texto)
        self.iniciar_tarefa()
        perfil = self.perfil_atual
        self.executor.submit(self.processar_texto, texto, perfil)

    # ======================================================
    # PROCESSAR TEXTO
    # ======================================================

    def processar_texto(self, texto, perfil=None):
        try:
            perfil = perfil or self.perfil_atual
            if perfil == "Público":
                resultado = executar_comando_publico(texto)
                resposta = resultado if resultado else perguntar(texto)

                self.root.after(
                    0,
                    lambda r=resposta: self.adicionar_mensagem("JARVIS", r),
                )
                self.atualizar_estado("🔊 FALANDO")
                with self.tts_lock:
                    falar(resposta)
                return

            comando_aula = classificar_comando_aula(texto)

            if comando_aula == "iniciar":
                if self.gravacao_aula_thread is not None and self.gravacao_aula_thread.is_alive():
                    self.root.after(0, lambda: self.adicionar_mensagem("JARVIS", "A gravação da aula já está ativa."))
                    return

                self.root.after(0, lambda: self.adicionar_mensagem("JARVIS", "Gravação da aula iniciada. Diga 'parar gravação da aula' para encerrar."))
                self.gravacao_aula_stop = threading.Event()
                self.gravacao_aula_thread = threading.Thread(
                    target=gravar_aula_continua,
                    args=(r"C:\Users\User\Downloads\Assistente\aula_teams.wav", self.gravacao_aula_stop),
                    daemon=True,
                )
                self.gravacao_aula_thread.start()
                return

            if comando_aula == "parar":
                if self.gravacao_aula_thread is not None and self.gravacao_aula_thread.is_alive():
                    self.root.after(0, lambda: self.adicionar_mensagem("JARVIS", "Encerrando gravação da aula..."))
                    self.gravacao_aula_stop.set()
                    self.gravacao_aula_thread.join(timeout=15)
                    caminho = r"C:\Users\User\Downloads\Assistente\aula_teams.wav"
                    transcricao = transcrever(caminho)
                    resumo = perguntar(
                        "Você é um assistente acadêmico brasileiro. "
                        "Resuma esta aula em português do Brasil, em tópicos, conceitos e tarefas.\n\n"
                        f"TRANSCRIÇÃO:\n{transcricao}"
                    )
                    self.root.after(0, lambda r=resumo: self.adicionar_mensagem("JARVIS", r),)
                    with self.tts_lock:
                        falar(resumo)
                    self.gravacao_aula_thread = None
                    self.gravacao_aula_stop = None
                    return

                self.root.after(0, lambda: self.adicionar_mensagem("JARVIS", "Não há gravação da aula ativa."))
                return

            self.atualizar_estado("⚙️ EXECUTANDO")

            resultado = executar_comando(texto)

            if resultado:
                logging.info("COMANDO | %s | RESULTADO | %s", texto, resultado)
                resposta = resultado
            else:
                logging.info("QWEN | %s", texto)
                self.atualizar_estado("🧠 PENSANDO")
                resposta = perguntar(texto)

            self.root.after(
                0,
                lambda r=resposta: self.adicionar_mensagem("JARVIS", r),
            )

            self.atualizar_estado("🔊 FALANDO")

            with self.tts_lock:
                falar(resposta)

        except Exception as erro:
            mensagem = f"Erro ao processar comando:\n{erro}"
            self.root.after(0, lambda: self.adicionar_mensagem("JARVIS", mensagem))
            self.atualizar_estado("🔴 ERRO")
        finally:
            self.finalizar_tarefa()

    # ======================================================
    # VOZ
    # ======================================================

    def iniciar_voz(self):
        self.iniciar_tarefa()
        self.executor.submit(self.processar_voz)

    def processar_voz(self):
        perfil = self.perfil_atual
        try:
            self.atualizar_estado("🔴 OUVINDO")
            audio = gravar_audio()
            self.atualizar_estado("📝 TRANSCRIBINDO")

            texto = transcrever(audio)
            logging.info("VOZ | %s", texto)

            if not texto:
                self.finalizar_tarefa()
                return

            self.root.after(
                0,
                lambda t=texto: self.adicionar_mensagem("VOCÊ", t),
            )

            self.processar_texto(texto, perfil)

        except Exception as erro:
            mensagem = f"Erro no microfone:\n{erro}"
            self.root.after(0, lambda: self.adicionar_mensagem("JARVIS", mensagem))
            self.atualizar_estado("🔴 ERRO")
            self.finalizar_tarefa()

    # ======================================================
    # AULA DO TEAMS
    # ======================================================

    def iniciar_aula_teams(self):
        if self.perfil_atual == "Público":
            self.adicionar_mensagem("JARVIS", "Gravação de aula está bloqueada no perfil público.")
            return
        self.iniciar_tarefa()
        self.executor.submit(self.processar_aula_teams)

    def processar_aula_teams(self):
        try:
            self.atualizar_estado("🎧 GRAVANDO AULA")
            audio = gravar_aula_teams(tempo_maximo=600)
            self.atualizar_estado("📝 TRANSCRIBINDO AULA")

            texto = transcrever(audio)
            logging.info("AULA | %s", texto)

            if not texto:
                self.root.after(
                    0,
                    lambda: self.adicionar_mensagem("JARVIS", "Não consegui extrair áudio da aula."),
                )
                return

            self.root.after(
                0,
                lambda t=texto: self.adicionar_mensagem("VOCÊ", "Transcrição da aula:\n" + t[:5000]),
            )

            self.atualizar_estado("🧠 RESUMINDO AULA")

            prompt = (
                "Você é um assistente acadêmico brasileiro. "
                "Resuma esta aula em português do Brasil. "
                "Use estrutura clara: tema principal, tópicos, conceitos-chave, "
                "resumo em 5 itens e tarefas ou pendências. "
                "Se houver algo mal explicado ou incompleto, deixe explícito.\n\n"
                f"TRANSCRIÇÃO:\n{texto}"
            )

            resumo = perguntar(prompt)

            self.root.after(
                0,
                lambda r=resumo: self.adicionar_mensagem("JARVIS", r),
            )

            self.atualizar_estado("🔊 FALANDO")

            with self.tts_lock:
                falar(resumo)

        except Exception as erro:
            mensagem = f"Erro ao gravar e resumir a aula:\n{erro}"
            self.root.after(0, lambda: self.adicionar_mensagem("JARVIS", mensagem))
            self.atualizar_estado("🔴 ERRO")
        finally:
            self.finalizar_tarefa()

    # ======================================================
    # ANÁLISE DE PRINT
    # ======================================================

    def iniciar_analise_print(self):
        if self.perfil_atual == "Público":
            self.adicionar_mensagem("JARVIS", "Análise de tela está bloqueada no perfil público.")
            return
        self.iniciar_tarefa()
        self.executor.submit(self.processar_analise_print)

    def processar_analise_print(self):
        try:
            self.atualizar_estado("TIRANDO PRINT")
            tirar_print()
            self.atualizar_estado("ANALISANDO")

            ultimo_print = obter_ultimo_print()

            if ultimo_print is None:
                self.root.after(
                    0,
                    lambda: self.adicionar_mensagem("JARVIS", "Não encontrei o print para analisar."),
                )
                self.finalizar_tarefa()
                return

            resposta = analisar_imagem(
                ultimo_print,
                "Analise este print cuidadosamente e me diga o que aparece nele. "
                "Se houver erros, mensagens ou informações importantes, explique "
                "de forma clara e direta.",
            )

            self.root.after(
                0,
                lambda r=resposta: self.adicionar_mensagem("JARVIS", r),
            )
            self.atualizar_estado("FALANDO")

            with self.tts_lock:
                falar(resposta)

            self.finalizar_tarefa()

        except Exception as erro:
            mensagem = f"Erro ao analisar o print:\n{erro}"
            self.root.after(0, lambda: self.adicionar_mensagem("JARVIS", mensagem))
            self.finalizar_tarefa()

    # ======================================================
    # INICIAR
    # ======================================================

    def iniciar(self):
        self.root.mainloop()


# ==========================================================
# EXECUÇÃO
# ==========================================================

if __name__ == "__main__":
    interface = JarvisInterface()
    interface.iniciar()
