"""Adaptive Intent Resilience Engine.

Provides real‑time monitoring of operator intent strings, detecting
sudden semantic shifts and offering corrective suggestions.
"""

from __future__ import annotations
import logging
import difflib
from collections import deque
from dataclasses import dataclass, field
from typing import Deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntentProcessingError(RuntimeError):
    """Raised when intent data cannot be processed."""
    pass

@dataclass
class IntentResilienceEngine:
    """Engine that tracks recent operator intents and flags anomalies."""
    window_size: int = 20
    similarity_threshold: float = 0.6
    _buffer: Deque[str] = field(default_factory=lambda: deque(maxlen=20))

    def ingest_intent(self, intent: str) -> None:
        """Add a new intent to the sliding window.

        Args:
            intent: The operator intent string.
        Raises:
            IntentProcessingError: If intent is not a non‑empty string.
        """
        if not isinstance(intent, str) or not intent:
            raise IntentProcessingError("Intent must be a non‑empty string")
        self._buffer.append(intent)
        logger.debug("Ingested intent: %s", intent)

    def _average_similarity(self, new_intent: str) -> float:
        """Compute average similarity of new_intent against buffered intents."""
        if not self._buffer:
            return 1.0
        scores = [
            difflib.SequenceMatcher(a=prev, b=new_intent).ratio()
            for prev in self._buffer
        ]
        return sum(scores) / len(scores)

    def detect_anomaly(self, new_intent: str) -> bool:
        """Return True if new_intent deviates from recent intents."""
        similarity = self._average_similarity(new_intent)
        logger.debug("Average similarity for '%s': %.3f", new_intent, similarity)
        return similarity < self.similarity_threshold

    def suggest_correction(self, new_intent: str) -> str:
        """Suggest a corrected intent based on the most similar buffered intent.

        Raises:
            IntentProcessingError: If there is no history to base a suggestion on.
        """
        if not self._buffer:
            raise IntentProcessingError("No historical intents to base suggestion on")
        most_similar = max(
            self._buffer,
            key=lambda prev: difflib.SequenceMatcher(a=prev, b=new_intent).ratio(),
        )
        return most_similar

def _demo() -> None:
    engine = IntentResilienceEngine()
    sample_intents = [
        "open patient record",
        "view lab results",
        "schedule follow‑up",
        "open patient record",
        "view lab results",
        "shutdown system",  # anomalous
    ]
    for intent in sample_intents:
        try:
            if engine.detect_anomaly(intent):
                suggestion = engine.suggest_correction(intent)
                logger.info("Anomaly detected: '%s'. Suggested intent: '%s'", intent, suggestion)
            else:
                logger.info("Intent accepted: %s", intent)
            engine.ingest_intent(intent)
        except IntentProcessingError as exc:
            logger.error("Failed to process intent: %s", exc)

if __name__ == "__main__":
    _demo()
