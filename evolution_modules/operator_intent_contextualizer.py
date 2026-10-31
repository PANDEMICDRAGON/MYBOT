"""
Operator Intent Contextualizer and Prioritizer.

Provides a lightweight engine to ingest raw operator intents,
enrich them with context, compute priority scores, and expose
ordered recommendations. Designed for real‑time integration
with Cortana's autonomous decision loop.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Iterable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass(order=True)
class Intent:
    """Represents a single operator intent."""
    priority: float = field(init=False, compare=True)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc), compare=False)
    raw: str = field(compare=False)
    metadata: Dict[str, Any] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        try:
            self.priority = self._compute_base_priority()
        except Exception as exc:
            logger.exception("Failed to compute priority for intent %s", self.raw)
            raise ValueError("Invalid intent data") from exc

    def _compute_base_priority(self) -> float:
        """Derive a numeric priority from metadata and content."""
        base = 0.0
        # Simple heuristic: presence of keywords boosts priority
        keywords = {"urgent", "critical", "escalate", "immediate"}
        tokens = set(self.raw.lower().split())
        if keywords & tokens:
            base += 5.0
        # Metadata weight
        weight = float(self.metadata.get("weight", 1.0))
        return base * weight

class OperatorIntentContextualizer:
    """Collects intents, enriches them and returns a prioritized list."""

    def __init__(self, max_intents: int = 100) -> None:
        if max_intents <= 0:
            raise ValueError("max_intents must be positive")
        self.max_intents = max_intents
        self._intents: List[Intent] = []

    def ingest(self, raw_intent: str, metadata: Dict[str, Any] | None = None) -> None:
        """Add a new intent to the buffer."""
        metadata = metadata or {}
        try:
            intent = Intent(raw=raw_intent, metadata=metadata)
        except Exception as exc:
            logger.error("Ingestion failed for intent: %s", raw_intent)
            raise
        self._intents.append(intent)
        if len(self._intents) > self.max_intents:
            # Drop the oldest intent(s) to respect the limit
            self._intents.sort(key=lambda i: i.timestamp)
            self._intents = self._intents[-self.max_intents:]

    def prioritize(self) -> List[Intent]:
        """Return intents ordered by descending priority then recency."""
        return sorted(self._intents, key=lambda i: (-i.priority, -i.timestamp.timestamp()))

    def clear(self) -> None:
        """Remove all stored intents."""
        self._intents.clear()

def _demo() -> None:
    ctx = OperatorIntentContextualizer(max_intents=10)
    sample = [
        ("Check battery status", {"weight": 0.8}),
        ("Urgent: Deploy emergency medical kit", {"weight": 1.2}),
        ("Schedule routine maintenance", {"weight": 0.5}),
        ("Critical: Shut down overheating generator", {"weight": 1.5}),
    ]
    for raw, meta in sample:
        ctx.ingest(raw, meta)
    for intent in ctx.prioritize():
        print(f"[{intent.timestamp.isoformat()}] priority={intent.priority:.2f} -> {intent.raw}")

if __name__ == "__main__":
    _demo()
