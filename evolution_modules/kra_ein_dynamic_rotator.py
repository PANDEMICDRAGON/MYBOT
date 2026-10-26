import hashlib
import time
import uuid
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EINStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class EINRecord:
    ein: str
    status: EINStatus
    created_at: float
    expires_at: float
    metadata: Dict[str, str] = field(default_factory=dict)

    def is_valid(self) -> bool:
        return self.status == EINStatus.ACTIVE and time.time() < self.expires_at


class KRAEINDynamicRotator:
    def __init__(self, rotation_interval: int = 3600):
        self.rotation_interval = rotation_interval
        self.ein_records: Dict[str, EINRecord] = {}
        self._lock = None  # Placeholder for thread safety if needed

    def generate_ein(self, business_id: str) -> str:
        """Generate a unique EIN based on business ID and timestamp."""
        timestamp = int(time.time())
        seed = f"{business_id}{timestamp}{uuid.uuid4()}"
        return hashlib.sha256(seed.encode()).hexdigest()[:16].upper()

    def register_ein(self, business_id: str, metadata: Optional[Dict[str, str]] = None) -> str:
        """Register a new EIN for a business."""
        ein = self.generate_ein(business_id)
        record = EINRecord(
            ein=ein,
            status=EINStatus.ACTIVE,
            created_at=time.time(),
            expires_at=time.time() + self.rotation_interval,
            metadata=metadata or {}
        )
        self.ein_records[ein] = record
        logger.info(f"Registered EIN {ein} for business {business_id}")
        return ein

    def rotate_ein(self, business_id: str) -> str:
        """Rotate the EIN for a business, deactivating the old one."""
        for ein, record in self.ein_records.items():
            if record.metadata.get("business_id") == business_id and record.is_valid():
                record.status = EINStatus.REVOKED
                logger.info(f"Revoked EIN {ein} for business {business_id}")
                break
        return self.register_ein(business_id)

    def validate_ein(self, ein: str) -> bool:
        """Validate an EIN."""
        record = self.ein_records.get(ein)
        return record.is_valid() if record else False

    def get_active_eins(self) -> List[str]:
        """Get all active EINs."""
        return [ein for ein, record in self.ein_records.items() if record.is_valid()]

    def cleanup_expired_eins(self) -> int:
        """Remove expired EINs from the registry."""
        expired_eins = [ein for ein, record in self.ein_records.items() if not record.is_valid()]
        for ein in expired_eins:
            del self.ein_records[ein]
        logger.info(f"Cleaned up {len(expired_eins)} expired EINs")
        return len(expired_eins)


if __name__ == "__main__":
    rotator = KRAEINDynamicRotator(rotation_interval=3600)
    business_id = "BUSINESS_001"

    # Register a new EIN
    ein = rotator.register_ein(business_id, metadata={"business_id": business_id})
    print(f"Registered EIN: {ein}")

    # Validate the EIN
    print(f"EIN Valid: {rotator.validate_ein(ein)}")

    # Rotate the EIN
    new_ein = rotator.rotate_ein(business_id)
    print(f"Rotated EIN: {new_ein}")

    # Validate the old EIN (should be invalid)
    print(f"Old EIN Valid: {rotator.validate_ein(ein)}")

    # Validate the new EIN (should be valid)
    print(f"New EIN Valid: {rotator.validate_ein(new_ein)}")

    # Get active EINs
    print(f"Active EINs: {rotator.get_active_eins()}")

    # Cleanup expired EINs
    cleaned = rotator.cleanup_expired_eins()
    print(f"Cleaned up {cleaned} expired EINs")
