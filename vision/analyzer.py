"""Adaptador opcional para analise multimodal pelo Qwen existente."""

import tempfile
from pathlib import Path

from PIL import Image


class MultimodalAnalyzer:
    def analyze(self, image: Image.Image | str | Path, question: str) -> str:
        try:
            from ia.qwen import analisar_imagem
        except ImportError as erro:
            raise RuntimeError("Nao foi possivel carregar o analisador multimodal ia.qwen.") from erro

        if isinstance(image, (str, Path)):
            return analisar_imagem(str(image), question)

        with tempfile.TemporaryDirectory(prefix="jarvis_vision_") as temporario:
            caminho = Path(temporario) / "frame.png"
            image.save(caminho, format="PNG")
            return analisar_imagem(str(caminho), question)
