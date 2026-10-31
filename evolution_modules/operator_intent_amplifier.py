"""
Operator Intent Amplifier
Provides proactive intent prediction and resource prefetching for the operator.
"""

from __future__ import annotations
import json
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Event:
    """Simple representation of an operator event."""
    timestamp: float
    type: str
    payload: Dict[str, str] = field(default_factory=dict)

class OperatorIntentAmplifier:
    """
    Analyzes a sliding window of recent operator events and predicts the next
    likely intent using a very small rule‑based model.  The prediction can be
    used by downstream components to pre‑fetch data, spin up compute, or
    adjust security posture before the operator issues the command.
    """

    def __init__(self, window_size: int = 20) -> None:
        self.window_size: int = window_size
        self._events: Deque[Event] = deque(maxlen=window_size)

    def ingest_event(self, event: Event) -> None:
        """Add a new event to the sliding window."""
        if not isinstance(event, Event):
            raise TypeError("event must be an instance of Event")
        self._events.append(event)
        logger.debug("Ingested event %s", event)

    def _frequency_map(self) -> Dict[str, int]:
        """Count occurrences of event types in the current window."""
        freq: Dict[str, int] = {}
        for ev in self._events:
            freq[ev.type] = freq.get(ev.type, 0) + 1
        return freq

    def predict_intent(self) -> Optional[str]:
        """
        Predict the next intent based on the most frequent recent event type.
        Returns None if there is insufficient data.
        """
        if not self._events:
            return None
        freq = self._frequency_map()
        predicted = max(freq, key=freq.get)
        logger.info("Predicted next intent: %s", predicted)
        return predicted

    def prefetch_resources(self) -> List[str]:
        """
        Translate a predicted intent into a list of resource identifiers that
        should be prefetched.  This mapping is deliberately static for safety.
        """
        intent = self.predict_intent()
        mapping: Dict[str, List[str]] = {
            "data_query": ["db_connection", "query_cache"],
            "file_upload": ["storage_bucket", "encryption_key"],
            "system_report": ["metrics_collector", "report_template"],
        }
        resources = mapping.get(intent, [])
        if resources:
            logger.info("Prefetching resources for intent %s: %s", intent, resources)
        else:
            logger.info("No resources to prefetch for intent %s", intent)
        return resources


def _demo() -> None:
    """Simple demonstration used when the module is executed directly."""
    import time

    amplifier = OperatorIntentAmplifier(window_size=5)

    sample_events = [
        Event(time.time(), "data_query"),
        Event(time.time(), "data_query"),
        Event(time.time(), "file_upload"),
        Event(time.time(), "data_query"),
        Event(time.time(), "system_report"),
    ]

    for ev in sample_events:
        amplifier.ingest_event(ev)

    print("Predicted intent:", amplifier.predict_intent())
    print("Resources to prefetch:", amplifier.prefetch_resources())


if __name__ == "__main__":
    _demo()
