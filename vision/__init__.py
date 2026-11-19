"""Ferramentas de visao computacional do Jarvis.

Este pacote e independente da interface existente. Nada e inicializado
automaticamente ao importar o pacote.
"""

from .engine import VisionEngine, VisionResult
from .settings import VisionSettings

__all__ = ["VisionEngine", "VisionResult", "VisionSettings"]
