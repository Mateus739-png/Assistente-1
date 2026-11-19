"""Configuracoes do pacote de visao."""

from dataclasses import dataclass, field
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class VisionSettings:
    monitor_index: int = 0
    cache_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "screenshots" / "cache")
    save_screenshots: bool = False
    enable_motion_detection: bool = False
    enable_object_detection: bool = False
    enable_ocr: bool = False
    confidence_threshold: float = 0.35
    yolo_model: Path | None = None
    tesseract_cmd: str | None = None
