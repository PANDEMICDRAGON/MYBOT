import logging
import secrets
import time
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KraEinDynamicRotator:
    """
    A class to handle the dynamic rotation of KRA Electronic Identification Numbers (EINs)
    and ensure compliance with Kenyan tax regulations.
    """

    def __init__(self, initial_ein: str, rotation_interval: int = 3600):
        """
        Initialize the KraEinDynamicRotator.

        Args:
            initial_ein (str): The initial EIN to start with.
            rotation_interval (int): The interval in seconds after which the EIN should be rotated.
        """
        self.current_ein = initial_ein
        self.rotation_interval = rotation_interval
        self.last_rotation_time = time.time()
        self.ein_history: List[str] = [initial_ein]

    def generate_new_ein(self) -> str:
        """
        Generate a new secure EIN.

        Returns:
            str: A newly generated EIN.
        """
        new_ein = secrets.token_hex(16)
        logger.info(f"Generated new EIN: {new_ein}")
        return new_ein

    def rotate_ein(self) -> str:
        """
        Rotate the current EIN to a new one.

        Returns:
            str: The newly rotated EIN.
        """
        if time.time() - self.last_rotation_time < self.rotation_interval:
            logger.warning("Rotation interval not yet reached. Skipping rotation.")
            return self.current_ein

        new_ein = self.generate_new_ein()
        self.current_ein = new_ein
        self.last_rotation_time = time.time()
        self.ein_history.append(new_ein)
        logger.info(f"EIN rotated to: {new_ein}")
        return new_ein

    def get_current_ein(self) -> str:
        """
        Retrieve the current EIN.

        Returns:
            str: The current EIN.
        """
        return self.current_ein

    def get_ein_history(self) -> List[str]:
        """
        Retrieve the history of all rotated EINs.

        Returns:
            List[str]: A list of all EINs used.
        """
        return self.ein_history

    def validate_ein(self, ein: str) -> bool:
        """
        Validate if the provided EIN is the current one.

        Args:
            ein (str): The EIN to validate.

        Returns:
            bool: True if the EIN is valid, False otherwise.
        """
        return ein == self.current_ein


def main():
    """
    Main function to test the KraEinDynamicRotator.
    """
    initial_ein = "initial_ein_12345"
    rotator = KraEinDynamicRotator(initial_ein, rotation_interval=1)

    # Test initial state
    assert rotator.get_current_ein() == initial_ein
    assert rotator.get_ein_history() == [initial_ein]

    # Test rotation
    time.sleep(1.1)
    new_ein = rotator.rotate_ein()
    assert rotator.get_current_ein() == new_ein
    assert rotator.get_ein_history() == [initial_ein, new_ein]

    # Test validation
    assert rotator.validate_ein(new_ein)
    assert not rotator.validate_ein(initial_ein)

    logger.info("All tests passed successfully.")


if __name__ == "__main__":
    main()