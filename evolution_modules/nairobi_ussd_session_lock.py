import time
import hashlib
import hmac
import secrets
import threading
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SessionState(Enum):
    IDLE = "idle"
    ACTIVE = "active"
    LOCKED = "locked"
    EXPIRED = "expired"


@dataclass
class USSDSession:
    session_id: str
    user_id: str
    created_at: float
    last_activity: float
    state: SessionState = SessionState.IDLE
    nonce: Optional[str] = None
    nonce_hash: Optional[str] = None
    attempt_count: int = 0
    lock_until: Optional[float] = None
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def is_locked(self) -> bool:
        return self.state == SessionState.LOCKED or (self.lock_until and time.time() < self.lock_until)

    def is_expired(self, timeout: float = 300.0) -> bool:
        return time.time() - self.last_activity > timeout


class USSDSessionLock:
    """
    A security module to protect USSD sessions from replay attacks and concurrent hijacking.
    """

    def __init__(self, secret_key: str, session_timeout: float = 300.0, max_attempts: int = 5):
        self.secret_key = secret_key.encode()
        self.session_timeout = session_timeout
        self.max_attempts = max_attempts
        self.sessions: Dict[str, USSDSession] = {}
        self._global_lock = threading.Lock()

    def _generate_nonce(self) -> str:
        return secrets.token_hex(16)

    def _compute_nonce_hash(self, nonce: str) -> str:
        return hmac.new(self.secret_key, nonce.encode(), hashlib.sha256).hexdigest()

    def start_session(self, user_id: str) -> Tuple[bool, str, Optional[str]]:
        """
        Start a new USSD session.
        Returns: (success, session_id, nonce)
        """
        with self._global_lock:
            # Check for existing active session
            for session in self.sessions.values():
                if session.user_id == user_id and session.state == SessionState.ACTIVE:
                    return False, session.session_id, None

            session_id = secrets.token_hex(8)
            nonce = self._generate_nonce()
            nonce_hash = self._compute_nonce_hash(nonce)

            session = USSDSession(
                session_id=session_id,
                user_id=user_id,
                created_at=time.time(),
                last_activity=time.time(),
                state=SessionState.ACTIVE,
                nonce=nonce,
                nonce_hash=nonce_hash
            )
            self.sessions[session_id] = session
            logger.info(f"Started USSD session {session_id} for user {user_id}")
            return True, session_id, nonce

    def validate_transaction(self, session_id: str, nonce: str, payload: str) -> bool:
        """
        Validate a USSD transaction using nonce-based replay protection.
        """
        with self._global_lock:
            session = self.sessions.get(session_id)
            if not session:
                logger.warning(f"Invalid session ID: {session_id}")
                return False

            if session.is_locked():
                logger.warning(f"Session {session_id} is locked")
                return False

            if session.is_expired(self.session_timeout):
                session.state = SessionState.EXPIRED
                logger.warning(f"Session {session_id} expired")
                return False

            # Check nonce replay
            if session.nonce != nonce:
                session.attempt_count += 1
                if session.attempt_count >= self.max_attempts:
                    self._lock_session(session)
                logger.warning(f"Nonce mismatch for session {session_id}, attempt {session.attempt_count}")
                return False

            # Validate payload integrity (simplified HMAC check)
            expected_hash = hmac.new(self.secret_key, payload.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected_hash, session.nonce_hash):
                session.attempt_count += 1
                if session.attempt_count >= self.max_attempts:
                    self._lock_session(session)
                logger.warning(f"Payload integrity check failed for session {session_id}")
                return False

            # Success: update last activity and invalidate nonce
            session.last_activity = time.time()
            session.nonce = None
            session.nonce_hash = None
            session.attempt_count = 0
            logger.info(f"Transaction validated for session {session_id}")
            return True

    def _lock_session(self, session: USSDSession):
        session.state = SessionState.LOCKED
        session.lock_until = time.time() + 300  # Lock for 5 minutes
        logger.error(f"Session {session.session_id} locked due to multiple failed attempts")

    def end_session(self, session_id: str) -> bool:
        with self._global_lock:
            session = self.sessions.pop(session_id, None)
            if session:
                logger.info(f"Ended USSD session {session_id}")
                return True
            return False

    def get_session_status(self, session_id: str) -> Optional[Dict]:
        with self._global_lock:
            session = self.sessions.get(session_id)
            if not session:
                return None
            return {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "state": session.state.value,
                "is_locked": session.is_locked(),
                "is_expired": session.is_expired(self.session_timeout),
                "attempt_count": session.attempt_count
            }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    shield = USSDSessionLock(secret_key="test-secret-key")

    # Test 1: Start session
    success, session_id, nonce = shield.start_session("user123")
    assert success, "Session start failed"
    assert nonce is not None, "Nonce not generated"
    print(f"Session started: {session_id}, Nonce: {nonce}")

    # Test 2: Valid transaction
    payload = "*182*0*100#"
    valid = shield.validate_transaction(session_id, nonce, payload)
    assert valid, "Valid transaction failed"
    print("Valid transaction accepted")

    # Test 3: Replay attack (same nonce)
    replay = shield.validate_transaction(session_id, nonce, payload)
    assert not replay, "Replay attack should fail"
    print("Replay attack blocked")

    # Test 4: Invalid nonce
    invalid = shield.validate_transaction(session_id, "wrong-nonce", payload)
    assert not invalid, "Invalid nonce should fail"
    print("Invalid nonce blocked")

    # Test 5: End session
    ended = shield.end_session(session_id)
    assert ended, "Session end failed"
    print("Session ended")

    print("All USSD Session Lock tests passed.")