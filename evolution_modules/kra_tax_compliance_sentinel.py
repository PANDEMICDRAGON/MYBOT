import time
import hashlib
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('KRA_Tax_Compliance_Sentinel')


class TaxType(Enum):
    """Enum representing different types of taxes in Kenya."""
    VAT = "VAT"
    PAYE = "PAYE"
    WITHHOLDING = "WITHHOLDING"
    CORPORATION = "CORPORATION"
    PROPERTY = "PROPERTY"


@dataclass
class TaxObligation:
    """Represents a single tax obligation."""
    tax_type: TaxType
    amount: float
    due_date: str
    status: str = "PENDING"
    reference_id: str = ""

    def __post_init__(self):
        if not self.reference_id:
            self.reference_id = hashlib.md5(
                f"{self.tax_type.value}_{self.amount}_{self.due_date}".encode()
            ).hexdigest()[:12]


class KRAComplianceEngine:
    """
    Engine for monitoring and managing KRA tax compliance.
    
    Attributes:
        taxpayer_id (str): Unique identifier for the taxpayer.
        obligations (List[TaxObligation]): List of current tax obligations.
        audit_log (List[Dict]): Log of compliance actions.
    """

    def __init__(self, taxpayer_id: str):
        self.taxpayer_id = taxpayer_id
        self.obligations: List[TaxObligation] = []
        self.audit_log: List[Dict[str, Any]] = []
        self._log_action("INITIALIZATION", f"Compliance engine initialized for {taxpayer_id}")

    def _log_action(self, action: str, details: str) -> None:
        """Log a compliance action to the audit trail."""
        entry = {
            "timestamp": time.time(),
            "action": action,
            "details": details,
            "taxpayer_id": self.taxpayer_id
        }
        self.audit_log.append(entry)
        logger.info(f"[AUDIT] {action}: {details}")

    def add_obligation(self, tax_type: TaxType, amount: float, due_date: str) -> TaxObligation:
        """
        Add a new tax obligation to the compliance engine.
        
        Args:
            tax_type (TaxType): Type of tax.
            amount (float): Amount due.
            due_date (str): Due date in ISO format.
            
        Returns:
            TaxObligation: The created obligation object.
        """
        obligation = TaxObligation(tax_type=tax_type, amount=amount, due_date=due_date)
        self.obligations.append(obligation)
        self._log_action("OBLIGATION_ADDED", f"Added {tax_type.value} obligation of KES {amount}")
        return obligation

    def mark_as_paid(self, reference_id: str) -> bool:
        """
        Mark a tax obligation as paid.
        
        Args:
            reference_id (str): Reference ID of the obligation.
            
        Returns:
            bool: True if the obligation was found and marked as paid, False otherwise.
        """
        for obligation in self.obligations:
            if obligation.reference_id == reference_id:
                obligation.status = "PAID"
                self._log_action("OBLIGATION_PAID", f"Marked {reference_id} as paid")
                return True
        self._log_action("OBLIGATION_NOT_FOUND", f"Could not find obligation {reference_id}")
        return False

    def get_pending_obligations(self) -> List[TaxObligation]:
        """Retrieve all pending tax obligations."""
        return [o for o in self.obligations if o.status == "PENDING"]

    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Generate a compliance report summarizing the current state.
        
        Returns:
            Dict[str, Any]: Compliance report.
        """
        pending = self.get_pending_obligations()
        total_pending = sum(o.amount for o in pending)
        report = {
            "taxpayer_id": self.taxpayer_id,
            "total_obligations": len(self.obligations),
            "pending_obligations": len(pending),
            "total_pending_amount": total_pending,
            "audit_log_entries": len(self.audit_log),
            "status": "COMPLIANT" if not pending else "NON_COMPLIANT"
        }
        self._log_action("REPORT_GENERATED", f"Compliance report generated: {report['status']}")
        return report


def main():
    """Test harness for the KRA Compliance Sentinel."""
    try:
        engine = KRAComplianceEngine(taxpayer_id="KRA-TEST-12345")
        
        # Add sample obligations
        vat_obligation = engine.add_obligation(TaxType.VAT, 15000.0, "2024-12-20")
        paye_obligation = engine.add_obligation(TaxType.PAYE, 8000.0, "2024-12-25")
        
        # Mark one as paid
        engine.mark_as_paid(vat_obligation.reference_id)
        
        # Generate report
        report = engine.generate_compliance_report()
        print(json.dumps(report, indent=2))
        
        # Verify audit log
        assert len(engine.audit_log) >= 4, "Audit log should have at least 4 entries"
        assert report["status"] == "NON_COMPLIANT", "Should be non-compliant due to pending PAYE"
        
        logger.info("KRA Tax Compliance Sentinel test passed successfully.")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    main()