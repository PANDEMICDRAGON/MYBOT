"""
HMAC-SHA256 Payload Integrity Signer & Replay Protector.
Generated autonomously by Cortana Continuous Self-Evolution Core.
"""

import hmac
import hashlib
import time

class PayloadSigner:
    """Signs and verifies JSON payloads using HMAC-SHA256 with timestamp anti-replay."""
    @staticmethod
    def sign(data_str: str, secret_key: str) -> str:
        ts = str(int(time.time()))
        message = f"{ts}:{data_str}".encode("utf-8")
        sig = hmac.new(secret_key.encode("utf-8"), message, hashlib.sha256).hexdigest()
        return f"{ts}:{sig}"

    @staticmethod
    def verify(data_str: str, signature_header: str, secret_key: str, max_age_secs: int = 300) -> bool:
        try:
            ts_str, sig = signature_header.split(":", 1)
            ts = int(ts_str)
            if abs(time.time() - ts) > max_age_secs:
                return False
            message = f"{ts_str}:{data_str}".encode("utf-8")
            expected = hmac.new(secret_key.encode("utf-8"), message, hashlib.sha256).hexdigest()
            return hmac.compare_digest(sig, expected)
        except Exception:
            return False

if __name__ == "__main__":
    secret = "cortana_secret_salt"
    payload = '{"cmd": "status"}'
    token = PayloadSigner.sign(payload, secret)
    assert PayloadSigner.verify(payload, token, secret) is True
    assert PayloadSigner.verify(payload + "tamper", token, secret) is False
    print("PayloadSigner verified.")
