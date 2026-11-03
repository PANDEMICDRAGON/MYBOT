import hashlib
import time
import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KRA_EIN_Rotator")

class RotationStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"

@dataclass
class RotationEvent:
    timestamp: float
    status: RotationStatus
    old_ein_hash: str
    new_ein_hash: str
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class KRAEINDynamicRotator:
    """
    Autonomous KRA EIN Dynamic Rotator & Compliance Sentinel.
    
    This class handles the secure, time-based rotation of Electronic Identity Numbers (EINs)
    used for KRA API interactions. It ensures that credentials are never static and
    monitors the integrity of the communication channel.
    """

    def __init__(self, secret_key: str, rotation_interval: int = 300):
        """
        Initialize the Rotator.
        
        Args:
            secret_key (str): The base secret key for generating EINs.
            rotation_interval (int): Interval in seconds for rotation.
        """
        self.secret_key = secret_key
        self.rotation_interval = rotation_interval
        self.current_ein: Optional[str] = None
        self.last_rotation_time: float = 0.0
        self.rotation_history: list[RotationEvent] = []
        self._generate_new_ein()

    def _generate_new_ein(self) -> str:
        """
        Generate a new EIN based on the current time and secret key.
        
        Returns:
            str: The newly generated EIN.
        """
        current_time = int(time.time())
        # Use a combination of time, secret key, and a random nonce for entropy
        nonce = os.urandom(16).hex()
        data = f"{self.secret_key}:{current_time}:{nonce}".encode('utf-8')
        ein_hash = hashlib.sha256(data).hexdigest()
        
        # Format the EIN to look like a standard KRA EIN (e.g., 12345678901234567890123456789012)
        # For demonstration, we'll use the first 32 characters of the hash
        self.current_ein = ein_hash[:32]
        self.last_rotation_time = time.time()
        
        logger.info(f"Generated new EIN: {self.current_ein[:8]}... (Hash: {ein_hash[:8]}...)")
        return self.current_ein

    def get_current_ein(self) -> str:
        """
        Get the current EIN, rotating it if necessary.
        
        Returns:
            str: The current valid EIN.
        """
        if time.time() - self.last_rotation_time > self.rotation_interval:
            old_ein_hash = hashlib.sha256(self.current_ein.encode('utf-8')).hexdigest()
            self._generate_new_ein()
            new_ein_hash = hashlib.sha256(self.current_ein.encode('utf-8')).hexdigest()
            
            event = RotationEvent(
                timestamp=time.time(),
                status=RotationStatus.SUCCESS,
                old_ein_hash=old_ein_hash,
                new_ein_hash=new_ein_hash,
                reason="Time-based rotation",
                metadata={"interval": self.rotation_interval}
            )
            self.rotation_history.append(event)
            logger.info(f"Rotated EIN. Old: {old_ein_hash[:8]}..., New: {new_ein_hash[:8]}...")
        
        return self.current_ein

    def verify_response_integrity(self, response_headers: Dict[str, str]) -> bool:
        """
        Verify the integrity of the KRA API response headers.
        
        Args:
            response_headers (Dict[str, str]): The headers from the KRA API response.
            
        Returns:
            bool: True if the response is valid, False otherwise.
        """
        required_headers = ['X-KRA-Signature', 'X-KRA-Timestamp']
        for header in required_headers:
            if header not in response_headers:
                logger.warning(f"Missing required header: {header}")
                return False
        
        # Simulate signature verification
        signature = response_headers['X-KRA-Signature']
        timestamp = response_headers['X-KRA-Timestamp']
        
        # Check if the timestamp is within a reasonable window (e.g., 5 minutes)
        if abs(time.time() - float(timestamp)) > 300:
            logger.warning("Response timestamp is outside the acceptable window.")
            return False
        
        # Simulate signature check (in production, this would use the KRA public key)
        if not signature:
            logger.warning("Empty signature in response.")
            return False
        
        return True

    def get_rotation_history(self) -> list[Dict[str, Any]]:
        """
        Get the history of EIN rotations.
        
        Returns:
            list[Dict[str, Any]]: A list of rotation events.
        """
        return [
            {
                "timestamp": event.timestamp,
                "status": event.status.value,
                "old_ein_hash": event.old_ein_hash,
                "new_ein_hash": event.new_ein_hash,
                "reason": event.reason,
                "metadata": event.metadata
            }
            for event in self.rotation_history
        ]

if __name__ == "__main__":
    # Test harness
    secret = "test_secret_key_for_kra"
    rotator = KRAEINDynamicRotator(secret_key=secret, rotation_interval=1)
    
    # Test 1: Get current EIN
    ein1 = rotator.get_current_ein()
    print(f"Initial EIN: {ein1}")
    
    # Wait for rotation
    time.sleep(1.1)
    
    # Test 2: Get rotated EIN
    ein2 = rotator.get_current_ein()
    print(f"Rotated EIN: {ein2}")
    
    assert ein1 != ein2, "EIN should have rotated"
    
    # Test 3: Verify response integrity
    valid_headers = {
        "X-KRA-Signature": "valid_signature",
        "X-KRA-Timestamp": str(time.time())
    }
    assert rotator.verify_response_integrity(valid_headers) == True, "Valid headers should pass"
    
    invalid_headers = {
        "X-KRA-Signature": "",
        "X-KRA-Timestamp": str(time.time())
    }
    assert rotator.verify_response_integrity(invalid_headers) == False, "Invalid headers should fail"
    
    # Test 4: Check rotation history
    history = rotator.get_rotation_history()
    assert len(history) == 1, "Should have one rotation event"
    
    print("All tests passed successfully.")
    print(f"Rotation History: {json.dumps(history, indent=2)}")