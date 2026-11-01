import hashlib
import time
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EINRecord:
    ein: str
    timestamp: float
    status: str = 'active'
    metadata: Dict = field(default_factory=dict)

class EINStatus(Enum):
    ACTIVE = 'active'
    EXPIRED = 'expired'
    REVOKED = 'revoked'

class KraEinDynamicRotator:
    def __init__(self, max_ein_age: int = 3600, max_ein_count: int = 1000):
        self.max_ein_age = max_ein_age
        self.max_ein_count = max_ein_count
        self.ein_records: Dict[str, EINRecord] = {}
        self.lock = threading.Lock()

    def generate_ein(self, transaction_id: str) -> str:
        """Generate a unique EIN based on transaction ID and timestamp."""
        with self.lock:
            timestamp = time.time()
            unique_id = uuid.uuid4().hex
            ein = f"{timestamp}_{unique_id}"
            self.ein_records[ein] = EINRecord(ein=ein, timestamp=timestamp, metadata={'transaction_id': transaction_id})
            logger.info(f"Generated new EIN: {ein}")
            return ein

    def validate_ein(self, ein: str) -> bool:
        """Validate if an EIN is active and not expired."""
        with self.lock:
            record = self.ein_records.get(ein)
            if not record:
                logger.warning(f"EIN not found: {ein}")
                return False
            if record.status != EINStatus.ACTIVE.value:
                logger.warning(f"EIN is not active: {ein}")
                return False
            if time.time() - record.timestamp > self.max_ein_age:
                logger.warning(f"EIN is expired: {ein}")
                return False
            return True

    def revoke_ein(self, ein: str) -> bool:
        """Revoke an EIN."""
        with self.lock:
            record = self.ein_records.get(ein)
            if not record:
                logger.warning(f"EIN not found: {ein}")
                return False
            record.status = EINStatus.REVOKED.value
            logger.info(f"Revoked EIN: {ein}")
            return True

    def rotate_eins(self) -> List[str]:
        """Rotate expired EINs and return a list of revoked EINs."""
        with self.lock:
            revoked_eins = []
            for ein, record in self.ein_records.items():
                if record.status == EINStatus.ACTIVE.value and time.time() - record.timestamp > self.max_ein_age:
                    record.status = EINStatus.EXPIRED.value
                    revoked_eins.append(ein)
                    logger.info(f"Rotated EIN: {ein}")
            return revoked_eins

    def get_active_eins(self) -> List[str]:
        """Get a list of active EINs."""
        with self.lock:
            return [ein for ein, record in self.ein_records.items() if record.status == EINStatus.ACTIVE.value]

    def get_ein_count(self) -> int:
        """Get the count of active EINs."""
        with self.lock:
            return len(self.get_active_eins())

    def cleanup_old_eins(self) -> int:
        """Clean up old EINs beyond max_ein_count."""
        with self.lock:
            if len(self.ein_records) > self.max_ein_count:
                sorted_eins = sorted(self.ein_records.items(), key=lambda x: x[1].timestamp)
                to_remove = len(self.ein_records) - self.max_ein_count
                for ein, _ in sorted_eins[:to_remove]:
                    del self.ein_records[ein]
                    logger.info(f"Cleaned up old EIN: {ein}")
                return to_remove
            return 0

if __name__ == '__main__':
    rotator = KraEinDynamicRotator(max_ein_age=60, max_ein_count=10)
    
    # Generate EINs
    ein1 = rotator.generate_ein("TXN123")
    ein2 = rotator.generate_ein("TXN456")
    
    # Validate EINs
    assert rotator.validate_ein(ein1), "EIN1 should be valid"
    assert rotator.validate_ein(ein2), "EIN2 should be valid"
    
    # Revoke EIN
    assert rotator.revoke_ein(ein1), "EIN1 should be revoked"
    assert not rotator.validate_ein(ein1), "EIN1 should be invalid after revocation"
    
    # Rotate EINs
    time.sleep(61)  # Wait for EINs to expire
    rotated_eins = rotator.rotate_eins()
    assert ein2 in rotated_eins, "EIN2 should be rotated"
    
    # Get active EINs
    active_eins = rotator.get_active_eins()
    assert len(active_eins) == 0, "No active EINs should remain"
    
    # Cleanup old EINs
    for i in range(15):
        rotator.generate_ein(f"TXN{i}")
    cleaned_count = rotator.cleanup_old_eins()
    assert cleaned_count == 5, "5 old EINs should be cleaned up"
    
    logger.info("All tests passed successfully.")