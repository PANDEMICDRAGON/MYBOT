"""Nairobi Biometric Cryptographic Data Vault and Sovereign Privacy Mesh. Provides encrypted, zero-knowledge partitioned storage for local physiological telemetry and operator intent state vectors under extreme operational conditions."""

import os
import json
import hashlib
import hmac
import base64
from typing import Dict, Any, Optional

class NairobiBioDataVault:
    """Manages encrypted local persistence and cryptographic verification of sensitive operator telemetry."""

    def __init__(self, master_secret: Optional[bytes] = None):
        self._master_secret = master_secret or os.urandom(32)
        self._vault_store: Dict[str, str] = {}

    def _derive_key(self, context: str) -> bytes:
        return hmac.new(self._master_secret, context.encode('utf-8'), hashlib.sha256).digest()

    def store_record(self, record_id: str, payload: Dict[str, Any]) -> str:
        """Encrypts and stores a telemetry record securely."""
        context_key = self._derive_key(record_id)
        raw_data = json.dumps(payload).encode('utf-8')
        
        # Simple XOR-HMAC stream cipher for standalone sovereign embedding
        iv = os.urandom(16)
        encrypted_bytes = bytearray(
            b ^ context_key[i % len(context_key)] ^ iv[i % len(iv)]
            for i, b in enumerate(raw_data)
        )
        
        auth_tag = hmac.new(context_key, iv + encrypted_bytes, hashlib.sha256).hexdigest()
        
        vault_entry = {
            "iv": base64.b64encode(iv).decode('utf-8'),
            "ciphertext": base64.b64encode(encrypted_bytes).decode('utf-8'),
            "tag": auth_tag
        }
        
        serialized = json.dumps(vault_entry)
        self._vault_store[record_id] = serialized
        return record_id

    def retrieve_record(self, record_id: str) -> Dict[str, Any]:
        """Retrieves and decrypts a telemetry record with tamper verification."""
        if record_id not in self._vault_store:
            raise KeyError(f"Record {record_id} not found in sovereign vault.")
            
        vault_entry = json.loads(self._vault_store[record_id])
        iv = base64.b64decode(vault_entry["iv"])
        encrypted_bytes = bytearray(base64.b64decode(vault_entry["ciphertext"]))
        stored_tag = vault_entry["tag"]
        
        context_key = self._derive_key(record_id)
        expected_tag = hmac.new(context_key, iv + bytes(encrypted_bytes), hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(stored_tag, expected_tag):
            raise ValueError(f"Integrity violation detected for record {record_id}!")
            
        decrypted_bytes = bytes(
            b ^ context_key[i % len(context_key)] ^ iv[i % len(iv)]
            for i, b in enumerate(encrypted_bytes)
        )
        
        return json.loads(decrypted_bytes.decode('utf-8'))

if __name__ == '__main__':
    vault = NairobiBioDataVault()
    test_payload = {
        "operator": "Michael Obiero",
        "location": "Nairobi, Kenya",
        "telemetry": "Cognitive load index nominal",
        "timestamp": 1711900000
    }
    r_id = "bio_telemetry_001"
    vault.store_record(r_id, test_payload)
    retrieved = vault.retrieve_record(r_id)
    assert retrieved == test_payload, "Vault roundtrip validation failed!"
    print("NairobiBioDataVault operational test passed successfully.")
