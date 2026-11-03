import time
import uuid
import hashlib
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EINStatus(Enum):
    """Enumeration of possible EIN statuses."""
    VALID = "VALID"
    INVALID = "INVALID"
    EXPIRED = "EXPIRED"
    PENDING = "PENDING"


@dataclass
class EINRecord:
    """Data class to represent a single Electronic Invoice Number (EIN) record."""
    ein: str
    timestamp: float
    status: EINStatus
    metadata: Dict[str, Any] = field(default_factory=dict)


class KRAEINDynamicRotator:
    """
    Autonomous KRA EIN Dynamic Rotator & Compliance Sentinel.
    
    This class handles the generation, validation, and rotation of Electronic Invoice Numbers (EINs)
    in compliance with Kenya Revenue Authority (KRA) standards. It ensures that EINs are unique,
    valid, and rotated periodically to prevent fraud and ensure compliance.
    """

    def __init__(self, kra_api_key: str, rotation_interval: int = 3600):
        """
        Initialize the KRA EIN Dynamic Rotator.

        Args:
            kra_api_key (str): The API key for KRA's EIN validation service.
            rotation_interval (int): The interval in seconds after which EINs should be rotated.
        """
        self.kra_api_key = kra_api_key
        self.rotation_interval = rotation_interval
        self.ein_records: Dict[str, EINRecord] = {}
        self.last_rotation_time: float = time.time()
        self.logger = logging.getLogger(__name__)

    def generate_ein(self) -> str:
        """
        Generate a new unique Electronic Invoice Number (EIN).

        Returns:
            str: A newly generated EIN.
        """
        timestamp = int(time.time())
        random_uuid = uuid.uuid4().hex
        ein = f"{timestamp}_{random_uuid}"
        self.logger.info(f"Generated new EIN: {ein}")
        return ein

    def validate_ein(self, ein: str) -> bool:
        """
        Validate an EIN against KRA's API.

        Args:
            ein (str): The EIN to validate.

        Returns:
            bool: True if the EIN is valid, False otherwise.
        """
        # Simulate API call to KRA for validation
        try:
            # In a real implementation, this would make an HTTP request to KRA's API
            # For this example, we simulate a successful validation
            self.logger.info(f"Validating EIN: {ein}")
            return True
        except Exception as e:
            self.logger.error(f"Error validating EIN {ein}: {e}")
            return False

    def rotate_ein(self) -> str:
        """
        Rotate the current EIN and validate the new one.

        Returns:
            str: The newly rotated and validated EIN.
        """
        new_ein = self.generate_ein()
        if self.validate_ein(new_ein):
            self.ein_records[new_ein] = EINRecord(
                ein=new_ein,
                timestamp=time.time(),
                status=EINStatus.VALID,
                metadata={"rotated_at": time.time()}
            )
            self.last_rotation_time = time.time()
            self.logger.info(f"Successfully rotated EIN to: {new_ein}")
            return new_ein
        else:
            self.logger.error(f"Failed to rotate EIN to: {new_ein}")
            raise ValueError("Failed to rotate EIN")

    def get_current_ein(self) -> Optional[str]:
        """
        Get the current valid EIN.

        Returns:
            Optional[str]: The current valid EIN, or None if no valid EIN exists.
        """
        for ein, record in self.ein_records.items():
            if record.status == EINStatus.VALID:
                return ein
        return None

    def check_rotation_needed(self) -> bool:
        """
        Check if an EIN rotation is needed based on the rotation interval.

        Returns:
            bool: True if rotation is needed, False otherwise.
        """
        return (time.time() - self.last_rotation_time) >= self.rotation_interval

    def run_autonomous_rotation(self) -> None:
        """
        Run the autonomous rotation process.

        This method checks if a rotation is needed and performs it if so.
        """
        if self.check_rotation_needed():
            self.rotate_ein()


if __name__ == "__main__":
    # Test harness
    rotator = KRAEINDynamicRotator(kra_api_key="test_api_key", rotation_interval=1)
    
    # Generate and validate an EIN
    ein = rotator.generate_ein()
    is_valid = rotator.validate_ein(ein)
    print(f"Generated EIN: {ein}, Valid: {is_valid}")

    # Rotate the EIN
    new_ein = rotator.rotate_ein()
    print(f"Rotated EIN: {new_ein}")

    # Check if rotation is needed
    print(f"Rotation needed: {rotator.check_rotation_needed()}")

    # Run autonomous rotation
    rotator.run_autonomous_rotation()
    print(f"Current EIN after autonomous rotation: {rotator.get_current_ein()}")