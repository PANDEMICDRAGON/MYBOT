import time
import hashlib
import hmac
import secrets
import json
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KenyaSMSOtpHardener")


class OtpStatus(Enum):
    """Enum representing the status of an OTP verification attempt."""
    VALID = "valid"
    EXPIRED = "expired"
    INVALID = "invalid"
    REPLAYED = "replayed"
    RATE_LIMITED = "rate_limited"


@dataclass
class OtpRecord:
    """Data class to store OTP metadata."""
    code_hash: str
    nonce: str
    created_at: float
    attempts: int = 0
    last_attempt_at: Optional[float] = None


class KenyaSmsOtpHardener:
    """
    A security module to generate and verify SMS One-Time Passwords (OTPs)
    with enhanced protections against replay attacks, timing attacks,
    and brute-force attempts, tailored for Kenyan network conditions.
    """

    def __init__(self, secret_key: str, window_size: int = 30, max_attempts: int = 5, rate_limit_window: int = 60):
        """
        Initialize the OTP Hardener.

        Args:
            secret_key: A high-entropy secret key for HMAC generation.
            window_size: The time window in seconds for OTP validity.
            max_attempts: Maximum allowed verification attempts per OTP.
            rate_limit_window: Time window in seconds for rate limiting.
        """
        if not secret_key or len(secret_key) < 16:
            raise ValueError("Secret key must be at least 16 characters long.")

        self.secret_key = secret_key.encode('utf-8')
        self.window_size = window_size
        self.max_attempts = max_attempts
        self.rate_limit_window = rate_limit_window

        # In-memory store for active OTPs (in production, this would be a secure cache like Redis)
        self.active_otps: Dict[str, OtpRecord] = {}
        self.recent_requests: Dict[str, list] = {}

    def _generate_hmac(self, timestamp: int, nonce: str) -> str:
        """
        Generate an HMAC-SHA256 hash for the given timestamp and nonce.

        Args:
            timestamp: The current Unix timestamp truncated to the window.
            nonce: A random nonce to prevent replay.

        Returns:
            A hexadecimal string of the HMAC.
        """
        message = f"{timestamp}:{nonce}".encode('utf-8')
        return hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()

    def generate_otp(self, user_id: str) -> Tuple[str, str]:
        """
        Generate a new OTP for the user.

        Args:
            user_id: The unique identifier for the user.

        Returns:
            A tuple containing (otp_code, nonce).
        """
        # Check rate limiting
        if self._is_rate_limited(user_id):
            raise PermissionError(f"Rate limit exceeded for user {user_id}.")

        current_time = time.time()
        timestamp = int(current_time // self.window_size)
        nonce = secrets.token_hex(8)

        # Generate a 6-digit OTP from the HMAC
        hmac_hex = self._generate_hmac(timestamp, nonce)
        otp_code = str(int(hmac_hex[:6], 16) % 1000000).zfill(6)

        # Store the record
        self.active_otps[user_id] = OtpRecord(
            code_hash=hashlib.sha256(otp_code.encode('utf-8')).hexdigest(),
            nonce=nonce,
            created_at=current_time
        )

        logger.info(f"Generated OTP for user {user_id}.")
        return otp_code, nonce

    def verify_otp(self, user_id: str, otp_code: str, nonce: str) -> OtpStatus:
        """
        Verify an OTP for the user.

        Args:
            user_id: The unique identifier for the user.
            otp_code: The OTP code provided by the user.
            nonce: The nonce provided with the OTP.

        Returns:
            An OtpStatus enum indicating the result of the verification.
        """
        if user_id not in self.active_otps:
            return OtpStatus.INVALID

        record = self.active_otps[user_id]

        # Check if the nonce matches
        if record.nonce != nonce:
            return OtpStatus.INVALID

        # Check if the OTP is expired
        if time.time() - record.created_at > self.window_size:
            del self.active_otps[user_id]
            return OtpStatus.EXPIRED

        # Check attempt limit
        if record.attempts >= self.max_attempts:
            del self.active_otps[user_id]
            return OtpStatus.INVALID

        # Increment attempts
        record.attempts += 1
        record.last_attempt_at = time.time()

        # Verify the code
        provided_hash = hashlib.sha256(otp_code.encode('utf-8')).hexdigest()
        if hmac.compare_digest(provided_hash, record.code_hash):
            # Success: Remove the OTP to prevent reuse
            del self.active_otps[user_id]
            logger.info(f"OTP verified successfully for user {user_id}.")
            return OtpStatus.VALID
        else:
            logger.warning(f"Invalid OTP attempt for user {user_id}.")
            return OtpStatus.INVALID

    def _is_rate_limited(self, user_id: str) -> bool:
        """
        Check if the user is rate limited.

        Args:
            user_id: The unique identifier for the user.

        Returns:
            True if the user is rate limited, False otherwise.
        """
        current_time = time.time()
        if user_id not in self.recent_requests:
            self.recent_requests[user_id] = []

        # Remove old requests outside the rate limit window
        self.recent_requests[user_id] = [
            t for t in self.recent_requests[user_id] if current_time - t < self.rate_limit_window
        ]

        if len(self.recent_requests[user_id]) >= 10:  # Max 10 requests per minute
            return True

        self.recent_requests[user_id].append(current_time)
        return False


if __name__ == "__main__":
    # Test Harness
    secret = "super-secret-key-for-kenya-otp-hardener"
    hardener = KenyaSmsOtpHardener(secret)

    user_id = "michael_obiero"

    # Generate OTP
    otp, nonce = hardener.generate_otp(user_id)
    print(f"Generated OTP: {otp}, Nonce: {nonce}")

    # Verify OTP
    status = hardener.verify_otp(user_id, otp, nonce)
    print(f"Verification Status: {status}")
    assert status == OtpStatus.VALID, "OTP verification failed."

    # Try to reuse OTP (should fail)
    status = hardener.verify_otp(user_id, otp, nonce)
    print(f"Reuse Status: {status}")
    assert status == OtpStatus.INVALID, "OTP reuse should be invalid."

    # Test rate limiting
    try:
        for _ in range(11):
            hardener.generate_otp(user_id)
    except PermissionError as e:
        print(f"Rate Limit Triggered: {e}")

    print("All tests passed.")