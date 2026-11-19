"""Orquestracao sob demanda da captura, OCR, deteccao e analise."""

from dataclasses import dataclass, field

from .analyzer import MultimodalAnalyzer
from .capture import CapturedFrame, ScreenCapture
from .context import VisionContext, VisionObservation
from .detector import MotionDetector, YoloDetector
from .ocr import OCRReader
from .settings import VisionSettings


@dataclass
class VisionResult:
    frame: CapturedFrame
    motion: dict | None = None
    detections: list[dict] = field(default_factory=list)
    text: str = ""
    description: str = ""


class VisionEngine:
    def __init__(self, settings: VisionSettings | None = None):
        self.settings = settings or VisionSettings()
        self.capture_screen = ScreenCapture(self.settings)
        self.motion_detector = MotionDetector()
        self.object_detector = YoloDetector(
            model_path=self.settings.yolo_model,
            confidence=self.settings.confidence_threshold,
        )
        self.ocr_reader = OCRReader(self.settings)
        self.analyzer = MultimodalAnalyzer()
        self.context = VisionContext()

    def inspect(self, question: str | None = None, save: bool | None = None) -> VisionResult:
        frame = self.capture_screen.capture(save=save)
        motion = None
        detections = []
        text = ""
        description = ""

        if self.settings.enable_motion_detection:
            motion = self.motion_detector.detect(frame.image)
        if self.settings.enable_object_detection:
            detections = self.object_detector.detect(frame.image)
        if self.settings.enable_ocr:
            text = self.ocr_reader.read(frame.image)
        if question:
            description = self.analyzer.analyze(frame.image, question)

        result = VisionResult(
            frame=frame,
            motion=motion,
            detections=detections,
            text=text,
            description=description,
        )
        self.context.add(VisionObservation(
            observed_at=frame.captured_at,
            motion=motion,
            detections=detections,
            text=text,
            description=description,
        ))
        return result
