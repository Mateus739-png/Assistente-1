"""Contexto curto em memoria para observacoes recentes da tela."""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from threading import RLock


@dataclass
class VisionObservation:
    observed_at: datetime = field(default_factory=lambda: datetime.now().astimezone())
    motion: dict | None = None
    detections: list[dict] = field(default_factory=list)
    text: str = ""
    description: str = ""


class VisionContext:
    def __init__(self, max_observations: int = 10):
        if max_observations < 1:
            raise ValueError("max_observations precisa ser maior que zero.")
        self._observations = deque(maxlen=max_observations)
        self._lock = RLock()

    def add(self, observation: VisionObservation) -> None:
        with self._lock:
            self._observations.append(observation)

    def recent(self) -> list[VisionObservation]:
        with self._lock:
            return list(self._observations)

    def clear(self) -> None:
        with self._lock:
            self._observations.clear()
