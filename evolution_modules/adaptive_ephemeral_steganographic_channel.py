"""
Adaptive Ephemeral Steganographic Channel Module.

Provides covert, zero-trust telemetry and command channels by embedding encrypted
payloads into benign carrier JSON messages using unicode zero-width steganography.
Designed for operational continuity and anti-surveillance in high-threat network environments.
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any, Dict, List, Optional, Tuple


class SteganographicChannel:
    """Covert communications channel leveraging Zero-Width Unicode Steganography.

    Attributes:
        shared_secret (bytes): Pre-shared cryptographic secret for HMAC and keystream derivation.
    """

    BIT_0 = "\u200b"  # Zero-Width Space
    BIT_1 = "\u200c"  # Zero-Width Non-Joiner
    MARKER = "\u200d"  # Zero-Width Joiner (Delimiter)

    def __init__(self, shared_secret: Optional[bytes] = None) -> None:
        """Initialize the steganographic channel with a shared secret key."""
        if shared_secret is None:
            self.shared_secret = secrets.token_bytes(32)
        else:
            self.shared_secret = shared_secret

    def _derive_keys(self, salt: bytes) -> Tuple[bytes, bytes]:
        """Derive encryption and authentication keys using HMAC-SHA256 KDF."""
        key_enc = hmac.new(self.shared_secret, salt + b"STEGO_ENC_V1", hashlib.sha256).digest()
        key_mac = hmac.new(self.shared_secret, salt + b"STEGO_MAC_V1", hashlib.sha256).digest()
        return key_enc, key_mac

    def _keystream(self, key: bytes, length: int) -> bytes:
        """Generate a deterministic XOR keystream based on HMAC-SHA256."""
        stream = bytearray()
        counter = 0
        while len(stream) < length:
            block = hmac.new(key, counter.to_bytes(4, "big"), hashlib.sha256).digest()
            stream.extend(block)
            counter += 1
        return bytes(stream[:length])

    def encrypt(self, payload_data: bytes) -> bytes:
        """Encrypt payload data with HMAC-SHA256 authentication."""
        salt = secrets.token_bytes(16)
        key_enc, key_mac = self._derive_keys(salt)
        keystream = self._keystream(key_enc, len(payload_data))
        ciphertext = bytes(p ^ k for p, k in zip(payload_data, keystream))
        mac = hmac.new(key_mac, ciphertext, hashlib.sha256).digest()[:16]
        return salt + mac + ciphertext

    def decrypt(self, encrypted_bundle: bytes) -> bytes:
        """Decrypt and verify authentication MAC of encrypted payload."""
        if len(encrypted_bundle) < 32:
            raise ValueError("Invalid encrypted payload bundle: buffer truncated.")
        salt = encrypted_bundle[:16]
        mac = encrypted_bundle[16:32]
        ciphertext = encrypted_bundle[32:]

        key_enc, key_mac = self._derive_keys(salt)
        expected_mac = hmac.new(key_mac, ciphertext, hashlib.sha256).digest()[:16]

        if not hmac.compare_digest(mac, expected_mac):
            raise ValueError("Integrity verification failed: MAC mismatch.")

        keystream = self._keystream(key_enc, len(ciphertext))
        return bytes(c ^ k for c, k in zip(ciphertext, keystream))

    def _bytes_to_stego(self, data: bytes) -> str:
        """Convert binary bytes into zero-width unicode character sequence."""
        stego_chars = [self.MARKER]
        for byte in data:
            for bit_idx in range(7, -1, -1):
                bit = (byte >> bit_idx) & 1
                stego_chars.append(self.BIT_1 if bit else self.BIT_0)
        stego_chars.append(self.MARKER)
        return "".join(stego_chars)

    def _stego_to_bytes(self, stego_str: str) -> bytes:
        """Extract and parse zero-width unicode sequence back to raw bytes."""
        start = stego_str.find(self.MARKER)
        end = stego_str.rfind(self.MARKER)
        if start == -1 or end == -1 or start == end:
            raise ValueError("No valid steganographic delimiters found in payload.")

        core = stego_str[start + 1 : end]
        bits = []
        for char in core:
            if char == self.BIT_0:
                bits.append(0)
            elif char == self.BIT_1:
                bits.append(1)

        if len(bits) % 8 != 0:
            raise ValueError("Malformed bit sequence in steganographic string.")

        result = bytearray()
        for i in range(0, len(bits), 8):
            byte_val = 0
            for bit in bits[i : i + 8]:
                byte_val = (byte_val << 1) | bit
            result.append(byte_val)

        return bytes(result)

    def embed_secret_in_carrier(self, secret: Dict[str, Any], carrier: Dict[str, Any], target_field: str) -> Dict[str, Any]:
        """Embed a secret dictionary covertly inside a carrier dictionary field."""
        if target_field not in carrier or not isinstance(carrier[target_field], str):
            raise KeyError(f"Target field '{target_field}' must exist and be a string in carrier.")

        secret_json = json.dumps(secret, separators=(",", ":")).encode("utf-8")
        encrypted_data = self.encrypt(secret_json)
        stego_tail = self._bytes_to_stego(encrypted_data)

        modified_carrier = carrier.copy()
        modified_carrier[target_field] = carrier[target_field] + stego_tail
        return modified_carrier

    def extract_secret_from_carrier(self, carrier: Dict[str, Any], target_field: str) -> Dict[str, Any]:
        """Extract and decrypt secret dictionary embedded inside a carrier dictionary field."""
        if target_field not in carrier or not isinstance(carrier[target_field], str):
            raise KeyError(f"Target field '{target_field}' missing or invalid in carrier.")

        field_val = carrier[target_field]
        encrypted_bytes = self._stego_to_bytes(field_val)
        decrypted_json = self.decrypt(encrypted_bytes)
        return json.loads(decrypted_json.decode("utf-8"))


if __name__ == "__main__":
    key = secrets.token_bytes(32)
    channel = SteganographicChannel(shared_secret=key)

    benign_carrier = {
        "status": "OPERATIONAL",
        "timestamp": time.time(),
        "node_id": "NAIROBI_EDGE_NODE_01",
        "message": "Routine telemetry heartbeat - all systems green.",
    }

    covert_secret = {
        "command": "EXECUTE_SHIELD_OVERRIDE",
        "target": "PERIMETER_FIREWALL",
        "operator": "Michael Obiero",
        "location": "Nairobi, Kenya",
        "auth_nonce": secrets.token_hex(8),
    }

    stego_carrier = channel.embed_secret_in_carrier(covert_secret, benign_carrier, target_field="message")
    extracted_secret = channel.extract_secret_from_carrier(stego_carrier, target_field="message")

    assert extracted_secret["command"] == covert_secret["command"]
    assert extracted_secret["operator"] == covert_secret["operator"]
    print("STEGANOGRAPHIC CHANNEL VERIFICATION SUCCESSFUL!")
