"""
adaptive_credential_attenuator.py

Utility for generating short‑lived, scoped credentials derived from a master secret.
Designed to be lightweight, auditable and safe for inclusion in any Cortana module.
"""

import secrets
import string
import datetime
import hashlib
from typing import Optional, Dict, Any


class AttenuationError(Exception):
    """Base exception for all attenuation‑related failures."""


class CredentialAttenuator:
    """Generate and validate attenuated credentials.

    A *credential* is a dictionary containing a cryptographic token, an ISO‑8601
    expiration timestamp, a textual *scope* and a remaining‑use counter.

    The implementation is deliberately simple – it hashes the master secret
    together with the requested parameters and a random salt.  The hash is
    computationally irreversible, making the derived token safe to expose to
    downstream services.
    """

    def __init__(self, master_secret: str, default_ttl: datetime.timedelta = datetime.timedelta(minutes=15)) -> None:
        if not master_secret:
            raise ValueError("master_secret must be a non‑empty string")
        self._master_secret = master_secret
        self._default_ttl = default_ttl

    def generate(self, scope: str, ttl: Optional[datetime.timedelta] = None, usage_limit: int = 1) -> Dict[str, Any]:
        """Create a new attenuated credential.

        Args:
            scope: Arbitrary identifier describing what the token may be used for
                (e.g. ``"read:water_meter"``).
            ttl: Desired time‑to‑live; falls back to the instance default.
            usage_limit: How many successful validations are allowed before the
                token is considered exhausted.

        Returns:
            A dictionary with the keys ``token``, ``expires_at``, ``scope`` and
            ``remaining_uses``.
        """
        if not scope:
            raise ValueError("scope must be a non‑empty string")
        ttl = ttl or self._default_ttl
        if ttl.total_seconds() <= 0:
            raise ValueError("ttl must be a positive duration")
        if usage_limit < 1:
            raise ValueError("usage_limit must be at least 1")

        token = self._derive_token(scope, ttl, usage_limit)
        expires_at = datetime.datetime.utcnow() + ttl
        return {
            "token": token,
            "expires_at": expires_at.isoformat(timespec='seconds') + "Z",
            "scope": scope,
            "remaining_uses": usage_limit,
        }

    def _derive_token(self, scope: str, ttl: datetime.timedelta, usage_limit: int) -> str:
        """Internal helper that produces a deterministic SHA‑256 token.

        The token incorporates:
        * the master secret (kept private),
        * the requested *scope*,
        * the TTL in seconds,
        * the usage limit, and
        * a cryptographically‑secure random *salt*.
        """
        salt = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
        raw = f"{self._master_secret}:{scope}:{ttl.total_seconds()}:{usage_limit}:{salt}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def validate(token_info: Dict[str, Any]) -> bool:
        """Validate a credential dictionary.

        Checks that the current UTC time is before ``expires_at`` and that the
        ``remaining_uses`` counter is positive.  Any malformed input returns
        ``False`` rather than raising.
        """
        try:
            expires_str = token_info["expires_at"].replace("Z", "")
            expires = datetime.datetime.fromisoformat(expires_str)
            if datetime.datetime.utcnow() > expires:
                return False
            if token_info.get("remaining_uses", 0) <= 0:
                return False
            return True
        except Exception:
            return False


def _demo() -> None:
    """Simple sanity‑check executed when the module is run directly."""
    master = "super_secret_master_key_123"
    attenuator = CredentialAttenuator(master)
    cred = attenuator.generate(scope="read:water_meter", usage_limit=3)
    print("Generated credential:", cred)
    print("Valid immediately?", CredentialAttenuator.validate(cred))
    # Simulate a single use
    cred["remaining_uses"] -= 1
    print("After one use, still valid?", CredentialAttenuator.validate(cred))


if __name__ == "__main__":
    _demo()
