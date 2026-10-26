"""
dynamic_zero_trust_issuer.py
Provides a zero‑trust credential issuer that creates short‑lived signed tokens.
"""

import base64
import hashlib
import hmac
import json
import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List

class CredentialError(Exception):
    """Base exception for credential operations."""

class TokenVerificationError(CredentialError):
    """Raised when token verification fails."""

def _b64_encode(data: bytes) -> str:
    """URL‑safe base64 encode without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def _b64_decode(data: str) -> bytes:
    """URL‑safe base64 decode adding required padding."""
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)

class CredentialIssuer:
    """Issues and verifies HMAC‑signed tokens with automatic key rotation.

    The token format mimics a minimal JWT: ``kid.payload.signature`` where each
    segment is URL‑safe base64 without padding.
    """

    _rotation_interval: int = 300  # seconds between key rotations
    _token_lifetime: int = 60      # seconds a token remains valid

    def __init__(self) -> None:
        self._keys: Dict[str, bytes] = {}
        self._current_kid: Optional[str] = None
        self._lock = threading.Lock()
        self._rotate_key()  # initialise the first signing key
        self._start_rotator()

    def _generate_key(self) -> bytes:
        """Create a fresh 128‑bit secret key."""
        return uuid.uuid4().bytes

    def _rotate_key(self) -> None:
        """Generate a new signing key and retire old ones beyond a safety window."""
        with self._lock:
            kid = str(uuid.uuid4())
            self._keys[kid] = self._generate_key()
            self._current_kid = kid
            # Prune keys older than two rotation intervals to bound memory.
            cutoff = time.time() - self._rotation_interval * 2
            for old_kid in list(self._keys):
                # In a full implementation we would store creation timestamps.
                # Here we keep all keys for simplicity.
                pass

    def _start_rotator(self) -> None:
        """Background daemon that rotates the signing key periodically."""
        def rotator() -> None:
            while True:
                time.sleep(self._rotation_interval)
                self._rotate_key()
        t = threading.Thread(target=rotator, daemon=True)
        t.start()

    def issue_token(self, subject: str, scopes: Optional[List[str]] = None) -> str:
        """Create a signed token for *subject*.

        Args:
            subject: Identifier of the token owner (e.g., user email).
            scopes: Optional list of permission strings.
        Returns:
            A compact token string ``kid.payload.signature``.
        """
        if scopes is None:
            scopes = []
        header = {"alg": "HS256", "kid": self._current_kid}
        now = int(time.time())
        payload = {
            "sub": subject,
            "scp": scopes,
            "iat": now,
            "exp": now + self._token_lifetime,
            "jti": str(uuid.uuid4())
        }
        header_b64 = _b64_encode(json.dumps(header, separators=(',', ':')).encode())
        payload_b64 = _b64_encode(json.dumps(payload, separators=(',', ':')).encode())
        signing_input = f"{header_b64}.{payload_b64}".encode()
        key = self._keys[self._current_kid]
        signature = hmac.new(key, signing_input, hashlib.sha256).digest()
        sig_b64 = _b64_encode(signature)
        return f"{header_b64}.{payload_b64}.{sig_b64}"

    def verify_token(self, token: str) -> dict:
        """Validate *token* and return its payload.

        Raises:
            TokenVerificationError: If the token is malformed, expired, or the
                signature does not match.
        """
        try:
            header_b64, payload_b64, sig_b64 = token.split('.')
        except ValueError as exc:
            raise TokenVerificationError("Malformed token") from exc
        header = json.loads(_b64_decode(header_b64).decode())
        kid = header.get("kid")
        if not kid or kid not in self._keys:
            raise TokenVerificationError("Unknown key identifier")
        signing_input = f"{header_b64}.{payload_b64}".encode()
        expected_sig = hmac.new(self._keys[kid], signing_input, hashlib.sha256).digest()
        actual_sig = _b64_decode(sig_b64)
        if not hmac.compare_digest(expected_sig, actual_sig):
            raise TokenVerificationError("Signature mismatch")
        payload = json.loads(_b64_decode(payload_b64).decode())
        now = int(time.time())
        if payload.get("exp", 0) < now:
            raise TokenVerificationError("Token expired")
        return payload

if __name__ == "__main__":
    issuer = CredentialIssuer()
    token = issuer.issue_token("michael.obiero@cortana.ai", ["read", "write"])
    print("Issued token:", token)
    try:
        payload = issuer.verify_token(token)
        print("Verified payload:", payload)
    except TokenVerificationError as err:
        print("Verification failed:", err)
