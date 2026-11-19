"""Deteccao leve de movimento e interface opcional para YOLO."""

from PIL import Image


class MotionDetector:
    def __init__(self, threshold: float = 18.0, min_changed_pixels: int = 250):
        self.threshold = threshold
        self.min_changed_pixels = min_changed_pixels
        self._previous = None

    def detect(self, image: Image.Image) -> dict:
        try:
            import cv2
            import numpy as np
        except ImportError as erro:
            raise RuntimeError(
                "Deteccao de movimento requer opencv-python e numpy."
            ) from erro

        frame = np.asarray(image.convert("RGB"))
        atual = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        anterior = self._previous
        self._previous = atual

        if anterior is None or anterior.shape != atual.shape:
            return {"motion": False, "changed_pixels": 0}

        diferenca = cv2.absdiff(anterior, atual)
        _, mascara = cv2.threshold(diferenca, self.threshold, 255, cv2.THRESH_BINARY)
        pixels_alterados = int(cv2.countNonZero(mascara))
        return {
            "motion": pixels_alterados >= self.min_changed_pixels,
            "changed_pixels": pixels_alterados,
        }

    def reset(self) -> None:
        self._previous = None


class YoloDetector:
    def __init__(self, model_path=None, confidence: float = 0.35):
        self.model_path = model_path
        self.confidence = confidence
        self._model = None

    def _load(self):
        if self._model is not None:
            return
        if self.model_path is None:
            raise RuntimeError("Configure VisionSettings.yolo_model antes de usar YOLO.")
        try:
            from ultralytics import YOLO
        except ImportError as erro:
            raise RuntimeError(
                "Deteccao de objetos requer ultralytics. Instale requirements-vision.txt."
            ) from erro
        self._model = YOLO(str(self.model_path))

    def detect(self, image: Image.Image) -> list[dict]:
        self._load()
        resultados = self._model.predict(
            source=image,
            conf=self.confidence,
            verbose=False,
        )
        deteccoes = []
        for resultado in resultados:
            nomes = resultado.names
            for caixa in resultado.boxes:
                indice = int(caixa.cls.item())
                deteccoes.append({
                    "label": nomes[indice],
                    "confidence": float(caixa.conf.item()),
                    "xyxy": [float(valor) for valor in caixa.xyxy[0].tolist()],
                })
        return deteccoes
