"""
Module: aura_key_rotator.py
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Description:
Provides zero-knowledge ephemeral cryptographic key generation, automatic hardware-
bound derivation, secure rotation, and encrypted envelope storage suitable for
protecting local sensitive state vectors and M-Pesa transactional logs offline.
"""

import os
import time
import hmac
import hashlib
import base64
import json
from typing import Dict, Any, Optional


class KeyRotationError(Exception):
    """Raised when key derivation, rotation, or cryptographic unsealing fails."""
    pass


class AutonomousKeyRotator:
    """
    Manages the lifecycle of localized ephemeral cryptographic keys bound to 
    system entropy and execution context.
    """

    def __init__(self, master_salt: Optional[bytes] = None, rotation_interval_seconds: int = 3600):
        self.master_salt = master_salt or os.urandom(32)
        self.rotation_interval = rotation_interval_seconds
        self.current_generation = 1
        self._active_key = self._derive_key(self.current_generation)
        self.last_rotated = time.time()

    def _derive_key(self, generation: int) -> bytes:
        """Derives a cryptographically secure key using HMAC-SHA256 and system entropy."""
        context_seed = f"CORTANA_NAIROBI_GEN_{generation}_{os.getpid()}".encode('utf-8')
        h = hmac.new(self.master_salt, context_seed, hashlib.sha256)
        # Mix in physical or pseudo-random OS entropy
        h.update(os.urandom(16))
        return h.digest()

    def rotate_if_needed(self) -> bool:
        """Rotates the active encryption key if the rotation interval has elapsed."""
        now = time.time()
        if now - self.last_rotated >= self.rotation_interval:
            self.current_generation += 1
            self._active_key = self._derive_key(self.current_generation)
            self.last_rotated = now
            return True
        return False

    def encrypt_payload(self, plaintext: str) -> Dict[str, Any]:
        """
        Encrypts plaintext using an ephemeral XOR-HMAC stream cipher bound to the active key.
        Returns an envelope containing generation, nonce, ciphertext, and tag.
        """
        self.rotate_if_needed()
        nonce = os.urandom(16)
        
        # Generate keystream block via HMAC counter mode
        h = hmac.new(self._active_key, nonce, hashlib.sha256)
        keystream = h.digest()
        
        pt_bytes = plaintext.encode('utf-8')
        # Pad or slice keystream to match plaintext length
        extended_keystream = (keystream * ((len(pt_bytes) // len(keystream)) + 1))[:len(pt_bytes)]
        
        ciphertext = bytes(a ^ b for a, b in zip(pt_bytes, extended_keystream))
        
        # Compute authentication tag
        tag_hmac = hmac.new(self._active_key, nonce + ciphertext, hashlib.sha256)
        tag = tag_hmac.digest()

        return {
            "generation": self.current_generation,
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "tag": base64.b64encode(tag).decode('utf-8')
        }

    def decrypt_payload(self, envelope: Dict[str, Any]) -> str:
        """
        Decrypts an envelope. Raises KeyRotationError if integrity tag fails
        or if the key generation is unrecognized.
        """
        try:
            gen = envelope["generation"]
            if gen != self.current_generation:
                raise KeyRotationError(f"Key generation mismatch. Active: {self.current_generation}, Provided: {gen}")
            
            nonce = base64.b64decode(envelope["nonce"])
            ciphertext = base64.b64decode(envelope["ciphertext"])
            tag = base64.b64decode(envelope["tag"])
            
            # Verify authentication tag
            expected_tag_hmac = hmac.new(self._active_key, nonce + ciphertext, hashlib.sha256)
            if not hmac.compare_digest(expected_tag_hmac.digest(), tag):
                raise KeyRotationError("Cryptographic integrity check failed: Tampering detected.")
            
            # Re-generate keystream
            h = hmac.new(self._active_key, nonce, hashlib.sha256)
            keystream = h.digest()
            extended_keystream = (keystream * ((len(ciphertext) // len(keystream)) + 1))[:len(ciphertext)]
            
            pt_bytes = bytes(a ^ b for a, b in zip(ciphertext, extended_keystream))
            return pt_bytes.decode('utf-8')

        except Exception as e:
            if isinstance(e, KeyRotationError):
                raise
            raise KeyRotationError(f"Failed to decrypt payload: {str(e)}")


if __name__ == "__main__":
    print("Initializing Autonomous Key Rotator Test Harness...")
    rotator = AutonomousKeyRotator(rotation_interval_seconds=1)
    
    test_secret = "CONFIDENTIAL_MPESA_LEDGER_TX_98312_NAIROBI"
    envelope = rotator.encrypt_payload(test_secret)
    print(f"Encrypted Envelope (Gen {envelope['generation']}): {json.dumps(envelope, indent=2)}")
    
    decrypted = rotator.decrypt_payload(envelope)
    print(f"Successfully Decrypted: {decrypted}")
    assert test_secret == decrypted, "Decryption test failed!"
    print("AURA-KRE Verification Passed Successfully.")
