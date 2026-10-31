"""adaptive_quantum_threat_model.py

A self‑contained module that provides a post‑quantum‑aware, adaptive threat‑modeling engine.
It allows dynamic registration of threat signatures, computes a quantum‑resistant
fingerprint for each signature, and evaluates incoming events against the model
to produce a risk score.

The implementation uses only the Python standard library, making it safe to
import in constrained environments.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping


class ThreatModelError(Exception):
    """Base exception for all errors raised by :class:`AdaptiveQuantumThreatModel`."""


def _pq_hash(data: bytes) -> str:
    """Return a post‑quantum‑resistant hash of *data*.

    Currently uses SHA‑3‑256 which is a NIST‑approved hash function considered
    resistant to quantum attacks (Grover's algorithm provides at most a square‑root
    speed‑up). The function returns a hexadecimal string.
    """
    return hashlib.sha3_256(data).hexdigest()


@dataclass
class ThreatSignature:
    """Immutable representation of a threat signature.

    Attributes
    ----------
    name: str
        Human‑readable identifier.
    pattern: Mapping[str, Any]
        JSON‑compatible pattern that an event must match to be considered a hit.
    severity: int
        Integer in the range 1‑10 indicating the base severity of the threat.
    fingerprint: str = field(init=False)
        Quantum‑resistant hash computed from ``name`` and ``pattern``.
    """

    name: str
    pattern: Mapping[str, Any]
    severity: int
    fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        if not (1 <= self.severity <= 10):
            raise ThreatModelError(f"Severity must be between 1 and 10, got {self.severity}")
        # Serialize pattern deterministically for hashing
        try:
            pattern_bytes = json.dumps(self.pattern, sort_keys=True).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise ThreatModelError(f"Pattern must be JSON‑serializable: {exc}") from exc
        self.fingerprint = _pq_hash(self.name.encode("utf-8") + pattern_bytes)

    def matches(self, event: Mapping[str, Any]) -> bool:
        """Return ``True`` if *event* satisfies the signature's pattern.

        The matching algorithm is deliberately simple: every key in ``pattern``
        must exist in ``event`` and the associated values must be equal.
        """
        for key, expected in self.pattern.items():
            if event.get(key) != expected:
                return False
        return True


class AdaptiveQuantumThreatModel:
    """Container for dynamic threat signatures with quantum‑resistant identification.

    The model supports adding, removing, and evaluating signatures at runtime.
    Risk scores are aggregated as a weighted sum of matched signature severities.
    """

    def __init__(self) -> None:
        self._signatures: Dict[str, ThreatSignature] = {}

    def add_signature(self, signature: ThreatSignature) -> None:
        """Register a new *signature*.

        Raises
        ------
        ThreatModelError
            If a signature with the same fingerprint already exists.
        """
        if signature.fingerprint in self._signatures:
            raise ThreatModelError(f"Signature '{signature.name}' already registered")
        self._signatures[signature.fingerprint] = signature

    def remove_signature(self, fingerprint: str) -> None:
        """Remove a signature identified by its *fingerprint*.

        Raises
        ------
        ThreatModelError
            If the fingerprint is unknown.
        """
        try:
            del self._signatures[fingerprint]
        except KeyError as exc:
            raise ThreatModelError(f"Fingerprint {fingerprint} not found") from exc

    def evaluate_event(self, event: Mapping[str, Any]) -> float:
        """Evaluate *event* against all registered signatures.

        Returns a risk score in the range ``0.0`` – ``10.0`` where ``10.0``
        represents the maximum aggregated severity.
        """
        if not isinstance(event, Mapping):
            raise ThreatModelError("Event must be a mapping type (e.g., dict)")
        total_severity = 0
        for sig in self._signatures.values():
            if sig.matches(event):
                total_severity += sig.severity
        # Normalise to 0‑10 scale (max possible severity is 10 * number of signatures)
        max_possible = 10 * len(self._signatures) if self._signatures else 1
        risk_score = (total_severity / max_possible) * 10.0
        return round(risk_score, 2)

    def list_signatures(self) -> List[Dict[str, Any]]:
        """Return a JSON‑serialisable list of registered signatures."""
        return [
            {
                "name": sig.name,
                "severity": sig.severity,
                "fingerprint": sig.fingerprint,
                "pattern": sig.pattern,
            }
            for sig in self._signatures.values()
        ]


if __name__ == "__main__":
    # Simple demonstration harness
    model = AdaptiveQuantumThreatModel()
    try:
        sig1 = ThreatSignature(
            name="SuspiciousLogin",
            pattern={"event_type": "login", "location": "unknown"},
            severity=7,
        )
        sig2 = ThreatSignature(
            name="DataExfiltration",
            pattern={"event_type": "file_transfer", "direction": "outbound"},
            severity=9,
        )
        model.add_signature(sig1)
        model.add_signature(sig2)
    except ThreatModelError as e:
        print(f"Error during signature registration: {e}", file=sys.stderr)
        sys.exit(1)

    test_events = [
        {"event_type": "login", "location": "unknown", "user": "alice"},
        {"event_type": "file_transfer", "direction": "outbound", "size_mb": 120},
        {"event_type": "login", "location": "office", "user": "bob"},
    ]

    for i, ev in enumerate(test_events, 1):
        try:
            score = model.evaluate_event(ev)
            print(f"Event {i} risk score: {score}")
        except ThreatModelError as e:
            print(f"Failed to evaluate event {i}: {e}", file=sys.stderr)

    print("Registered signatures:")
    print(json.dumps(model.list_signatures(), indent=2))
