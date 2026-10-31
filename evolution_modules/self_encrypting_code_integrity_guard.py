import hashlib, base64, secrets, os
from typing import Optional

class IntegrityGuardError(Exception):
    """Base exception for integrity guard errors."""
    pass

class SelfEncryptingCodeIntegrityGuard:
    """
    Compute a SHA-256 digest of a file and protect it with a lightweight
    XOR‑based encryption using a secret key. The encrypted token can later be
    used to verify that the file has not been altered.
    """
    def __init__(self, key: Optional[bytes] = None) -> None:
        """
        Initialise the guard with a 32‑byte secret key. If no key is supplied a
        cryptographically‑secure random key is generated.
        """
        if key is None:
            self._key = secrets.token_bytes(32)
        else:
            if len(key) != 32:
                raise IntegrityGuardError("Key must be exactly 32 bytes.")
            self._key = key

    def _xor(self, data: bytes) -> bytes:
        """XOR ``data`` with the internal key, cycling the key as needed."""
        return bytes(b ^ self._key[i % len(self._key)] for i, b in enumerate(data))

    def encrypt_hash(self, file_path: str) -> str:
        """
        Compute SHA-256 of ``file_path`` and return an encrypted token as a
        base64‑encoded string.
        """
        if not os.path.isfile(file_path):
            raise IntegrityGuardError(f"File not found: {file_path}")
        with open(file_path, "rb") as f:
            digest = hashlib.sha256(f.read()).digest()
        encrypted = self._xor(digest)
        return base64.urlsafe_b64encode(encrypted).decode("ascii")

    def verify(self, file_path: str, token: str) -> bool:
        """
        Verify that ``file_path`` matches the previously generated ``token``.
        Returns ``True`` if the file is unchanged, ``False`` otherwise.
        """
        try:
            expected = self.encrypt_hash(file_path)
            return secrets.compare_digest(expected, token)
        except IntegrityGuardError:
            return False

    def rotate_key(self, new_key: bytes) -> None:
        """
        Replace the current secret key with ``new_key``. The new key must be
        exactly 32 bytes.
        """
        if len(new_key) != 32:
            raise IntegrityGuardError("New key must be exactly 32 bytes.")
        self._key = new_key

if __name__ == "__main__":
    guard = SelfEncryptingCodeIntegrityGuard()
    current_file = __file__
    token = guard.encrypt_hash(current_file)
    print(f"Token: {token}")
    assert guard.verify(current_file, token), "Verification failed on original file."
    # Simulate tampering by modifying token
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
    assert not guard.verify(current_file, tampered), "Tampered token incorrectly verified."
    # Rotate key and ensure old token no longer verifies
    guard.rotate_key(secrets.token_bytes(32))
    assert not guard.verify(current_file, token), "Token should fail after key rotation."
    print("All self-tests passed.")
