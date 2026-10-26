from __future__ import annotations
import os
import threading
import time
from typing import Any

class MemoryGuardError(Exception):
    """Base exception for MemoryGuard errors."""

class KeyRotationError(MemoryGuardError):
    """Raised when key rotation fails."""

class MemoryGuard:
    """A lightweight in‑process memory guard that encrypts sensitive data at rest and rotates the encryption key periodically.

    The implementation uses a simple XOR cipher as a placeholder; in production it can be swapped for an authenticated encryption primitive.
    """

    _key_lock = threading.Lock()
    _key: bytes

    def __init__(self, rotation_interval: int = 300) -> None:
        """Initialise the guard.

        Args:
            rotation_interval: Seconds between automatic key rotations.
        """
        self._key = os.urandom(32)
        self._rotation_interval = rotation_interval
        self._stop_event = threading.Event()
        self._rotator = threading.Thread(target=self._auto_rotate, daemon=True)
        self._rotator.start()

    def _auto_rotate(self) -> None:
        while not self._stop_event.wait(self._rotation_interval):
            try:
                self.rotate_key()
            except Exception as exc:
                raise KeyRotationError("Automatic key rotation failed") from exc

    def rotate_key(self) -> None:
        """Generate a new encryption key."""
        with self._key_lock:
            self._key = os.urandom(32)

    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypt data using a simple XOR cipher with the current key.

        Not for production cryptography – placeholder for a real primitive.

        Args:
            plaintext: Data to encrypt.

        Returns:
            Encrypted bytes.
        """
        if not isinstance(plaintext, (bytes, bytearray)):
            raise TypeError("plaintext must be bytes")
        with self._key_lock:
            key = self._key
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(plaintext))

    def decrypt(self, ciphertext: bytes) -> bytes:
        """Decrypt data encrypted by :meth:`encrypt`.

        Args:
            ciphertext: Encrypted data.

        Returns:
            Original plaintext.
        """
        # XOR is symmetric
        return self.encrypt(ciphertext)

    def shutdown(self) -> None:
        """Stop the background rotator."""
        self._stop_event.set()
        self._rotator.join()

if __name__ == "__main__":
    guard = MemoryGuard(rotation_interval=2)
    secret = b"OperatorSecret123"
    encrypted = guard.encrypt(secret)
    decrypted = guard.decrypt(encrypted)
    assert decrypted == secret, "Decryption failed"
    print("Encryption round‑trip successful.")
    # Let the rotator run a couple of cycles
    time.sleep(5)
    guard.shutdown()
