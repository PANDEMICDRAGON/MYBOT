"""Privacy-Preserving Telemetry Aggregator.

Collects telemetry events, applies differential privacy, signs the payload,
and prepares it for secure transmission.
"""

import json
import hmac
import hashlib
import time
import random
import math
from typing import List, Dict, Any

class TelemetryAggregator:
    """Aggregates telemetry events and emits privacy‑preserving, signed payloads.

    The class buffers arbitrary event dictionaries, performs a simple numeric
    sum aggregation, adds Laplace noise calibrated by an epsilon value, and
    returns a JSON envelope containing the noisy metrics and an HMAC‑SHA256
    signature.
    """

    def __init__(self, secret_key: bytes, epsilon: float = 1.0) -> None:
        """Create a new aggregator.

        Args:
            secret_key: Bytes used for HMAC signing. Must be non‑empty.
            epsilon: Differential‑privacy budget; smaller values add more noise.
        Raises:
            ValueError: If ``secret_key`` is empty or ``epsilon`` is non‑positive.
        """
        if not secret_key:
            raise ValueError("secret_key must be non‑empty")
        if epsilon <= 0:
            raise ValueError("epsilon must be positive")
        self._secret_key = secret_key
        self._epsilon = epsilon
        self._buffer: List[Dict[str, Any]] = []

    def record(self, event: Dict[str, Any]) -> None:
        """Add a telemetry event to the internal buffer.

        Args:
            event: Dictionary representing a single telemetry snapshot.
        Raises:
            TypeError: If ``event`` is not a dictionary.
        """
        if not isinstance(event, dict):
            raise TypeError("event must be a dict")
        self._buffer.append(event)

    def _laplace_noise(self, scale: float) -> float:
        """Generate Laplace noise with 0 mean and the given scale.

        The implementation uses the inverse‑transform method.
        """
        u = random.random() - 0.5
        return -scale * (1 if u < 0 else -1) * math.log(1 - 2 * abs(u))

    def _apply_differential_privacy(self, aggregated: Dict[str, float]) -> Dict[str, float]:
        """Add Laplace noise to each numeric metric.

        Args:
            aggregated: Deterministic sum of numeric fields.
        Returns:
            A new dictionary with noisy values.
        """
        noisy: Dict[str, float] = {}
        scale = 1.0 / self._epsilon
        for k, v in aggregated.items():
            noise = self._laplace_noise(scale)
            noisy[k] = v + noise
        return noisy

    def _aggregate(self) -> Dict[str, float]:
        """Sum‑reduce numeric fields across all buffered events.

        Returns:
            Mapping of metric name to summed value.
        """
        result: Dict[str, float] = {}
        for ev in self._buffer:
            for k, v in ev.items():
                if isinstance(v, (int, float)):
                    result[k] = result.get(k, 0.0) + float(v)
        return result

    def emit(self) -> str:
        """Create a signed, privacy‑preserving payload and clear the buffer.

        Returns:
            JSON string containing ``payload`` and ``signature`` fields.
        Raises:
            RuntimeError: If there is no telemetry to emit.
        """
        if not self._buffer:
            raise RuntimeError("No telemetry to emit")
        aggregated = self._aggregate()
        noisy = self._apply_differential_privacy(aggregated)
        payload = {
            "timestamp": int(time.time()),
            "metrics": noisy,
        }
        payload_bytes = json.dumps(payload, separators=(",", ":")).encode()
        signature = hmac.new(self._secret_key, payload_bytes, hashlib.sha256).hexdigest()
        envelope = {"payload": payload, "signature": signature}
        # In production this would be sent over a secure channel.
        self._buffer.clear()
        return json.dumps(envelope)

if __name__ == "__main__":
    # Demonstration of the aggregator in action.
    aggregator = TelemetryAggregator(secret_key=b"supersecret", epsilon=0.5)
    aggregator.record({"cpu_load": 23, "mem_usage": 58})
    aggregator.record({"cpu_load": 27, "mem_usage": 61})
    try:
        output = aggregator.emit()
        print("Emitted telemetry:", output)
    except Exception as exc:
        print("Telemetry emission failed:", exc)
