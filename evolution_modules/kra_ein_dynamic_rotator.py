import time
import hashlib
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class EINRecord:
    ein: str
    timestamp: float
    status: str = "active"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ein": self.ein,
            "timestamp": self.timestamp,
            "status": self.status
        }

class KraEinDynamicRotator:
    def __init__(self, rotation_interval: int = 3600):
        self.rotation_interval = rotation_interval
        self.ein_history: list[EINRecord] = []
        self.current_ein: Optional[str] = None

    def generate_ein(self) -> str:
        """Generate a new EIN based on current timestamp and random seed."""
        seed = f"{time.time()}_{hashlib.sha256(str(time.time()).encode()).hexdigest()}"
        return f"KRA-{hashlib.sha256(seed.encode()).hexdigest()[:12].upper()}"

    def rotate_ein(self) -> str:
        """Rotate the current EIN and log the previous one."""
        if self.current_ein:
            self.ein_history.append(EINRecord(self.current_ein, time.time(), "rotated"))
        self.current_ein = self.generate_ein()
        return self.current_ein

    def get_current_ein(self) -> str:
        """Get the current active EIN, rotating if necessary."""
        if not self.current_ein or (time.time() - self.ein_history[-1].timestamp > self.rotation_interval if self.ein_history else True):
            self.rotate_ein()
        return self.current_ein

    def get_compliance_status(self) -> Dict[str, Any]:
        """Return compliance status including current EIN and history."""
        return {
            "current_ein": self.get_current_ein(),
            "history_length": len(self.ein_history),
            "last_rotation": self.ein_history[-1].timestamp if self.ein_history else None
        }

if __name__ == "__main__":
    rotator = KraEinDynamicRotator(rotation_interval=1)
    print("Initial EIN:", rotator.get_current_ein())
    time.sleep(2)
    print("Rotated EIN:", rotator.get_current_ein())
    print("Compliance Status:", json.dumps(rotator.get_compliance_status(), indent=2))