"""Adaptive Zero-Trust Credential Hardening Engine.

Provides automated generation, validation, and rotation of high‑entropy
credentials while maintaining an audit trail. Designed to be integrated
into any service that requires continuous credential hardening under a
zero‑trust security model.
"""

import logging
import secrets
import string
import hashlib
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CredentialRecord:
    """Store metadata for a credential."""
    secret_hash: str
    created_at: float
    last_used: Optional[float] = None
    rotation_interval: int = 86400  # 24h by default

class AdaptiveZeroTrustHardener:
    """Manage lifecycle of credentials with zero‑trust principles."""

    def __init__(self, rotation_interval: int = 86400) -> None:
        """
        Initialise the hardener.

        Args:
            rotation_interval: Seconds after which a credential must be rotated.
        """
        self._store: Dict[str, CredentialRecord] = {}
        self.rotation_interval = rotation_interval

    def _hash(self, secret: str) -> str:
        """Return a SHA‑256 hash of the secret."""
        return hashlib.sha256(secret.encode('utf-8')).hexdigest()

    def generate(self, length: int = 32) -> str:
        """
        Generate a high‑entropy secret.

        Args:
            length: Desired length of the secret.

        Returns:
            The plain‑text secret.
        """
        alphabet = string.ascii_letters + string.digits + string.punctuation
        secret = ''.join(secrets.choice(alphabet) for _ in range(length))
        secret_hash = self._hash(secret)
        self._store[secret_hash] = CredentialRecord(
            secret_hash=secret_hash,
            created_at=time.time(),
            rotation_interval=self.rotation_interval,
        )
        logger.info("Generated new credential with hash %s", secret_hash)
        return secret

    def validate(self, secret: str) -> bool:
        """
        Validate a presented secret against stored records.

        Args:
            secret: The plain‑text credential to validate.

        Returns:
            True if the credential is known and not expired, False otherwise.
        """
        secret_hash = self._hash(secret)
        record = self._store.get(secret_hash)
        if not record:
            logger.warning("Validation failed: unknown credential")
            return False
        now = time.time()
        if now - record.created_at > record.rotation_interval:
            logger.warning("Credential %s expired, rotation required", secret_hash)
            return False
        record.last_used = now
        logger.info("Credential %s validated successfully", secret_hash)
        return True

    def rotate(self, old_secret: str, new_length: int = 32) -> Optional[str]:
        """
        Rotate an existing credential.

        Args:
            old_secret: The current credential to be replaced.
            new_length: Length of the new credential.

        Returns:
            The new plain‑text credential, or None if rotation failed.
        """
        if not self.validate(old_secret):
            logger.error("Rotation aborted: old credential invalid")
            return None
        old_hash = self._hash(old_secret)
        new_secret = self.generate(new_length)
        # Remove old record
        self._store.pop(old_hash, None)
        logger.info("Rotated credential %s -> %s", old_hash, self._hash(new_secret))
        return new_secret

    def audit_log(self) -> Dict[str, CredentialRecord]:
        """Return a copy of the internal credential store for auditing."""
        return dict(self._store)

def _demo() -> None:
    """Simple demonstration when run as a script."""
    hardener = AdaptiveZeroTrustHardener(rotation_interval=10)  # 10 s for demo
    secret = hardener.generate(16)
    assert hardener.validate(secret)
    time.sleep(11)  # exceed rotation interval
    assert not hardener.validate(secret)
    new_secret = hardener.rotate(secret, 24)
    if new_secret:
        assert hardener.validate(new_secret)
    print("Demo completed successfully.")

if __name__ == "__main__":
    _demo()
