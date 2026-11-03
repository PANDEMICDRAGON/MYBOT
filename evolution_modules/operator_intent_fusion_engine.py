"""
Operator Intent Fusion Engine
Provides fusion of multimodal operator intent signals.
"""

from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Dict, List

class IntentFusionError(Exception):
    """Raised when the fusion process encounters an unrecoverable condition."""

@dataclass
class IntentSignal:
    """A single intent observation from a specific source.

    Attributes:
        source: Identifier of the signal source (e.g., "keystroke", "voice").
        confidence: Float in the range [0.0, 1.0] indicating certainty.
        intent: The inferred operator intent (e.g., "search", "navigate").
    """
    source: str
    confidence: float  # 0.0 – 1.0
    intent: str

class OperatorIntentFusionEngine:
    """Collects, validates, and fuses operator intent signals.

    The engine applies configurable source weights and a simple weighted‑vote
    algorithm to produce a single, high‑confidence intent. It is deliberately
    lightweight and async‑compatible for deployment on edge compute nodes.
    """

    def __init__(self, weights: Dict[str, float] | None = None) -> None:
        """Create a new fusion engine.

        Args:
            weights: Optional mapping of ``source`` → ``weight``. Sources not
                present default to a weight of ``1.0``.
        """
        self._weights: Dict[str, float] = weights or {}
        self._signals: List[IntentSignal] = []

    def add_signal(self, signal: IntentSignal) -> None:
        """Validate and store an incoming intent signal.

        Raises:
            IntentFusionError: If ``signal.confidence`` is outside the 0‑1 range.
        """
        if not 0.0 <= signal.confidence <= 1.0:
            raise IntentFusionError(
                f"Confidence out of range [{signal.confidence}]; must be 0.0‑1.0"
            )
        self._signals.append(signal)

    async def fuse(self) -> str:
        """Fuse all collected signals into a single intent.

        Returns:
            The intent string with the highest aggregated weighted confidence.

        Raises:
            IntentFusionError: If no signals have been added.
        """
        if not self._signals:
            raise IntentFusionError("No intent signals available for fusion.")
        # Simulate asynchronous processing (e.g., I/O‑bound feature extraction).
        await asyncio.sleep(0)
        scores: Dict[str, float] = {}
        for sig in self._signals:
            weight = self._weights.get(sig.source, 1.0)
            scores[sig.intent] = scores.get(sig.intent, 0.0) + sig.confidence * weight
        # Determine the intent with the highest cumulative score.
        fused_intent = max(scores, key=scores.get)
        # Reset internal state for the next fusion cycle.
        self._signals.clear()
        return fused_intent

def _sample_signal_generator() -> List[IntentSignal]:
    """Create a deterministic set of example signals for the demo harness."""
    return [
        IntentSignal(source="keystroke", confidence=0.92, intent="search"),
        IntentSignal(source="voice", confidence=0.67, intent="search"),
        IntentSignal(source="eye_gaze", confidence=0.81, intent="navigate"),
    ]

async def _demo() -> None:
    """Run a short demonstration of the fusion engine."""
    engine = OperatorIntentFusionEngine(weights={"keystroke": 1.2, "voice": 1.0, "eye_gaze": 0.9})
    for signal in _sample_signal_generator():
        engine.add_signal(signal)
    result = await engine.fuse()
    print(f"Fused operator intent: {result}")

if __name__ == "__main__":
    asyncio.run(_demo())
