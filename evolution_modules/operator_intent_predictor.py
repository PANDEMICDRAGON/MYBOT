'''Operator Intent Predictor module.

Provides a lightweight, self‑contained predictor that learns from
operator command history and suggests the most likely next intent.
'''

from __future__ import annotations
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

class PredictionError(Exception):
    """Raised when the predictor cannot generate a prediction."""
    pass

@dataclass
class IntentPredictor:
    """Incrementally learns sequences of operator intents.

    The predictor builds a first‑order Markov model where each observed
    intent maps to a counter of subsequent intents.  It can be persisted
    to JSON and reloaded without external dependencies.
    """
    model: Dict[str, Counter] = field(default_factory=lambda: defaultdict(Counter))
    _last_intent: Optional[str] = None

    def observe(self, intent: str) -> None:
        """Record an observed intent.

        Args:
            intent: The textual representation of the operator intent.
        """
        intent = intent.strip()
        if not intent:
            raise ValueError("Intent must be a non‑empty string")
        if self._last_intent is not None:
            self.model[self._last_intent][intent] += 1
        self._last_intent = intent

    def predict(self, fallback: Optional[str] = None) -> str:
        """Predict the most likely next intent.

        Args:
            fallback: Optional intent to return if prediction is impossible.

        Returns:
            The predicted intent string.

        Raises:
            PredictionError: If no data is available and no fallback is given.
        """
        if self._last_intent is None:
            if fallback is not None:
                return fallback
            raise PredictionError("No prior intent to base prediction on")
        next_counter = self.model.get(self._last_intent)
        if not next_counter:
            if fallback is not None:
                return fallback
            raise PredictionError(f"No observed successors for intent '{self._last_intent}'")
        prediction, _ = next_counter.most_common(1)[0]
        return prediction

    def to_json(self, path: Path) -> None:
        """Persist the model to a JSON file.

        Args:
            path: Destination file path.
        """
        serializable = {k: dict(v) for k, v in self.model.items()}
        path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")

    @classmethod
    def from_json(cls, path: Path) -> "IntentPredictor":
        """Load a predictor from a JSON file.

        Args:
            path: Source file path.

        Returns:
            An IntentPredictor instance with the restored model.
        """
        data = json.loads(path.read_text(encoding="utf-8"))
        model: Dict[str, Counter] = defaultdict(Counter)
        for k, inner in data.items():
            model[k] = Counter(inner)
        return cls(model=model)

def _demo() -> None:
    """Simple demonstration when run as a script."""
    sample_intents = [
        "list_active_sessions",
        "fetch_recent_logs",
        "fetch_recent_logs",
        "list_active_sessions",
        "restart_service",
        "list_active_sessions",
        "fetch_recent_logs",
    ]

    predictor = IntentPredictor()
    for intent in sample_intents:
        predictor.observe(intent)

    try:
        next_intent = predictor.predict(fallback="list_active_sessions")
        print(f"Predicted next intent: {next_intent}")
    except PredictionError as exc:
        print(f"Prediction failed: {exc}", file=sys.stderr)

    tmp_path = Path("intent_model.json")
    predictor.to_json(tmp_path)
    loaded = IntentPredictor.from_json(tmp_path)
    print(f"Loaded model predicts: {loaded.predict(fallback='idle')}")

if __name__ == "__main__":
    _demo()
