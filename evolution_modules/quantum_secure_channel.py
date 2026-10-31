"""quantum_secure_channel.py

Self‑contained implementation of a lightweight, post‑quantum‑inspired secure channel.

Features
--------
* Pure‑standard‑library – no external dependencies.
* Elliptic‑curve‑like Diffie‑Hellman using a large safe prime (simulated quantum‑resistance).
* Simple XOR‑based encryption derived from a SHA‑256 shared secret.
* Full type hints, docstrings and robust error handling.
* Executable ``__main__`` test harness demonstrating end‑to‑end encrypted messaging
  between two autonomous peers.

While the mathematics is not truly post‑quantum (that requires lattice‑based
algorithms not available in the stdlib), the module abstracts the workflow so
future replacements can be swapped in without altering calling code.
"""

from __future__ import annotations

import base64
import hashlib
import secrets
from dataclasses import dataclass
from typing import Any

# A 127‑bit safe prime (2**127‑1 is a Mersenne prime and works well for demo).
DEFAULT_PRIME: int = (1 << 127) - 1
DEFAULT_GENERATOR: int = 2
KEY_SIZE_BYTES: int = 16  # 128‑bit symmetric key for XOR cipher


class SecureChannelError(Exception):
    """Base exception for all SecureChannel related errors."""


@dataclass(slots=True)
class SecureChannel:
    """Manage a Diffie‑Hellman style key exchange and symmetric encryption.

    Parameters
    ----------
    private_key: int | None
        Optional pre‑generated private exponent. If ``None`` a fresh key is
        generated on instantiation.
    prime: int
        Large prime modulus for the DH group. Defaults to a 127‑bit safe prime.
    generator: int
        Group generator. Defaults to ``2``.
    """

    private_key: int | None = None
    prime: int = DEFAULT_PRIME
    generator: int = DEFAULT_GENERATOR

    def __post_init__(self) -> None:
        if self.private_key is None:
            self.private_key = self._generate_private_key()
        if not (2 <= self.private_key < self.prime - 2):
            raise SecureChannelError("private_key out of valid range")
        self._public_key: int | None = None

    @staticmethod
    def _generate_private_key() -> int:
        """Generate a cryptographically secure private exponent.

        Returns
        -------
        int
            A random integer in the interval ``[2, prime‑2)``.
        """
        # 126‑bit random number ensures it is < prime‑2 for the default prime.
        return secrets.randbits(126) + 2

    def public_key(self) -> int:
        """Return the public key, computing it lazily if needed.

        Returns
        -------
        int
            ``generator ** private_key mod prime``.
        """
        if self._public_key is None:
            self._public_key = pow(self.generator, self.private_key, self.prime)
        return self._public_key

    def _derive_shared_secret(self, peer_public_key: int) -> bytes:
        """Derive a raw shared secret from a peer's public key.

        Parameters
        ----------
        peer_public_key: int
            The counterpart's public key.

        Returns
        -------
        bytes
            SHA‑256 digest of the DH shared integer, truncated to ``KEY_SIZE_BYTES``.
        """
        if not (2 <= peer_public_key < self.prime - 2):
            raise SecureChannelError("peer_public_key out of valid range")
        shared_int: int = pow(peer_public_key, self.private_key, self.prime)
        shared_bytes: bytes = shared_int.to_bytes((shared_int.bit_length() + 7) // 8, "big")
        # Derive a fixed‑size symmetric key via SHA‑256.
        return hashlib.sha256(shared_bytes).digest()[:KEY_SIZE_BYTES]

    @staticmethod
    def _xor_cipher(data: bytes, key: bytes) -> bytes:
        """Encrypt/Decrypt data with a repeating XOR key.

        This is **not** intended for production‑grade confidentiality but
        provides a deterministic, dependency‑free symmetric primitive suitable
        for demonstration and unit‑testing.
        """
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

    def encrypt(self, plaintext: str, peer_public_key: int) -> str:
        """Encrypt ``plaintext`` for a given peer.

        Parameters
        ----------
        plaintext: str
            Human‑readable message to protect.
        peer_public_key: int
            Counterpart's public key.

        Returns
        -------
        str
            Base64‑encoded ciphertext.
        """
        if not isinstance(plaintext, str):
            raise SecureChannelError("plaintext must be a string")
        key = self._derive_shared_secret(peer_public_key)
        cipher_bytes = self._xor_cipher(plaintext.encode("utf-8"), key)
        return base64.b64encode(cipher_bytes).decode("ascii")

    def decrypt(self, ciphertext_b64: str, peer_public_key: int) -> str:
        """Decrypt a previously encrypted message.

        Parameters
        ----------
        ciphertext_b64: str
            Base64 representation produced by :meth:`encrypt`.
        peer_public_key: int
            Counterpart's public key.

        Returns
        -------
        str
            The original plaintext.
        """
        try:
            cipher_bytes = base64.b64decode(ciphertext_b64.encode("ascii"))
        except Exception as exc:
            raise SecureChannelError("invalid base64 ciphertext") from exc
        key = self._derive_shared_secret(peer_public_key)
        plain_bytes = self._xor_cipher(cipher_bytes, key)
        try:
            return plain_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise SecureChannelError("decrypted bytes are not valid UTF‑8") from exc


def _demo() -> None:
    """Simple end‑to‑end demonstration.

    Two autonomous peers (Alice and Bob) instantiate ``SecureChannel`` objects,
    exchange public keys, and send encrypted messages to each other.
    """
    alice = SecureChannel()
    bob = SecureChannel()

    alice_pk = alice.public_key()
    bob_pk = bob.public_key()

    message_from_alice = "Hello Bob, this is Alice."
    encrypted = alice.encrypt(message_from_alice, bob_pk)
    print(f"Alice → Bob (encrypted): {encrypted}")
    decrypted = bob.decrypt(encrypted, alice_pk)
    print(f"Bob decrypts: {decrypted}")

    message_from_bob = "Hi Alice, Bob here. Secure channel works!"
    encrypted2 = bob.encrypt(message_from_bob, alice_pk)
    print(f"Bob → Alice (encrypted): {encrypted2}")
    decrypted2 = alice.decrypt(encrypted2, bob_pk)
    print(f"Alice decrypts: {decrypted2}")

    assert decrypted == message_from_alice
    assert decrypted2 == message_from_bob
    print("✅ SecureChannel demo completed successfully.")


if __name__ == "__main__":
    _demo()
