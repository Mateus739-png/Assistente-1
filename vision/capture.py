"""Captura de tela sob demanda, sem iniciar gravacao continua."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageGrab

from .settings import VisionSettings


@dataclass(frozen=True)
class CapturedFrame:
    image: Image.Image
    captured_at: datetime
    monitor_index: int
    saved_to: Path | None = None


class ScreenCapture:
    def __init__(self, settings: VisionSettings | None = None):
        self.settings = settings or VisionSettings()

    def capture(self, save: bool | None = None) -> CapturedFrame:
        monitor_index = self.settings.monitor_index
        captured_at = datetime.now().astimezone()

        try:
            import mss

            with mss.mss() as capturador:
                if monitor_index < 0 or monitor_index >= len(capturador.monitors):
                    raise ValueError(f"Indice de monitor invalido: {monitor_index}")
                captura = capturador.grab(capturador.monitors[monitor_index])
                image = Image.frombytes("RGB", captura.size, captura.rgb)
        except ImportError:
            image = ImageGrab.grab(all_screens=(monitor_index == 0)).convert("RGB")

        caminho = None
        deve_salvar = self.settings.save_screenshots if save is None else save
        if deve_salvar:
            self.settings.cache_dir.mkdir(parents=True, exist_ok=True)
            nome = captured_at.strftime("screen_%Y%m%d_%H%M%S_%f.png")
            caminho = self.settings.cache_dir / nome
            image.save(caminho)

        return CapturedFrame(
            image=image,
            captured_at=captured_at,
            monitor_index=monitor_index,
            saved_to=caminho,
        )
