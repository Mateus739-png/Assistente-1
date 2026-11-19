import requests
import base64
from io import BytesIO
from PIL import Image

QWEN_URL = "http://127.0.0.1:11434/v1/chat/completions"
QWEN_URL_FALLBACK = "http://127.0.0.1:8080/"
QWEN_MODEL = "qwen3-coder-reap:latest"

def _post_qwen(dados, timeout=120):
    erros = []

    for url in (QWEN_URL, QWEN_URL_FALLBACK):
        try:
            resposta = requests.post(url, json=dados, timeout=timeout)
            resposta.raise_for_status()
            return resposta
        except requests.exceptions.RequestException as erro:
            erros.append((url, erro))

    ultimo_erro = erros[-1][1] if erros else RuntimeError("Não foi possível conectar ao modelo.")
    raise ultimo_erro

def perguntar(texto):
    dados = {
        "model": QWEN_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "VocÃª Ã© Jarvis, um assistente pessoal brasileiro. "
                    "Fale sempre em portuguÃªs do Brasil. "
                    "Converse de forma natural, descontraÃ­da e direta, "
                    "como uma pessoa falando com outra. "
                    "NÃ£o seja excessivamente formal. "
                    "NÃ£o fique repetindo explicaÃ§Ãµes desnecessÃ¡rias. "
                    "Quando a pergunta for simples, responda de forma simples."
                )
            },
            {
                "role": "user",
                "content": texto
            }
        ],
        "max_tokens": 300
    }

    resposta = _post_qwen(dados, timeout=120)
    return resposta.json()["choices"][0]["message"]["content"]


def resumir_pesquisa(pergunta, resultados):
    contexto = ""

    for i, resultado in enumerate(resultados, 1):
        contexto += (
            f"\nResultado {i}:\n"
            f"TÃ­tulo: {resultado['titulo']}\n"
            f"DescriÃ§Ã£o: {resultado['texto']}\n"
        )

    dados = {
        "model": QWEN_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "VocÃª Ã© Jarvis, um assistente pessoal brasileiro. "
                    "Responda em portuguÃªs do Brasil. "
                    "Analise os resultados de pesquisa fornecidos. "
                    "FaÃ§a um resumo curto, natural e Ãºtil. "
                    "NÃ£o invente informaÃ§Ãµes que nÃ£o estejam nos resultados."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Pesquisei na internet sobre: {pergunta}\n\n"
                    f"{contexto}\n\n"
                    "FaÃ§a um resumo Ãºtil para o usuÃ¡rio."
                )
            }
        ],
        "max_tokens": 350
    }

    resposta = _post_qwen(dados, timeout=120)
    return resposta.json()["choices"][0]["message"]["content"]


def resolver_pesquisa_memoria(pergunta, memorias):
    contexto = "\n".join(
        f"- {memoria}"
        for memoria in memorias
    )

    dados = {
        "model": QWEN_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "VocÃª Ã© um assistente que transforma referÃªncias "
                    "do usuÃ¡rio em termos de pesquisa. "
                    "Use exclusivamente as informaÃ§Ãµes da memÃ³ria fornecida. "
                    "Retorne SOMENTE o termo que deve ser pesquisado na internet. "
                    "NÃ£o explique nada. "
                    "NÃ£o use frases como 'pesquisar', 'informaÃ§Ãµes sobre' ou 'o usuÃ¡rio'."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Pedido do usuÃ¡rio: {pergunta}\n\n"
                    f"MemÃ³ria:\n{contexto}\n\n"
                    "Qual termo especÃ­fico deve ser pesquisado?"
                )
            }
        ],
        "max_tokens": 50
    }

    resposta = _post_qwen(dados, timeout=120)
    return resposta.json()["choices"][0]["message"]["content"].strip()

def responder_com_memoria(pergunta, memorias):
    contexto = "\n".join(
        f"- {memoria}"
        for memoria in memorias
    )

    dados = {
        "model": QWEN_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "VocÃª Ã© Jarvis, um assistente pessoal brasileiro. "
                    "Responda em portuguÃªs do Brasil. "
                    "Use somente as informaÃ§Ãµes da memÃ³ria fornecida. "
                    "Responda de forma natural, curta e direta. "
                    "Se a memÃ³ria nÃ£o tiver a resposta, diga que nÃ£o sabe. "
                    "Nunca invente informaÃ§Ãµes."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Pergunta: {pergunta}\n\n"
                    f"MemÃ³ria disponÃ­vel:\n{contexto}\n\n"
                    "Responda Ã  pergunta."
                )
            }
        ],
        "max_tokens": 150
    }

    resposta = _post_qwen(dados, timeout=120)
    return resposta.json()["choices"][0]["message"]["content"]


def resumir_aula(texto):
    prompt = (
        "Você é um assistente acadêmico brasileiro. "
        "Resuma esta aula de forma clara e fácil de estudar. "
        "Estruture em: tema principal, tópicos abordados, conceitos-chave, "
        "resumo em 5 itens e tarefas ou pendências. "
        "Use português do Brasil, linguagem direta e simples.\n\n"
        f"TRANSCRIÇÃO:\n{texto}"
    )

    return perguntar(prompt)


# ==========================================================
# ANÃLISE DE IMAGEM
# ==========================================================

def analisar_imagem(caminho, pergunta):

    imagem = Image.open(caminho).convert("RGB")

    # Reduz bastante a imagem para acelerar o Qwen-VL
    imagem.thumbnail(
        (1280, 720),
        Image.Resampling.LANCZOS
    )

    buffer = BytesIO()

    imagem.save(
        buffer,
        format="JPEG",
        quality=60,
        optimize=True
    )

    imagem_base64 = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    dados = {
        "model": QWEN_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": pergunta
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": (
                                "data:image/jpeg;base64,"
                                + imagem_base64
                            )
                        }
                    }
                ]
            }
        ],
        "max_tokens": 80,
        "temperature": 0.1
    }

    resposta = _post_qwen(dados, timeout=600)

    if not resposta.ok:
        print()
        print("âŒ ERRO DO QWEN-VL")
        print("Status:", resposta.status_code)
        print("Resposta do servidor:")
        print(resposta.text)
        print()

        return "NÃ£o consegui analisar a imagem."

    resultado = resposta.json()

    return resultado["choices"][0]["message"]["content"].strip()
