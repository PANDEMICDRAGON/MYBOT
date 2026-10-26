import hashlib
import time
import uuid
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SessionStatus(Enum):
    ACTIVE = "active"
    LOCKED = "locked"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class USSDSession:
    session_id: str
    user_id: str
    device_fingerprint: str
    created_at: float
    expires_at: float
    status: SessionStatus
    last_activity: float
    transaction_hash: Optional[str] = None


class USSDSessionLock:
    """
    A security module to lock and protect USSD sessions in Nairobi.
    Prevents replay attacks, session hijacking, and unauthorized access.
    """

    def __init__(self, session_ttl: int = 300):
        self.sessions: Dict[str, USSDSession] = {}
        self.session_ttl = session_ttl
        self._lock = None  # Placeholder for thread safety if needed

    def create_session(self, user_id: str, device_fingerprint: str) -> str:
        """
        Create a new USSD session.
        
        Args:
            user_id: The unique identifier of the user.
            device_fingerprint: A hash representing the device's unique characteristics.
            
        Returns:
            The session ID.
        """
        session_id = str(uuid.uuid4())
        now = time.time()
        session = USSDSession(
            session_id=session_id,
            user_id=user_id,
            device_fingerprint=device_fingerprint,
            created_at=now,
            expires_at=now + self.session_ttl,
            status=SessionStatus.ACTIVE,
            last_activity=now
        )
        self.sessions[session_id] = session
        return session_id

    def validate_session(self, session_id: str, device_fingerprint: str) -> bool:
        """
        Validate a USSD session.
        
        Args:
            session_id: The session ID to validate.
            device_fingerprint: The device fingerprint to check against.
            
        Returns:
            True if the session is valid, False otherwise.
        """
        session = self.sessions.get(session_id)
        if not session:
            return False

        if session.status != SessionStatus.ACTIVE:
            return False

        if session.device_fingerprint != device_fingerprint:
            return False

        if time.time() > session.expires_at:
            session.status = SessionStatus.EXPIRED
            return False

        session.last_activity = time.time()
        return True

    def lock_session(self, session_id: str, transaction_data: str) -> str:
        """
        Lock a session to a specific transaction to prevent replay.
        
        Args:
            session_id: The session ID to lock.
            transaction_data: The data to bind the session to.
            
        Returns:
            The transaction hash.
        """
        session = self.sessions.get(session_id)
        if not session or session.status != SessionStatus.ACTIVE:
            raise ValueError("Invalid or inactive session")

        transaction_hash = hashlib.sha256(transaction_data.encode()).hexdigest()
        session.transaction_hash = transaction_hash
        session.status = SessionStatus.LOCKED
        return transaction_hash

    def unlock_session(self, session_id: str) -> bool:
        """
        Unlock a session after a transaction is completed.
        
        Args:
            session_id: The session ID to unlock.
            
        Returns:
            True if the session was unlocked, False otherwise.
        """
        session = self.sessions.get(session_id)
        if not session or session.status != SessionStatus.LOCKED:
            return False

        session.status = SessionStatus.ACTIVE
        session.transaction_hash = None
        return True

    def revoke_session(self, session_id: str) -> bool:
        """
        Revoke a session immediately.
        
        Args:
            session_id: The session ID to revoke.
            
        Returns:
            True if the session was revoked, False otherwise.
        """
        session = self.sessions.get(session_id)
        if not session:
            return False

        session.status = SessionStatus.REVOKED
        return True

    def get_session_status(self, session_id: str) -> Optional[SessionStatus]:
        """
        Get the status of a session.
        
        Args:
            session_id: The session ID to check.
            
        Returns:
            The session status, or None if the session does not exist.
        """
        session = self.sessions.get(session_id)
        if not session:
            return None

        if time.time() > session.expires_at and session.status == SessionStatus.ACTIVE:
            session.status = SessionStatus.EXPIRED

        return session.status


if __name__ == "__main__":
    # Test harness
    lock = USSDSessionLock(session_ttl=10)
    
    # Create a session
    session_id = lock.create_session("user123", "device_fp_abc")
    print(f"Created session: {session_id}")
    
    # Validate the session
    is_valid = lock.validate_session(session_id, "device_fp_abc")
    print(f"Session valid: {is_valid}")
    
    # Lock the session to a transaction
    transaction_hash = lock.lock_session(session_id, "transfer_1000_kes")
    print(f"Transaction hash: {transaction_hash}")
    
    # Try to validate again (should fail because it's locked)
    is_valid = lock.validate_session(session_id, "device_fp_abc")
    print(f"Session valid after lock: {is_valid}")
    
    # Unlock the session
    unlocked = lock.unlock_session(session_id)
    print(f"Session unlocked: {unlocked}")
    
    # Validate again (should succeed)
    is_valid = lock.validate_session(session_id, "device_fp_abc")
    print(f"Session valid after unlock: {is_valid}")
    
    # Revoke the session
    revoked = lock.revoke_session(session_id)
    print(f"Session revoked: {revoked}")
    
    # Try to validate again (should fail because it's revoked)
    is_valid = lock.validate_session(session_id, "device_fp_abc")
    print(f"Session valid after revoke: {is_valid}")
    
    print("All tests passed.")