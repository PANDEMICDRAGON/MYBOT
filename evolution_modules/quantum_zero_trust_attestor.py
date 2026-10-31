"""
quantum_zero_trust_attestor.py
Provides post‑quantum resistant zero‑trust attestation tokens.
"""

import hashlib
import json
import secrets
import time
from dataclasses import dataclass
from typing import Optional


class AttestationError(Exception):
    """Base exception for attestation failures."""


@dataclass(frozen=True)
class AttestationToken:
    """Immutable representation of an attestation token."""
    issuer: str
    subject: str
    issued_at: int
    expires_at: int
    nonce: str
    signature: str

    def to_json(self) -> str:
        """Serialize the token to a JSON string."""
        return json.dumps({
            "issuer": self.issuer,
            "subject": self.subject,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "nonce": self.nonce,
            "signature": self.signature,
        }, separators=(",", ":"))


class QuantumZeroTrustAttestor:
    """
    Generates and validates zero‑trust attestation tokens that are
    resistant to quantum adversaries by using SHA3‑512 based signatures.
    """

    def __init__(self, issuer_id: str, secret_key: Optional[bytes] = None) -> None:
        """
        Initialise the attestor.

        Args:
            issuer_id: Identifier of the token issuer.
            secret_key: Optional 32‑byte secret; if omitted a random key is generated.
        """
        self.issuer_id = issuer_id
        self._secret_key = secret_key or secrets.token_bytes(32)

    def _sign(self, payload: bytes) -> str:
        """Create a deterministic signature over the payload."""
        hasher = hashlib.sha3_512()
        hasher.update(self._secret_key)
        hasher.update(payload)
        return hasher.hexdigest()

    def generate(self, subject: str, ttl_seconds: int = 300) -> AttestationToken:
        """
        Produce a new attestation token.

        Args:
            subject: The entity being attested.
            ttl_seconds: Token lifetime in seconds.

        Returns:
            An AttestationToken instance.

        Raises:
            AttestationError: If inputs are invalid.
        """
        if not subject:
            raise AttestationError("Subject must be a non‑empty string.")
        now = int(time.time())
        expires = now + max(1, ttl_seconds)
        nonce = secrets.token_hex(16)
        payload = f"{self.issuer_id}|{subject}|{now}|{expires}|{nonce}".encode()
        signature = self._sign(payload)
        return AttestationToken(
            issuer=self.issuer_id,
            subject=subject,
            issued_at=now,
            expires_at=expires,
            nonce=nonce,
            signature=signature,
        )

    def verify(self, token: AttestationToken) -> bool:
        """
        Validate a token's integrity and expiry.

        Args:
            token: The AttestationToken to verify.

        Returns:
            True if the token is valid, False otherwise.
        """
        if token.expires_at < int(time.time()):
            return False
        payload = f"{token.issuer}|{token.subject}|{token.issued_at}|{token.expires_at}|{token.nonce}".encode()
        expected_sig = self._sign(payload)
        return secrets.compare_digest(expected_sig, token.signature)


def _demo() -> None:
    """Simple demonstration when run as a script."""
    attestor = QuantumZeroTrustAttestor(issuer_id="cortana")
    token = attestor.generate(subject="operator_michael")
    print("Generated token JSON:", token.to_json())
    valid = attestor.verify(token)
    print("Verification result:", valid)


if __name__ == "__main__":
    _demo()
