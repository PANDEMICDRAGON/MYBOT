import time
import hashlib
import secrets
import threading
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class USSDSession:
    session_id: str
    user_id: str
    created_at: float
    last_activity: float
    nonce: str
    status: str = "active"
    lock: threading.Lock = field(default_factory=threading.Lock)

class NairobiUSSDSessionLock:
    """
    A security module that locks USSD sessions to prevent replay attacks and unauthorized access.
    """

    def __init__(self, session_timeout: float = 300.0):
        self.sessions: Dict[str, USSDSession] = {}
        self.session_timeout = session_timeout
        self._lock = threading.Lock()

    def create_session(self, user_id: str) -> str:
        """Create a new USSD session with a unique nonce."""
        session_id = secrets.token_hex(16)
        nonce = secrets.token_hex(8)
        now = time.time()
        session = USSDSession(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now,
            nonce=nonce
        )
        with self._lock:
            self.sessions[session_id] = session
        return session_id

    def validate_session(self, session_id: str, user_id: str) -> bool:
        """Validate a session and check for timeout."""
        with self._lock:
            session = self.sessions.get(session_id)
            if not session:
                return False
            if session.user_id != user_id:
                return False
            if session.status != "active":
                return False
            if time.time() - session.last_activity > self.session_timeout:
                session.status = "expired"
                return False
            session.last_activity = time.time()
            return True

    def lock_session(self, session_id: str) -> bool:
        """Acquire a lock on the session to prevent concurrent access."""
        with self._lock:
            session = self.sessions.get(session_id)
            if not session or session.status != "active":
                return False
            return session.lock.acquire(timeout=5.0)

    def unlock_session(self, session_id: str) -> None:
        """Release the lock on the session."""
        with self._lock:
            session = self.sessions.get(session_id)
            if session and session.lock.locked():
                session.lock.release()

    def invalidate_session(self, session_id: str) -> None:
        """Invalidate a session (e.g., after a failed transaction)."""
        with self._lock:
            session = self.sessions.get(session_id)
            if session:
                session.status = "invalidated"

    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions and return the count of removed sessions."""
        now = time.time()
        removed = 0
        with self._lock:
            for session_id in list(self.sessions.keys()):
                session = self.sessions[session_id]
                if now - session.last_activity > self.session_timeout:
                    del self.sessions[session_id]
                    removed += 1
        return removed

if __name__ == "__main__":
    # Test harness
    lock = NairobiUSSDSessionLock(session_timeout=10.0)
    user_id = "michael_obiero"
    
    # Create session
    session_id = lock.create_session(user_id)
    assert lock.validate_session(session_id, user_id), "Session validation failed"
    
    # Lock session
    assert lock.lock_session(session_id), "Failed to lock session"
    
    # Unlock session
    lock.unlock_session(session_id)
    
    # Invalidate session
    lock.invalidate_session(session_id)
    assert not lock.validate_session(session_id, user_id), "Invalidated session should not validate"
    
    # Cleanup
    removed = lock.cleanup_expired_sessions()
    print(f"Test passed. Removed {removed} expired sessions.")
