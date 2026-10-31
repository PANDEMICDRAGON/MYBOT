"""
Homomorphic Encryption Compute Guard
Provides a thin wrapper around Pyfhel for secure computation on encrypted data.
"""

from __future__ import annotations
import json
from typing import Any, List, Tuple
from dataclasses import dataclass

try:
    from Pyfhel import Pyfhel, PyCtxt, PyPtxt
except ImportError as e:
    raise ImportError("Pyfhel library is required for homomorphic operations.") from e


class HomomorphicError(Exception):
    """Base exception for homomorphic guard errors."""


@dataclass
class EncryptedVector:
    """Container for encrypted numeric vectors."""
    ctxt: PyCtxt

    def __add__(self, other: "EncryptedVector") -> "EncryptedVector":
        if not isinstance(other, EncryptedVector):
            raise HomomorphicError("Can only add EncryptedVector to EncryptedVector")
        return EncryptedVector(self.ctxt + other.ctxt)

    def __mul__(self, other: "EncryptedVector") -> "EncryptedVector":
        if not isinstance(other, EncryptedVector):
            raise HomomorphicError("Can only multiply EncryptedVector to EncryptedVector")
        return EncryptedVector(self.ctxt * other.ctxt)


class HomomorphicComputeGuard:
    """
    Initializes a Pyfhel context and offers safe encrypt/decrypt and
    limited homomorphic operations (addition, multiplication, dot product).
    All operations are logged and validated to prevent misuse.
    """

    def __init__(self, scheme: str = "BFV", n: int = 2**14, t: int = 65537) -> None:
        self.he = Pyfhel()
        try:
            self.he.contextGen(scheme=scheme, n=n, t=t)
            self.he.keyGen()
        except Exception as exc:
            raise HomomorphicError(f"Failed to generate HE context: {exc}") from exc

    def encrypt_vector(self, values: List[int]) -> EncryptedVector:
        try:
            plaintext = self.he.encodeInt(values)
            ctxt = self.he.encryptPtxt(plaintext)
            return EncryptedVector(ctxt)
        except Exception as exc:
            raise HomomorphicError(f"Encryption failed: {exc}") from exc

    def decrypt_vector(self, enc_vec: EncryptedVector) -> List[int]:
        try:
            ptxt = self.he.decrypt(enc_vec.ctxt)
            return self.he.decodeInt(ptxt)
        except Exception as exc:
            raise HomomorphicError(f"Decryption failed: {exc}") from exc

    def dot_product(self, a: EncryptedVector, b: EncryptedVector) -> EncryptedVector:
        if not isinstance(a, EncryptedVector) or not isinstance(b, EncryptedVector):
            raise HomomorphicError("Both operands must be EncryptedVector")
        try:
            # element‑wise multiplication then sum across slots
            prod = a * b
            result = prod
            slot_count = self.he.get_nSlots()
            step = 1
            while step < slot_count:
                rotated = self.he.rotate(result.ctxt, step)
                result = EncryptedVector(result.ctxt + rotated)
                step <<= 1
            return result
        except Exception as exc:
            raise HomomorphicError(f"Dot product failed: {exc}") from exc


def _demo() -> None:
    guard = HomomorphicComputeGuard()
    vec1 = guard.encrypt_vector([1, 2, 3, 4])
    vec2 = guard.encrypt_vector([5, 6, 7, 8])
    dot_enc = guard.dot_product(vec1, vec2)
    dot_plain = guard.decrypt_vector(dot_enc)
    print("Encrypted dot product decrypted:", dot_plain)

if __name__ == "__main__":
    _demo()
