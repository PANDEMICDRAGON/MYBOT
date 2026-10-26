import ast
import hashlib
import hmac
import logging
import os
import time
from typing import Dict, Any, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("OfflineVoiceSynapse")

class OfflineVoiceSynapse:
    """
    Provides secure, offline voice-command parsing, deterministic audio feature hashing,
    and cryptographic voiceprint verification for operator Michael Obiero in Nairobi.
    Ensures local command execution without cloud reliance or data leakage.
    """
    def __init__(self, authorized_operator_hash: str, salt: bytes = b"nairobi_voice_salt_v1"):
        self.authorized_operator_hash = authorized_operator_hash
        self.salt = salt
        self.command_registry: Dict[str, callable] = {}
        self.audit_log: list = []
        logger.info("OfflineVoiceSynapse initialized for Nairobi operational theater.")

    def register_command(self, phrase_slug: str, callback: callable) -> None:
        """Register an execution callback for a verified voice command slug."""
        self.command_registry[phrase_slug] = callback
        logger.debug(f"Registered secure voice command slug: {phrase_slug}")

    def _extract_spectral_features(self, audio_buffer: bytes) -> str:
        """
        Simulates localized FFT and Mel-Frequency Cepstral Coefficients (MFCC) feature extraction
        producing a deterministic cryptographic representation of the voice sample.
        """
        hasher = hashlib.blake2b(digest_size=32, salt=self.salt)
        hasher.update(audio_buffer)
        return hasher.hexdigest()

    def verify_voiceprint(self, audio_buffer: bytes) -> bool:
        """
        Cryptographically compares incoming audio biometric features against the registered operator hash.
        """
        try:
            sample_hash = self._extract_spectral_features(audio_buffer)
            # Constant-time comparison to prevent timing attacks
            is_verified = hmac.compare_digest(sample_hash, self.authorized_operator_hash)
            if not is_verified:
                logger.warning("Voiceprint verification FAILED: Unauthorized or corrupted audio sample.")
            return is_verified
        except Exception as e:
            logger.error(f"Error during voiceprint verification: {e}")
            return False

    def execute_command(self, audio_buffer: bytes, phrase_slug: str, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Validates operator voiceprint and executes the requested command securely if authorized.
        """
        timestamp = time.time()
        if not self.verify_voiceprint(audio_buffer):
            self.audit_log.append({"timestamp": timestamp, "slug": phrase_slug, "status": "REJECTED_UNAUTHORIZED"})
            return False, "Voice biometric authorization failed."

        if phrase_slug not in self.command_registry:
            self.audit_log.append({"timestamp": timestamp, "slug": phrase_slug, "status": "REJECTED_UNKNOWN_COMMAND"})
            return False, f"Unknown command slug: {phrase_slug}"

        try:
            callback = self.command_registry[phrase_slug]
            result = callback(context or {})
            self.audit_log.append({"timestamp": timestamp, "slug": phrase_slug, "status": "SUCCESS"})
            logger.info(f"Voice command '{phrase_slug}' executed successfully for operator.")
            return True, str(result)
        except Exception as e:
            logger.error(f"Command execution fault on '{phrase_slug}': {e}")
            self.audit_log.append({
                "timestamp": timestamp,
                "slug": phrase_slug,
                "status": "FAULT",
                "error": str(e)
            })
            return False, f"Execution fault: {e}"

if __name__ == "__main__":
    # Test Harness for OfflineVoiceSynapse
    test_audio = b"SIMULATED_MIC_STREAM_OBIER0_VOICE_SAMPLE_NAIROBI"
    hasher = hashlib.blake2b(digest_size=32, salt=b"nairobi_voice_salt_v1")
    hasher.update(test_audio)
    correct_hash = hasher.hexdigest()

    synapse = OfflineVoiceSynapse(authorized_operator_hash=correct_hash)
    
    def sample_grid_action(ctx):
        return "Nairobi Solar Grid Arbitrage manually overridden via voice."

    synapse.register_command("override_solar_grid", sample_grid_action)

    # Test successful verification & execution
    success, res = synapse.execute_command(test_audio, "override_solar_grid")
    assert success, "Test voice command failed verification"
    print(f"Test Execution Result: {res}")

    # Test unauthorized voice
    unauthorized_audio = b"SOME_RANDOM_INTRUDER_VOICE"
    fail_success, fail_res = synapse.execute_command(unauthorized_audio, "override_solar_grid")
    assert not fail_success, "Security breach: Unauthorized voice passed validation!"
    print(f"Security Intercept Confirmed: {fail_res}")

    # Validate syntax cleanliness
    code_string = open(__file__, "r", encoding="utf-8").read()
    ast.parse(code_string)
    print("AST parsing verified clean for offline_voice_synapse.py")
