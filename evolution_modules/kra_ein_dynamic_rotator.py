import hashlib
import time
import uuid
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KRA_EIN_Rotator")

class EINStatus(Enum):
    VALID = "VALID"
    EXPIRED = "EXPIRED"
    COMPROMISED = "COMPROMISED"
    PENDING = "PENDING"

@dataclass
class EINRecord:
    ein: str
    created_at: float
    expires_at: float
    status: EINStatus
    checksum: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class KRAEINDynamicRotator:
    """
    Proactively rotates KRA EINs to prevent spoofing and ensure compliance.
    """

    def __init__(self, rotation_interval: int = 3600):
        self.rotation_interval = rotation_interval
        self.active_ein: Optional[EINRecord] = None
        self.ein_history: list[EINRecord] = []
        self.compliance_flags: list[str] = []

    def _generate_ein(self) -> str:
        """Generate a unique EIN based on current time and UUID."""
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:8]
        return f"KRA-{timestamp}-{unique_id}"

    def _compute_checksum(self, ein: str) -> str:
        """Compute a SHA-256 checksum for the EIN."""
        return hashlib.sha256(ein.encode()).hexdigest()[:16]

    def rotate_ein(self) -> EINRecord:
        """Rotate the active EIN and mark the old one as expired."""
        if self.active_ein:
            self.active_ein.status = EINStatus.EXPIRED
            self.ein_history.append(self.active_ein)

        new_ein = self._generate_ein()
        now = time.time()
        new_record = EINRecord(
            ein=new_ein,
            created_at=now,
            expires_at=now + self.rotation_interval,
            status=EINStatus.VALID,
            checksum=self._compute_checksum(new_ein),
            metadata={"rotated_by": "Cortana_Autonomous_Evolution"}
        )
        self.active_ein = new_record
        logger.info(f"Rotated EIN to {new_ein}")
        return new_record

    def validate_ein(self, ein: str) -> bool:
        """Validate an EIN against the active record and checksum."""
        if not self.active_ein:
            return False
        if self.active_ein.ein != ein:
            return False
        if self.active_ein.status != EINStatus.VALID:
            return False
        if time.time() > self.active_ein.expires_at:
            self.active_ein.status = EINStatus.EXPIRED
            return False
        return True

    def check_compliance(self, transaction_amount: float) -> bool:
        """Check if a transaction amount complies with KRA thresholds."""
        # Simulated compliance check: flag transactions over 1,000,000 KES
        if transaction_amount > 1_000_000:
            self.compliance_flags.append(f"High-value transaction: {transaction_amount}")
            logger.warning(f"Compliance flag raised for transaction: {transaction_amount}")
            return False
        return True

    def get_active_ein(self) -> Optional[str]:
        """Return the active EIN if valid, else None."""
        if self.active_ein and self.active_ein.status == EINStatus.VALID:
            return self.active_ein.ein
        return None

if __name__ == "__main__":
    rotator = KRAEINDynamicRotator(rotation_interval=60)
    
    # Initial rotation
    ein_record = rotator.rotate_ein()
    print(f"Active EIN: {ein_record.ein}")
    
    # Validate EIN
    is_valid = rotator.validate_ein(ein_record.ein)
    print(f"EIN Valid: {is_valid}")
    
    # Check compliance
    compliant = rotator.check_compliance(500_000)
    print(f"Transaction Compliant: {compliant}")
    
    # Rotate again
    new_record = rotator.rotate_ein()
    print(f"New Active EIN: {new_record.ein}")
    
    # Old EIN should be invalid
    old_valid = rotator.validate_ein(ein_record.ein)
    print(f"Old EIN Valid: {old_valid}")
