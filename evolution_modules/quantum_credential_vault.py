"""Quantum-Resilient Credential Vault.

Provides in-memory storage of credentials encrypted with a
simulated post‑quantum key encapsulation mechanism. Keys are
periodically rotated and old ciphertexts are re‑encrypted.
"""

import base64
import hashlib
import secrets
from typing import Dict, Tuple

class VaultError(Exception):
    """Base class for vault errors."""
    pass

class CredentialNotFoundError(VaultError):
    """Raised when a credential ID is missing."""
    pass

class QuantumCredentialVault:
    """In‑memory vault protecting credentials with simulated PQ crypto.

    The vault generates a random 256‑bit master secret which is used
    as a symmetric key. To emulate a post‑quantum KEM the master secret
    is wrapped with a hash‑based key‑derivation that would be replaced
    by a real KEM in production.
    """

    def __init__(self) -> None:
        self._master_secret: bytes = self._generate_master_secret()
        self._store: Dict[str, Tuple[bytes, bytes]] = {}  # id -> (nonce, ciphertext)

    @staticmethod
    def _generate_master_secret() -> bytes:
        """Generate a fresh 256‑bit master secret."""
        return secrets.token_bytes(32)

    @staticmethod
    def _derive_key(master: bytes, nonce: bytes) -> bytes:
        """Derive a per‑credential encryption key."""
        return hashlib.sha256(master + nonce).digest()

    @staticmethod
    def _xor(data: bytes, key: bytes) -> bytes:
        """Simple XOR cipher (for demonstration only)."""
        return bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1)))

    def add_credential(self, cred_id: str, secret: str) -> None:
        """Encrypt and store a credential.

        Raises:
            VaultError: If the credential identifier already exists.
        """
        if cred_id in self._store:
            raise VaultError(f"Credential '{cred_id}' already exists.")
        nonce = secrets.token_bytes(16)
        key = self._derive_key(self._master_secret, nonce)
        ciphertext = self._xor(secret.encode('utf-8'), key)
        self._store[cred_id] = (nonce, ciphertext)

    def retrieve_credential(self, cred_id: str) -> str:
        """Decrypt and return a stored credential.

        Raises:
            CredentialNotFoundError: If the credential identifier is unknown.
        """
        try:
            nonce, ciphertext = self._store[cred_id]
        except KeyError as exc:
            raise CredentialNotFoundError(cred_id) from exc
        key = self._derive_key(self._master_secret, nonce)
        plaintext = self._xor(ciphertext, key)
        return plaintext.decode('utf-8')

    def rotate_master_key(self) -> None:
        """Generate a new master secret and re‑encrypt all entries."""
        old_secret = self._master_secret
        self._master_secret = self._generate_master_secret()
        for cred_id, (nonce, ciphertext) in self._store.items():
            # Decrypt with old secret
            old_key = self._derive_key(old_secret, nonce)
            plain = self._xor(ciphertext, old_key)
            # Encrypt with new secret
            new_key = self._derive_key(self._master_secret, nonce)
            new_cipher = self._xor(plain, new_key)
            self._store[cred_id] = (nonce, new_cipher)

    def export_snapshot(self) -> Dict[str, str]:
        """Export the vault contents as a JSON‑serialisable dict."""
        return {
            cred_id: base64.b64encode(nonce + ciphertext).decode('ascii')
            for cred_id, (nonce, ciphertext) in self._store.items()
        }

    @classmethod
    def import_snapshot(cls, snapshot: Dict[str, str]) -> "QuantumCredentialVault":
        """Create a vault from a previously exported snapshot."""
        vault = cls()
        for cred_id, b64 in snapshot.items():
            data = base64.b64decode(b64.encode('ascii'))
            nonce, ciphertext = data[:16], data[16:]
            vault._store[cred_id] = (nonce, ciphertext)
        return vault

if __name__ == "__main__":
    # Simple sanity test
    vault = QuantumCredentialVault()
    vault.add_credential("api_key", "s3cr3t!")
    assert vault.retrieve_credential("api_key") == "s3cr3t!"
    vault.rotate_master_key()
    assert vault.retrieve_credential("api_key") == "s3cr3t!"
    snap = vault.export_snapshot()
    new_vault = QuantumCredentialVault.import_snapshot(snap)
    assert new_vault.retrieve_credential("api_key") == "s3cr3t!"
    print("All tests passed.")
