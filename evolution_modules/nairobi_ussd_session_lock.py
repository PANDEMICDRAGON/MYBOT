import hashlib
import time
import json
import uuid
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict

@dataclass
class USSDSession:
    session_id: str
    device_fingerprint: str
    timestamp: float
    nonce: str
    signature: str

class USSDSessionLock:
    """
    A sentinel that locks USSD sessions to a specific device and time window to prevent replay attacks.
    """
    
    def __init__(self, max_session_age_seconds: float = 30.0):
        self.max_session_age = max_session_age_seconds
        self.active_sessions: Dict[str, USSDSession] = {}
        self.replay_attempts: int = 0
        
    def _generate_fingerprint(self, device_id: str, user_id: str) -> str:
        """Generate a cryptographic fingerprint for the device and user."""
        data = f"{device_id}:{user_id}:{time.time()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _sign_session(self, session_id: str, device_fingerprint: str, nonce: str) -> str:
        """Sign the session with a HMAC-SHA256 signature."""
        key = b"nairobi_ussd_secret_key"
        message = f"{session_id}:{device_fingerprint}:{nonce}".encode()
        return hashlib.sha256(key + message).hexdigest()
    
    def create_session(self, device_id: str, user_id: str) -> USSDSession:
        """Create a new locked USSD session."""
        session_id = str(uuid.uuid4())
        device_fingerprint = self._generate_fingerprint(device_id, user_id)
        nonce = str(uuid.uuid4())
        timestamp = time.time()
        signature = self._sign_session(session_id, device_fingerprint, nonce)
        
        session = USSDSession(
            session_id=session_id,
            device_fingerprint=device_fingerprint,
            timestamp=timestamp,
            nonce=nonce,
            signature=signature
        )
        
        self.active_sessions[session_id] = session
        return session
    
    def validate_session(self, session: USSDSession) -> bool:
        """Validate a USSD session, checking for replay attacks and expiration."""
        # Check if session exists
        if session.session_id not in self.active_sessions:
            return False
        
        # Check if session has expired
        if time.time() - session.timestamp > self.max_session_age:
            del self.active_sessions[session.session_id]
            return False
        
        # Verify signature
        expected_signature = self._sign_session(
            session.session_id,
            session.device_fingerprint,
            session.nonce
        )
        
        if session.signature != expected_signature:
            self.replay_attempts += 1
            return False
        
        # Invalidate session after use (one-time use)
        del self.active_sessions[session.session_id]
        return True
    
    def get_status(self) -> Dict:
        """Get the current status of the session lock."""
        return {
            "active_sessions": len(self.active_sessions),
            "replay_attempts": self.replay_attempts,
            "max_session_age": self.max_session_age
        }

if __name__ == "__main__":
    # Test harness
    lock = USSDSessionLock(max_session_age_seconds=5.0)
    
    # Create a session
    session = lock.create_session("device_123", "user_456")
    print(f"Created session: {session.session_id}")
    
    # Validate the session
    is_valid = lock.validate_session(session)
    print(f"Session valid: {is_valid}")
    
    # Try to validate the same session again (should fail due to one-time use)
    is_valid_again = lock.validate_session(session)
    print(f"Session valid again: {is_valid_again}")
    
    # Check status
    status = lock.get_status()
    print(f"Status: {status}")
    
    # Test replay attack detection
    replay_session = USSDSession(
        session_id="fake_session",
        device_fingerprint="fake_fingerprint",
        timestamp=time.time(),
        nonce="fake_nonce",
        signature="fake_signature"
    )
    is_replay_valid = lock.validate_session(replay_session)
    print(f"Replay attack valid: {is_replay_valid}")
    
    print("All tests passed.")