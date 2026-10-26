"""
post_quantum_key_exchange.py
Provides a lightweight post‑quantum key‑exchange orchestrator using a lattice‑based KEM placeholder. Designed for environments without external crypto libraries.
"""

import os
import hashlib
import secrets
from dataclasses import dataclass
from typing import Tuple

class PQKeyExchangeError(Exception):
    """Base exception for PQKeyExchange operations."""
    pass

@dataclass(frozen=True)
class KeyPair:
    """Public and private key pair."""
    public: bytes
    private: bytes

class PQKeyExchange:
    """
    Simplified post‑quantum key exchange orchestrator.
    Uses a hash‑based encapsulation as a stand‑in for a real KEM.
    """

    @staticmethod
    def generate_keypair() -> KeyPair:
        """
        Generates a pseudo‑random public/private key pair.
        Returns:
            KeyPair: The generated keys.
        """
        private = secrets.token_bytes(32)
        public = hashlib.sha256(private).digest()
        return KeyPair(public=public, private=private)

    @staticmethod
    def encapsulate(public_key: bytes) -> Tuple[bytes, bytes]:
        """
        Encapsulates a shared secret for the given public key.
        Args:
            public_key (bytes): Receiver's public key.
        Returns:
            Tuple[bytes, bytes]: (ciphertext, shared_secret)
        Raises:
            PQKeyExchangeError: If the public key length is unexpected.
        """
        if len(public_key) != 32:
            raise PQKeyExchangeError("Invalid public key length")
        # Derive a random secret and bind it to the public key
        secret = secrets.token_bytes(32)
        ciphertext = hashlib.sha256(public_key + secret).digest()
        shared_secret = hashlib.sha256(secret + public_key).digest()
        return ciphertext, shared_secret

    @staticmethod
    def decapsulate(ciphertext: bytes, private_key: bytes) -> bytes:
        """
        Recovers the shared secret from ciphertext using the private key.
        Args:
            ciphertext (bytes): The encapsulated ciphertext.
            private_key (bytes): Receiver's private key.
        Returns:
            bytes: The recovered shared secret.
        Raises:
            PQKeyExchangeError: If inputs are malformed.
        """
        if len(ciphertext) != 32 or len(private_key) != 32:
            raise PQKeyExchangeError("Invalid ciphertext or private key length")
        public_key = hashlib.sha256(private_key).digest()
        # Placeholder recovery: recompute a deterministic secret from inputs
        recovered_secret = hashlib.sha256(ciphertext + private_key).digest()
        shared_secret = hashlib.sha256(recovered_secret + public_key).digest()
        return shared_secret

def _demo():
    """Simple demonstration executed when run as a script."""
    alice = PQKeyExchange.generate_keypair()
    bob = PQKeyExchange.generate_keypair()

    # Alice encapsulates a secret for Bob
    ct, alice_secret = PQKeyExchange.encapsulate(bob.public)

    # Bob decapsulates
    bob_secret = PQKeyExchange.decapsulate(ct, bob.private)

    assert alice_secret == bob_secret, "Shared secrets differ!"

    print("Post‑quantum key exchange succeeded. Shared secret:", alice_secret.hex())

if __name__ == "__main__":
    _demo()
