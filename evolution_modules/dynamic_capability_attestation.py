"""
dynamic_capability_attestation.py

Provides CapabilityAttestor class for generating and verifying
cryptographic attestations of operator capabilities in a zero‑trust
environment. Attestations are HMAC‑SHA256 over a JSON payload
containing capability name, timestamp, and a nonce. Keys rotate
periodically; the module manages an in‑memory key store.
"""

import hmac
import hashlib
import json
import os
import threading
import time
from dataclasses import dataclass
from typing import Dict, Any

class AttestationError(Exception):
    """Base exception for attestation failures."""

@dataclass(frozen=True)
class Attestation:
    """Immutable representation of an attestation."""
    capability: str
    timestamp: float
    nonce: str
    signature: str

class CapabilityAttestor:
    """Generates and verifies capability attestations using rotating HMAC keys.
    The class is thread‑safe and suitable for embedding in autonomous agents.
    """

    _key_rotation_interval: float = 300.0  # seconds

    def __init__(self) -> None:
        self._keys: Dict[int, bytes] = {}
        self._current_key_id: int = 0
        self._lock = threading.RLock()
        self._rotate_key()  # initialise first key
        self._start_rotation_daemon()

    def _rotate_key(self) -> None:
        """Create a new HMAC key and discard the oldest if needed."""
        with self._lock:
            new_key = os.urandom(32)
            self._current_key_id += 1
            self._keys[self._current_key_id] = new_key
            # keep only the last two keys (current + previous) for verification
            if len(self._keys) > 2:
                oldest = min(self._keys.keys())
                del self._keys[oldest]

    def _start_rotation_daemon(self) -> None:
        """Background thread that rotates the key at a fixed interval."""
        def daemon() -> None:
            while True:
                time.sleep(self._key_rotation_interval)
                self._rotate_key()
        thread = threading.Thread(target=daemon, daemon=True, name="KeyRotator")
        thread.start()

    def _current_key(self) -> bytes:
        with self._lock:
            return self._keys[self._current_key_id]

    def generate(self, capability: str) -> Attestation:
        """Create an attestation for ``capability``.
        Returns an :class:`Attestation` instance.
        """
        if not capability:
            raise AttestationError("Capability name must be non‑empty")
        timestamp = time.time()
        nonce = os.urandom(16).hex()
        payload = json.dumps({
            "capability": capability,
            "timestamp": timestamp,
            "nonce": nonce,
        }, separators=(",", ":"), sort_keys=True).encode()
        signature = hmac.new(self._current_key(), payload, hashlib.sha256).hexdigest()
        return Attestation(capability, timestamp, nonce, signature)

    def verify(self, attestation: Attestation) -> bool:
        """Verify an :class:`Attestation`. Returns ``True`` if the signature
        matches any known key (current or previous); otherwise raises
        :class:`AttestationError`.
        """
        payload = json.dumps({
            "capability": attestation.capability,
            "timestamp": attestation.timestamp,
            "nonce": attestation.nonce,
        }, separators=(",", ":"), sort_keys=True).encode()
        with self._lock:
            for key in self._keys.values():
                expected = hmac.new(key, payload, hashlib.sha256).hexdigest()
                if hmac.compare_digest(expected, attestation.signature):
                    if time.time() - attestation.timestamp > 600:
                        raise AttestationError("Attestation expired")
                    return True
        raise AttestationError("Invalid attestation signature")

def _demo() -> None:
    """Simple demonstration used by the __main__ block."""
    attestor = CapabilityAttestor()
    att = attestor.generate("operator:read_metrics")
    print("Generated attestation:", att)
    try:
        valid = attestor.verify(att)
        print("Verification result:", valid)
    except AttestationError as exc:
        print("Verification failed:", exc)

if __name__ == "__main__":
    _demo()
