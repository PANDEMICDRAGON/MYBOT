import time
import hashlib
import secrets
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KRA_EIN_Rotator")


class RotationStatus(Enum):
    """Enum representing the status of an EIN rotation cycle."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class EINRecord:
    """Data class to store EIN metadata and security state."""
    ein: str
    created_at: float
    expires_at: float
    status: RotationStatus = RotationStatus.PENDING
    checksum: str = field(default="")

    def is_valid(self) -> bool:
        """Check if the EIN is currently valid and not expired."""
        return self.status == RotationStatus.SUCCESS and time.time() < self.expires_at

    def compute_checksum(self) -> str:
        """Compute a SHA-256 checksum of the EIN for integrity verification."""
        return hashlib.sha256(self.ein.encode('utf-8')).hexdigest()


class KRAEINDynamicRotator:
    """
    Autonomous module for rotating KRA Electronic Identification Numbers (EINs)
    and associated API tokens to prevent credential reuse and interception.
    
    This module operates in a zero-trust environment, ensuring that old credentials
    are immediately invalidated upon rotation and new ones are generated with
    cryptographic randomness.
    """

    def __init__(self, rotation_interval: int = 3600, max_history: int = 10):
        """
        Initialize the Rotator.
        
        Args:
            rotation_interval: Time in seconds before an EIN must be rotated.
            max_history: Maximum number of historical EIN records to keep.
        """
        self.rotation_interval = rotation_interval
        self.max_history = max_history
        self._history: list[EINRecord] = []
        self._current_ein: Optional[EINRecord] = None
        self._lock = False  # Simple flag to prevent concurrent rotations

    def _generate_ein(self) -> str:
        """
        Generate a cryptographically secure random EIN.
        
        Returns:
            A string representing the new EIN.
        """
        # Simulate KRA EIN format: 10 alphanumeric characters
        return secrets.token_hex(5).upper()

    def _invalidate_old_ein(self, old_ein: str) -> bool:
        """
        Simulate the invalidation of an old EIN with KRA servers.
        
        Args:
            old_ein: The EIN to invalidate.
            
        Returns:
            True if invalidation was successful.
        """
        logger.info(f"Invalidating old EIN: {old_ein[:4]}****")
        # In production, this would make an API call to KRA
        return True

    def rotate(self) -> Optional[EINRecord]:
        """
        Perform an EIN rotation cycle.
        
        Returns:
            The new EINRecord if successful, None otherwise.
        """
        if self._lock:
            logger.warning("Rotation already in progress.")
            return None

        self._lock = True
        try:
            logger.info("Starting EIN rotation cycle...")
            
            # Invalidate current EIN if it exists
            if self._current_ein and self._current_ein.is_valid():
                if not self._invalidate_old_ein(self._current_ein.ein):
                    raise RuntimeError("Failed to invalidate old EIN")
                self._current_ein.status = RotationStatus.EXPIRED

            # Generate new EIN
            new_ein_str = self._generate_ein()
            now = time.time()
            new_record = EINRecord(
                ein=new_ein_str,
                created_at=now,
                expires_at=now + self.rotation_interval,
                status=RotationStatus.SUCCESS,
                checksum=new_ein_str  # Placeholder, will be computed
            )
            new_record.checksum = new_record.compute_checksum()

            # Update state
            self._current_ein = new_record
            self._history.append(new_record)

            # Trim history if necessary
            if len(self._history) > self.max_history:
                self._history = self._history[-self.max_history:]

            logger.info(f"EIN rotation successful. New EIN: {new_ein_str[:4]}****")
            return new_record

        except Exception as e:
            logger.error(f"EIN rotation failed: {str(e)}")
            if self._current_ein:
                self._current_ein.status = RotationStatus.FAILED
            return None
        finally:
            self._lock = False

    def get_current_ein(self) -> Optional[str]:
        """
        Retrieve the current valid EIN.
        
        Returns:
            The current EIN string if valid, None otherwise.
        """
        if self._current_ein and self._current_ein.is_valid():
            return self._current_ein.ein
        return None

    def verify_ein_integrity(self, ein: str, checksum: str) -> bool:
        """
        Verify the integrity of an EIN using its checksum.
        
        Args:
            ein: The EIN to verify.
            checksum: The expected checksum.
            
        Returns:
            True if the EIN matches the checksum.
        """
        return hashlib.sha256(ein.encode('utf-8')).hexdigest() == checksum

    def get_status(self) -> Dict[str, any]:
        """
        Get the current status of the rotator.
        
        Returns:
            A dictionary containing status information.
        """
        return {
            "current_ein_valid": self.get_current_ein() is not None,
            "history_size": len(self._history),
            "rotation_interval": self.rotation_interval,
            "last_rotation": self._current_ein.created_at if self._current_ein else None
        }


if __name__ == "__main__":
    # Test Harness
    print("=== KRA EIN Dynamic Rotator Test ===")
    
    # Initialize rotator with short interval for testing
    rotator = KRAEINDynamicRotator(rotation_interval=60, max_history=5)
    
    # Initial rotation
    record1 = rotator.rotate()
    assert record1 is not None, "Initial rotation failed"
    assert record1.is_valid(), "New EIN should be valid"
    
    current_ein = rotator.get_current_ein()
    assert current_ein == record1.ein, "Current EIN mismatch"
    
    # Verify integrity
    assert rotator.verify_ein_integrity(record1.ein, record1.checksum), "Integrity check failed"
    
    # Second rotation
    record2 = rotator.rotate()
    assert record2 is not None, "Second rotation failed"
    assert record2.ein != record1.ein, "EINs should be different"
    
    # Old EIN should be invalid
    assert not record1.is_valid(), "Old EIN should be expired"
    
    # Current EIN should be the new one
    assert rotator.get_current_ein() == record2.ein, "Current EIN should be updated"
    
    # Check status
    status = rotator.get_status()
    assert status["current_ein_valid"] is True
    assert status["history_size"] == 2
    
    print("All tests passed successfully.")
    print(f"Status: {status}")