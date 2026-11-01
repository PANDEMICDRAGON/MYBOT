"""
dynamic_zero_trust_identity_mesh.py
Provides a lightweight zero‑trust identity mesh for distributed components.
"""

import secrets
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from typing import Dict, Tuple

class IdentityError(Exception):
    """Base class for identity mesh errors."""
    pass

class IdentityNotFoundError(IdentityError):
    """Raised when an identity is unknown to the mesh."""
    pass

class TokenVerificationError(IdentityError):
    """Raised when a presented token fails verification."""
    pass

class IdentityMesh:
    """Manages identities and issues short‑lived HMAC‑signed tokens.

    Tokens embed the identity id, an issued timestamp and an expiry.
    The mesh can be queried by any node that shares the secret seed.
    """

    def __init__(self, secret: bytes | None = None, token_ttl: int = 300):
        """Initialize the mesh.

        Args:
            secret: Optional root secret. If omitted a cryptographically strong
                random secret is generated.
            token_ttl: Default time‑to‑live for issued tokens in seconds.
        """
        self._secret = secret or secrets.token_bytes(32)
        self._identities: Dict[str, bytes] = {}
        self._token_ttl = token_ttl

    def register_identity(self, identity_id: str) -> None:
        """Register a new identity with a per‑identity secret.

        Raises:
            IdentityError: If the identity already exists.
        """
        if identity_id in self._identities:
            raise IdentityError(f"Identity {identity_id!r} already registered")
        self._identities[identity_id] = secrets.token_bytes(32)

    def _derive_key(self, identity_id: str) -> bytes:
        """Derive a signing key for the given identity using HMAC‑SHA256.
        """
        per_id_secret = self._identities.get(identity_id)
        if per_id_secret is None:
            raise IdentityNotFoundError(identity_id)
        return hmac.new(self._secret, per_id_secret, hashlib.sha256).digest()

    def issue_token(self, identity_id: str, ttl: int | None = None) -> str:
        """Issue a signed token for the given identity.

        Returns:
            A pipe‑separated token string.
        """
        key = self._derive_key(identity_id)
        now = int(time.time())
        expiry = now + (ttl if ttl is not None else self._token_ttl)
        payload = f"{identity_id}|{now}|{expiry}"
        signature = hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()
        token = f"{payload}|{signature}"
        return token

    def verify_token(self, token: str) -> Tuple[bool, str]:
        """Verify a token.

        Returns:
            (True, identity_id) if valid, otherwise (False, reason).
        """
        try:
            identity_id, issued_str, expiry_str, signature = token.split("|")
            issued = int(issued_str)
            expiry = int(expiry_str)
        except ValueError:
            return False, "malformed token"

        if time.time() > expiry:
            return False, "token expired"

        try:
            key = self._derive_key(identity_id)
        except IdentityNotFoundError:
            return False, "unknown identity"

        payload = f"{identity_id}|{issued}|{expiry}"
        expected_sig = hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_sig, signature):
            return False, "invalid signature"

        return True, identity_id

    def rotate_root_secret(self) -> None:
        """Rotate the root secret while preserving per‑identity secrets.
        This invalidates all previously issued tokens.
        """
        self._secret = secrets.token_bytes(32)

if __name__ == "__main__":
    mesh = IdentityMesh()
    user = "operator_michael"
    mesh.register_identity(user)
    token = mesh.issue_token(user)
    print(f"Issued token: {token}")

    valid, info = mesh.verify_token(token)
    print(f"Verification result: {valid}, info: {info}")

    # Simulate expiry
    expired_token = mesh.issue_token(user, ttl=1)
    time.sleep(2)
    valid, info = mesh.verify_token(expired_token)
    print(f"Expired token verification: {valid}, info: {info}")
