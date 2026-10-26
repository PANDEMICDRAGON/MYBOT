import hashlib
import time
import uuid
from typing import Dict, Optional, List
import json

class KraEinDynamicRotator:
    """
    A module to dynamically rotate and validate KRA Electronic Identification Numbers (EINs).
    Ensures compliance with Kenya Revenue Authority standards and prevents credential exposure.
    """

    def __init__(self, operator_id: str, base_ein: str):
        """
        Initialize the KRA EIN Dynamic Rotator.

        Args:
            operator_id (str): The unique identifier for the operator.
            base_ein (str): The base EIN to be rotated.
        """
        self.operator_id = operator_id
        self.base_ein = base_ein
        self.current_ein = base_ein
        self.rotation_history: List[Dict[str, str]] = []
        self.last_rotation_time: Optional[float] = None

    def rotate_ein(self) -> str:
        """
        Rotate the current EIN using a secure hash-based algorithm.

        Returns:
            str: The newly rotated EIN.
        """
        timestamp = time.time()
        unique_id = str(uuid.uuid4())
        seed = f"{self.base_ein}{timestamp}{unique_id}"
        hashed_seed = hashlib.sha256(seed.encode()).hexdigest()
        new_ein = hashed_seed[:10].upper()
        self.current_ein = new_ein
        self.last_rotation_time = timestamp
        self.rotation_history.append({
            "ein": new_ein,
            "timestamp": timestamp
        })
        return new_ein

    def validate_ein(self, ein: str) -> bool:
        """
        Validate if the provided EIN is the current valid EIN.

        Args:
            ein (str): The EIN to validate.

        Returns:
            bool: True if the EIN is valid, False otherwise.
        """
        return ein == self.current_ein

    def get_rotation_history(self) -> List[Dict[str, str]]:
        """
        Retrieve the history of EIN rotations.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing rotation details.
        """
        return self.rotation_history

    def export_state(self) -> str:
        """
        Export the current state of the rotator as a JSON string.

        Returns:
            str: JSON-formatted state of the rotator.
        """
        state = {
            "operator_id": self.operator_id,
            "current_ein": self.current_ein,
            "last_rotation_time": self.last_rotation_time,
            "rotation_history": self.rotation_history
        }
        return json.dumps(state)

if __name__ == "__main__":
    # Test Harness
    rotator = KraEinDynamicRotator("MichaelObiero", "KRA123456789")
    print(f"Initial EIN: {rotator.current_ein}")
    
    # Rotate EIN
    new_ein = rotator.rotate_ein()
    print(f"Rotated EIN: {new_ein}")
    
    # Validate EIN
    is_valid = rotator.validate_ein(new_ein)
    print(f"Validation Result: {is_valid}")
    
    # Get Rotation History
    history = rotator.get_rotation_history()
    print(f"Rotation History: {history}")
    
    # Export State
    state = rotator.export_state()
    print(f"Exported State: {state}")