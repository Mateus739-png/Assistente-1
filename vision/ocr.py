"""Leitura de texto em imagens usando Tesseract de forma opcional."""

from PIL import Image

from .settings import VisionSettings


class OCRReader:
    def __init__(self, settings: VisionSettings | None = None, language: str = "por"):
        self.settings = settings or VisionSettings()
        self.language = language

    def read(self, image: Image.Image) -> str:
        try:
            import pytesseract
        except ImportError as erro:
            raise RuntimeError(
                "OCR requer pytesseract e o executavel Tesseract instalado no Windows."
            ) from erro

        if self.settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.settings.tesseract_cmd
        return pytesseract.image_to_string(image, lang=self.language).strip()
