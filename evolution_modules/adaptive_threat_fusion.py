'''adaptive_threat_fusion.py'''

from __future__ import annotations
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ThreatIndicator:
    """A single threat indicator."""
    source: str
    indicator: str
    confidence: float  # 0.0 - 1.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "indicator": self.indicator,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }

class ThreatFusionEngine:
    """Aggregates, normalizes, and scores threat indicators from multiple feeds."""

    def __init__(self, max_indicators: int = 1000) -> None:
        """
        Initialize the engine.

        Args:
            max_indicators: Upper bound on stored indicators to limit memory usage.
        """
        self.max_indicators = max_indicators
        self._store: List[ThreatIndicator] = []

    def ingest(self, raw: Dict[str, Any]) -> None:
        """
        Ingest a raw threat payload from an external feed.

        Expected keys: 'source', 'indicator', 'confidence'.

        Raises:
            ValueError: If required fields are missing or malformed.
        """
        try:
            source = str(raw["source"])
            indicator = str(raw["indicator"])
            confidence = float(raw["confidence"])
        except (KeyError, TypeError, ValueError) as exc:
            logger.error("Invalid threat payload: %s", raw)
            raise ValueError("Malformed threat payload") from exc

        if not (0.0 <= confidence <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")

        ti = ThreatIndicator(source=source, indicator=indicator, confidence=confidence)
        self._store.append(ti)
        if len(self._store) > self.max_indicators:
            # Simple FIFO eviction
            self._store.pop(0)

    def query(self, indicator: str) -> Optional[ThreatIndicator]:
        """
        Retrieve the most recent entry for a given indicator.

        Returns:
            ThreatIndicator if found, else None.
        """
        for ti in reversed(self._store):
            if ti.indicator == indicator:
                return ti
        return None

    def top_n(self, n: int = 5) -> List[ThreatIndicator]:
        """
        Return the top N indicators sorted by confidence (desc).

        Args:
            n: Number of indicators to return.

        Returns:
            List of ThreatIndicator objects.
        """
        sorted_indicators = sorted(self._store, key=lambda ti: ti.confidence, reverse=True)
        return sorted_indicators[:n]

    def export_json(self) -> str:
        """Export the current store as a JSON string."""
        return json.dumps([ti.to_dict() for ti in self._store], indent=2)

def _demo() -> None:
    """Simple demonstration used when the module is executed directly."""
    engine = ThreatFusionEngine(max_indicators=10)
    sample_feed = [
        {"source": "feed_a", "indicator": "192.0.2.1", "confidence": 0.9},
        {"source": "feed_b", "indicator": "malicious.exe", "confidence": 0.85},
        {"source": "feed_c", "indicator": "192.0.2.1", "confidence": 0.95},
    ]

    for entry in sample_feed:
        try:
            engine.ingest(entry)
        except ValueError as e:
            logger.warning("Skipped entry: %s", e)

    print("Top indicators:")
    for ti in engine.top_n():
        print(f"- {ti.indicator} (confidence {ti.confidence:.2f}, source {ti.source})")

    print("\nJSON export:")
    print(engine.export_json())

if __name__ == "__main__":
    _demo()
