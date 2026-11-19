"""Busca e abertura de arquivos dentro das pastas conhecidas do Jarvis."""

import os
import unicodedata
from pathlib import Path


PASTA_ASSISTENTE = Path(__file__).resolve().parents[1]
PASTA_DOWNLOADS = Path.home() / "Downloads"
PASTAS_BUSCA = tuple(dict.fromkeys((PASTA_ASSISTENTE, PASTA_DOWNLOADS)))
PASTAS_IGNORADAS = {".git", "__pycache__", "node_modules"}


def _normalizar_nome(nome):
    nome = unicodedata.normalize("NFKD", nome.casefold())
    nome = "".join(c for c in nome if not unicodedata.combining(c))
    return " ".join(nome.strip().strip('"\'').split())


def encontrar_caminho(nome):
    """Retorna correspondências exatas pelo nome em projeto e Downloads."""
    if not isinstance(nome, str) or not nome.strip():
        return []

    nome = nome.strip().strip('"\'')
    nome_alvo = _normalizar_nome(Path(nome).name)
    encontrados = {}

    # Caminhos relativos são resolvidos somente dentro das raízes permitidas.
    if not Path(nome).is_absolute():
        for raiz_permitida in PASTAS_BUSCA:
            candidato = (raiz_permitida / nome).resolve()
            try:
                candidato.relative_to(raiz_permitida.resolve())
                if candidato.exists():
                    encontrados[str(candidato).casefold()] = candidato
            except ValueError:
                continue

    # Aceita caminho completo apenas dentro das pastas de busca permitidas.
    direto = Path(nome).expanduser()
    if direto.is_absolute() and direto.exists():
        direto = direto.resolve()
        for raiz_permitida in PASTAS_BUSCA:
            try:
                direto.relative_to(raiz_permitida.resolve())
                encontrados[str(direto).casefold()] = direto
                break
            except ValueError:
                continue

    for pasta in PASTAS_BUSCA:
        if not pasta.is_dir():
            continue

        for raiz, diretorios, arquivos in os.walk(pasta, onerror=lambda erro: None):
            diretorios[:] = [
                diretorio for diretorio in diretorios
                if diretorio.casefold() not in PASTAS_IGNORADAS
                and not diretorio.startswith(".")
            ]
            for item in (*arquivos, *diretorios):
                item_normalizado = _normalizar_nome(item)
                nome_sem_extensao = _normalizar_nome(Path(item).stem)
                corresponde = item_normalizado == nome_alvo
                corresponde_sem_extensao = not Path(nome).suffix and nome_sem_extensao == nome_alvo
                if corresponde or corresponde_sem_extensao:
                    caminho = (Path(raiz) / item).resolve()
                    encontrados[str(caminho).casefold()] = caminho

    return list(encontrados.values())


def abrir_caminho_generico(nome):
    if not isinstance(nome, str) or not nome.strip():
        return "Diga o nome do arquivo ou da pasta que você quer abrir."

    nome = nome.strip().strip('"\'')
    encontrados = encontrar_caminho(nome)
    if not encontrados:
        return f"Não encontrei {nome} na pasta do projeto nem em Downloads."

    if len(encontrados) > 1:
        opcoes = "; ".join(str(caminho) for caminho in encontrados[:5])
        restantes = len(encontrados) - 5
        complemento = f"; e mais {restantes}" if restantes > 0 else ""
        return (
            f"Encontrei {len(encontrados)} itens chamados {nome}: "
            f"{opcoes}{complemento}. Diga o caminho ou o nome completo."
        )

    caminho = encontrados[0]
    try:
        os.startfile(str(caminho))
        return f"Abrindo {caminho.name}."
    except (OSError, AttributeError) as erro:
        print(f"Erro ao abrir {caminho}: {erro}")
        return "Não consegui abrir esse arquivo ou pasta neste computador."
