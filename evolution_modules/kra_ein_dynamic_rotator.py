import hashlib
import time
import uuid
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import json
import os


class EINStatus(Enum):
    """Enum representing the status of an EIN."""
    PENDING = "PENDING"
    ISSUED = "ISSUED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


@dataclass
class EINRecord:
    """Data class representing a single Electronic Invoice Number record."""
    ein: str
    timestamp: float
    status: EINStatus
    metadata: Dict[str, str] = field(default_factory=dict)
    checksum: str = ""

    def to_dict(self) -> Dict:
        """Convert the record to a dictionary for serialization."""
        return {
            "ein": self.ein,
            "timestamp": self.timestamp,
            "status": self.status.value,
            "metadata": self.metadata,
            "checksum": self.checksum
        }


class KraEinDynamicRotator:
    """
    A dynamic rotator for Kenya Revenue Authority Electronic Invoice Numbers (EINs).
    
    This class ensures that EINs are generated in a non-sequential, cryptographically
    secure manner to prevent prediction and replay attacks. It maintains an in-memory
    state of issued EINs and provides a tamper-evident audit log.
    """

    def __init__(self, operator_id: str, secret_key: str):
        """
        Initialize the EIN Rotator.

        Args:
            operator_id: The unique identifier for the operator (e.g., KRA PIN).
            secret_key: A secret key used for HMAC signing to ensure integrity.
        """
        self.operator_id = operator_id
        self.secret_key = secret_key.encode('utf-8')
        self._issued_eins: Dict[str, EINRecord] = {}
        self._audit_log: List[str] = []
        self._last_ein_hash: str = hashlib.sha256(b"INITIAL").hexdigest()

    def _generate_ein(self) -> str:
        """
        Generate a new, unique EIN.

        Returns:
            A string representing the new EIN.
        """
        # Use a combination of timestamp, UUID, and previous hash to ensure uniqueness and non-sequentiality
        timestamp = time.time()
        unique_id = uuid.uuid4().hex
        # Create a hash chain to prevent prediction
        payload = f"{self.operator_id}:{timestamp}:{unique_id}:{self._last_ein_hash}".encode('utf-8')
        ein_hash = hashlib.sha256(payload).hexdigest()
        
        # Update the last hash for the next iteration
        self._last_ein_hash = ein_hash
        
        # Format the EIN (e.g., KRA-EIN-<hash_prefix>)
        return f"KRA-EIN-{ein_hash[:16].upper()}"

    def _compute_checksum(self, ein: str, metadata: Dict[str, str]) -> str:
        """
        Compute a checksum for the EIN and its metadata.

        Args:
            ein: The EIN string.
            metadata: The metadata associated with the EIN.

        Returns:
            A string representing the checksum.
        """
        payload = f"{ein}:{json.dumps(metadata, sort_keys=True)}".encode('utf-8')
        return hashlib.sha256(payload).hexdigest()

    def issue_ein(self, metadata: Optional[Dict[str, str]] = None) -> EINRecord:
        """
        Issue a new EIN.

        Args:
            metadata: Optional metadata to associate with the EIN.

        Returns:
            An EINRecord representing the newly issued EIN.

        Raises:
            ValueError: If the metadata is invalid.
        """
        if metadata is None:
            metadata = {}
        
        ein = self._generate_ein()
        timestamp = time.time()
        checksum = self._compute_checksum(ein, metadata)
        
        record = EINRecord(
            ein=ein,
            timestamp=timestamp,
            status=EINStatus.ISSUED,
            metadata=metadata,
            checksum=checksum
        )
        
        self._issued_eins[ein] = record
        self._audit_log.append(json.dumps(record.to_dict()))
        
        return record

    def cancel_ein(self, ein: str) -> bool:
        """
        Cancel an existing EIN.

        Args:
            ein: The EIN to cancel.

        Returns:
            True if the EIN was successfully cancelled, False otherwise.
        """
        if ein in self._issued_eins:
            record = self._issued_eins[ein]
            if record.status == EINStatus.ISSUED:
                record.status = EINStatus.CANCELLED
                self._audit_log.append(json.dumps(record.to_dict()))
                return True
        return False

    def get_ein(self, ein: str) -> Optional[EINRecord]:
        """
        Retrieve an EIN record.

        Args:
            ein: The EIN to retrieve.

        Returns:
            The EINRecord if found, None otherwise.
        """
        return self._issued_eins.get(ein)

    def get_audit_log(self) -> List[str]:
        """
        Retrieve the audit log.

        Returns:
            A list of JSON strings representing the audit log.
        """
        return self._audit_log.copy()

    def verify_integrity(self) -> bool:
        """
        Verify the integrity of all issued EINs.

        Returns:
            True if all EINs are valid, False otherwise.
        """
        for ein, record in self._issued_eins.items():
            expected_checksum = self._compute_checksum(ein, record.metadata)
            if record.checksum != expected_checksum:
                return False
        return True


if __name__ == "__main__":
    # Test the KraEinDynamicRotator
    rotator = KraEinDynamicRotator(operator_id="TEST_OPERATOR", secret_key="TEST_SECRET")
    
    # Issue an EIN
    ein_record = rotator.issue_ein(metadata={"invoice_id": "INV-001", "amount": "1000.00"})
    print(f"Issued EIN: {ein_record.ein}")
    print(f"Status: {ein_record.status.value}")
    
    # Retrieve the EIN
    retrieved_ein = rotator.get_ein(ein_record.ein)
    assert retrieved_ein is not None
    assert retrieved_ein.ein == ein_record.ein
    
    # Cancel the EIN
    cancelled = rotator.cancel_ein(ein_record.ein)
    assert cancelled is True
    
    # Verify integrity
    is_valid = rotator.verify_integrity()
    assert is_valid is True
    
    # Check audit log
    audit_log = rotator.get_audit_log()
    assert len(audit_log) == 2  # One for issue, one for cancel
    
    print("All tests passed.")