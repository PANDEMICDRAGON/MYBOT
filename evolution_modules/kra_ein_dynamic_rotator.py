import time
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KRA_EIN_Rotator")

@dataclass
class Credential:
    ein: str
    api_key: str
    created_at: datetime
    expires_at: datetime
    is_active: bool = True

@dataclass
class ComplianceDeadline:
    description: str
    due_date: datetime
    status: str = "pending"

class KRAEINDynamicRotator:
    """
    A dynamic rotator for KRA EINs and API keys.
    Ensures credentials are rotated before expiration and monitors compliance deadlines.
    """

    def __init__(self, rotation_interval_hours: int = 24):
        self.rotation_interval = timedelta(hours=rotation_interval_hours)
        self.credentials: List[Credential] = []
        self.compliance_deadlines: List[ComplianceDeadline] = []
        self._lock = False  # Simple lock for thread safety in single-threaded context

    def _generate_ein(self) -> str:
        """Generate a mock EIN (in production, this would call KRA API)."""
        timestamp = int(time.time())
        random_seed = hashlib.sha256(str(timestamp).encode()).hexdigest()[:8]
        return f"EIN-{timestamp}-{random_seed}"

    def _generate_api_key(self) -> str:
        """Generate a mock API key."""
        timestamp = int(time.time())
        random_seed = hashlib.sha256(str(timestamp).encode()).hexdigest()[:16]
        return f"API-{timestamp}-{random_seed}"

    def rotate_credential(self) -> Credential:
        """Rotate the current credential, deactivating the old one."""
        if self._lock:
            raise RuntimeError("Rotation already in progress")
        
        self._lock = True
        try:
            # Deactivate all existing credentials
            for cred in self.credentials:
                cred.is_active = False
            
            # Create new credential
            now = datetime.now()
            new_cred = Credential(
                ein=self._generate_ein(),
                api_key=self._generate_api_key(),
                created_at=now,
                expires_at=now + self.rotation_interval
            )
            self.credentials.append(new_cred)
            logger.info(f"Rotated credential to {new_cred.ein}")
            return new_cred
        finally:
            self._lock = False

    def get_active_credential(self) -> Optional[Credential]:
        """Get the currently active credential."""
        for cred in self.credentials:
            if cred.is_active:
                return cred
        return None

    def check_compliance(self) -> List[ComplianceDeadline]:
        """Check for upcoming compliance deadlines."""
        now = datetime.now()
        overdue = []
        for deadline in self.compliance_deadlines:
            if deadline.due_date < now and deadline.status == "pending":
                deadline.status = "overdue"
                overdue.append(deadline)
        return overdue

    def add_compliance_deadline(self, description: str, due_date: datetime) -> None:
        """Add a new compliance deadline."""
        self.compliance_deadlines.append(ComplianceDeadline(description, due_date))

    def run_rotation_cycle(self) -> Dict:
        """Run a full rotation and compliance check cycle."""
        result = {
            "rotated": False,
            "active_credential": None,
            "overdue_deadlines": []
        }
        
        active_cred = self.get_active_credential()
        if active_cred and active_cred.expires_at <= datetime.now():
            new_cred = self.rotate_credential()
            result["rotated"] = True
            result["active_credential"] = new_cred.ein
        else:
            result["active_credential"] = active_cred.ein if active_cred else None
        
        result["overdue_deadlines"] = self.check_compliance()
        return result

if __name__ == "__main__":
    # Test harness
    rotator = KRAEINDynamicRotator(rotation_interval_hours=1)
    
    # Initial rotation
    cred = rotator.rotate_credential()
    print(f"Initial Credential: {cred.ein}")
    
    # Add a compliance deadline that is overdue
    overdue_date = datetime.now() - timedelta(days=1)
    rotator.add_compliance_deadline("VAT Return", overdue_date)
    
    # Run cycle
    result = rotator.run_rotation_cycle()
    print(f"Rotation Result: {json.dumps(result, indent=2, default=str)}")
    
    # Force expiration and rotate again
    active = rotator.get_active_credential()
    if active:
        active.expires_at = datetime.now() - timedelta(seconds=1)
    
    result2 = rotator.run_rotation_cycle()
    print(f"Second Rotation Result: {json.dumps(result2, indent=2, default=str)}")
    
    assert result["rotated"] == False
    assert result2["rotated"] == True
    assert len(result2["overdue_deadlines"]) == 1
    print("All tests passed.")