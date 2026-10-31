import uuid
import time
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KraEinDynamicRotator:
    """
    A class to dynamically rotate and validate KRA Electronic Invoice Numbers (EINs).
    
    Attributes:
        business_name (str): The name of the business.
        pin (str): The KRA Personal Identification Number (PIN).
        ein_cache (Dict[str, Dict]): A cache of recently generated EINs.
        rotation_interval (int): The interval in seconds for rotating EINs.
    """

    def __init__(self, business_name: str, pin: str, rotation_interval: int = 3600):
        """
        Initialize the KraEinDynamicRotator.

        Args:
            business_name (str): The name of the business.
            pin (str): The KRA Personal Identification Number (PIN).
            rotation_interval (int): The interval in seconds for rotating EINs.
        """
        self.business_name = business_name
        self.pin = pin
        self.ein_cache: Dict[str, Dict] = {}
        self.rotation_interval = rotation_interval
        self._last_rotation_time = time.time()

    def generate_ein(self, invoice_data: Dict) -> str:
        """
        Generate a new KRA EIN based on the provided invoice data.

        Args:
            invoice_data (Dict): The invoice data used to generate the EIN.

        Returns:
            str: The generated EIN.
        """
        # Create a unique identifier for the invoice
        unique_id = str(uuid.uuid4())
        timestamp = int(time.time())

        # Create a hash of the invoice data and unique identifier
        hash_input = f"{self.business_name}{self.pin}{unique_id}{timestamp}{json.dumps(invoice_data)}"
        ein_hash = hashlib.sha256(hash_input.encode()).hexdigest()

        # Format the EIN (example format: EIN-<hash>-<timestamp>)
        ein = f"EIN-{ein_hash[:16]}-{timestamp}"

        # Cache the EIN
        self.ein_cache[ein] = {
            "ein": ein,
            "invoice_data": invoice_data,
            "generated_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(seconds=self.rotation_interval)).isoformat()
        }

        logger.info(f"Generated new EIN: {ein}")
        return ein

    def validate_ein(self, ein: str) -> bool:
        """
        Validate an existing EIN.

        Args:
            ein (str): The EIN to validate.

        Returns:
            bool: True if the EIN is valid, False otherwise.
        """
        if ein not in self.ein_cache:
            logger.warning(f"EIN not found in cache: {ein}")
            return False

        ein_data = self.ein_cache[ein]
        expires_at = datetime.fromisoformat(ein_data["expires_at"])

        if datetime.now() > expires_at:
            logger.warning(f"EIN has expired: {ein}")
            return False

        logger.info(f"EIN validated successfully: {ein}")
        return True

    def rotate_eins(self) -> None:
        """
        Rotate all cached EINs that have expired.
        """
        current_time = time.time()
        if current_time - self._last_rotation_time < self.rotation_interval:
            return

        expired_eins = []
        for ein, data in self.ein_cache.items():
            expires_at = datetime.fromisoformat(data["expires_at"])
            if datetime.now() > expires_at:
                expired_eins.append(ein)

        for ein in expired_eins:
            del self.ein_cache[ein]
            logger.info(f"Rotated expired EIN: {ein}")

        self._last_rotation_time = current_time
        logger.info("EIN rotation completed.")

    def get_active_eins(self) -> List[str]:
        """
        Retrieve all active (non-expired) EINs.

        Returns:
            List[str]: A list of active EINs.
        """
        active_eins = []
        for ein, data in self.ein_cache.items():
            expires_at = datetime.fromisoformat(data["expires_at"])
            if datetime.now() <= expires_at:
                active_eins.append(ein)

        return active_eins


if __name__ == "__main__":
    # Test the KraEinDynamicRotator
    rotator = KraEinDynamicRotator("Test Business", "12345678901234567890", rotation_interval=60)

    # Generate an EIN
    invoice_data = {"amount": 1000, "customer": "John Doe"}
    ein = rotator.generate_ein(invoice_data)
    print(f"Generated EIN: {ein}")

    # Validate the EIN
    is_valid = rotator.validate_ein(ein)
    print(f"EIN Valid: {is_valid}")

    # Rotate EINs
    rotator.rotate_eins()

    # Get active EINs
    active_eins = rotator.get_active_eins()
    print(f"Active EINs: {active_eins}")
