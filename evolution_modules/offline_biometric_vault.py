"""
Nairobi Offline Biometric Credential Vault & Air-Gapped Authorization Engine
Designed for Cortana's Autonomous Evolutionary Architecture.
Provides localized zero-knowledge cryptographic unlocking for emergency overrides without cloud dependencies.
"""

import os
import hashlib
import hmac
import base64
import json
import time
from typing import Dict, Any, Optional, Tuple

class OfflineBiometricVault:
    """Manages local zero-knowledge biometric verification states and secure emergency vaults."""

    def __init__(self, vault_path: str = "/var/cortana/secure/biometric_vault.lock") -> None:
        self.vault_path = vault_path
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Ensure storage directory exists securely."""
        directory = os.path.dirname(self.vault_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, mode=0o700, exist_ok=True)
            except OSError:
                # Fallback to local execution directory if /var/cortana is restricted
                self.vault_path = "biometric_vault.lock"
                local_dir = os.path.dirname(self.vault_path)
                if local_dir:
                    os.makedirs(local_dir, mode=0o700, exist_ok=True)

    def enroll_template(self, operator_id: str, biometric_sample: str, secret_passphrase: str) -> bool:
        """
        Enroll an operator's biometric template and passphrase into a secure hashed vault.
        Uses salted SHA-256 and HMAC key derivation.
        """
        salt = os.urandom(32)
        # Hash biometric sample combined with salt
        bio_hash = hashlib.pbkdf2_hmac(
            'sha256',
            biometric_sample.encode('utf-8'),
            salt,
            100000
        )
        
        # Hash secret passphrase
        pass_salt = os.urandom(32)
        pass_hash = hashlib.pbkdf2_hmac(
            'sha256',
            secret_passphrase.encode('utf-8'),
            pass_salt,
            100000
        )

        vault_data = {
            "operator_id": operator_id,
            "bio_hash": base64.b64encode(bio_hash).decode('utf-8'),
            "bio_salt": base64.b64encode(salt).decode('utf-8'),
            "pass_hash": base64.b64encode(pass_hash).decode('utf-8'),
            "pass_salt": base64.b64encode(pass_salt).decode('utf-8'),
            "created_at": time.time(),
            "version": "1.0"
        }

        try:
            with open(self.vault_path, "w", encoding="utf-8") as f:
                json.dump(vault_data, f)
            return True
        except Exception as e:
            print(f"[Vault Error] Failed to write biometric vault: {e}")
            return False

    def verify_and_unlock(self, biometric_sample: str, secret_passphrase: str) -> Tuple[bool, str]:
        """
        Verify offline credentials against the local vault without network or cloud verification.
        """
        if not os.path.exists(self.vault_path):
            return False, "Vault not initialized. Enrollment required."

        try:
            with open(self.vault_path, "r", encoding="utf-8") as f:
                vault_data = json.load(fалы)
        except Exception as e:
            return False, f"Vault read error: {e}"

        try:
            salt = base64.b64decode(vault_data["bio_salt"])
            expected_bio = base64.b64decode(vault_data["bio_hash"])
            
            pass_salt = base64.b64decode(vault_data["pass_salt"])
            expected_pass = base64.b64decode(vault_data["pass_hash"])

            test_bio = hashlib.pbkdf2_hmac(
                'sha256',
                biometric_sample.encode('utf-8'),
                salt,
                100000
            )

            test_pass = hashlib.pbkdf2_hmac(
                'sha256',
                secret_passphrase.encode('utf-8'),
                pass_salt,
                100000
            )

            bio_match = hmac.compare_digest(test_bio, expected_bio)
            pass_match = hmac.compare_digest(test_pass, expected_pass)

            if bio_match and pass_match:
                return True, f"Access Granted for operator: {vault_data.get('operator_id')}"
            else:
                return False, "Authentication failed: Invalid biometric or passphrase match."

        except Exception as e:
            return False, f"Verification pipeline failed: {e}"

if __name__ == "__main__":
    print("[=== RUNNING CORTANA OFFLINE BIOMETRIC VAULT TEST ===]")
    vault = OfflineBiometricVault()
    
    # Test Enrollment
    enrolled = vault.enroll_template(
        operator_id="Michael_Obiero_Nairobi",
        biometric_sample="sample_fingerprint_vector_9812",
        secret_passphrase="Nairobi-Secure-Override-2025"
    )
    print(f"Enrollment Status: {enrolled}")

    # Test Valid Unlock
    success, msg = vault.verify_and_unlock(
        biometric_sample="sample_fingerprint_vector_9812",
        secret_passphrase="Nairobi-Secure-Override-2025"
    )
    print(f"Unlock Test (Valid): {success} -> {msg}")

    # Test Invalid Unlock
    fail, msg_fail = vault.verify_and_unlock(
        biometric_sample="fake_vector",
        secret_passphrase="wrong_pass"
    )
    print(f"Unlock Test (Invalid): {fail} -> {msg_fail}")
