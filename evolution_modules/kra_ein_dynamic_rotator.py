import json
import time
import hashlib
import secrets
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class EINStatus:
    ein: str
    status: str
    expiry: float
    last_rotated: float

@dataclass
class ComplianceReport:
    is_compliant: bool
    issues: list
    timestamp: float

class KRAEINDynamicRotator:
    def __init__(self, api_key: str, base_url: str = "https://api.kra.go.ke"):
        self.api_key = api_key
        self.base_url = base_url
        self.current_ein: Optional[str] = None
        self.ein_status: Optional[EINStatus] = None
        self.compliance_report: Optional[ComplianceReport] = None

    def generate_ein(self) -> str:
        """Generate a new unique EIN using secure random bytes."""
        random_bytes = secrets.token_bytes(16)
        return hashlib.sha256(random_bytes).hexdigest()[:20]

    def rotate_ein(self) -> bool:
        """Rotate the current EIN to a new one."""
        if not self.current_ein:
            self.current_ein = self.generate_ein()
            self.ein_status = EINStatus(
                ein=self.current_ein,
                status="active",
                expiry=time.time() + 3600 * 24 * 30,
                last_rotated=time.time()
            )
            return True
        else:
            new_ein = self.generate_ein()
            self.ein_status = EINStatus(
                ein=new_ein,
                status="active",
                expiry=time.time() + 3600 * 24 * 30,
                last_rotated=time.time()
            )
            self.current_ein = new_ein
            return True

    def check_compliance(self) -> ComplianceReport:
        """Check the compliance status of the current EIN."""
        issues = []
        if not self.current_ein:
            issues.append("No active EIN")
        elif self.ein_status and self.ein_status.expiry < time.time():
            issues.append("EIN expired")
        
        return ComplianceReport(
            is_compliant=len(issues) == 0,
            issues=issues,
            timestamp=time.time()
        )

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the EIN rotator."""
        return {
            "current_ein": self.current_ein,
            "ein_status": self.ein_status.__dict__ if self.ein_status else None,
            "compliance_report": self.compliance_report.__dict__ if self.compliance_report else None
        }

if __name__ == "__main__":
    rotator = KRAEINDynamicRotator(api_key="test_key")
    rotator.rotate_ein()
    print(json.dumps(rotator.get_status(), indent=2))
    compliance = rotator.check_compliance()
    print(json.dumps(compliance.__dict__, indent=2))