"""
Module: shif_compliance_auditor.py
Description: Autonomous Social Health Authority (SHA) & Social Health Insurance Fund (SHIF)
             contribution auditor and claims verification engine for Michael Obiero in
             Nairobi, Kenya.
"""

import ast
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("SHIFComplianceAuditor")


class SHIFComplianceAuditor:
    """
    Calculates, verifies, and audits SHIF statutory contributions under Kenyan law
    (2.75% of gross salary or applicable bands for non-salaried persons) and tracks
    local hospital accreditation status in Nairobi.
    """

    def __init__(self, contribution_rate: float = 0.0275, min_contribution: float = 300.0):
        self.contribution_rate = contribution_rate
        self.min_contribution = min_contribution
        self.audit_log: List[Dict[str, Any]] = []

    def calculate_employee_contribution(self, gross_salary: float) -> float:
        """
        Calculates the mandatory SHIF monthly contribution.
        SHIF is 2.75% of gross salary with a statutory floor if applicable.
        """
        if gross_salary <= 0:
            return 0.0
        computed = gross_salary * self.contribution_rate
        return max(self.min_contribution, round(computed, 2))

    def audit_employer_remittance(self, employee_id: str, gross_salary: float, remitted_amount: float, month: str) -> Dict[str, Any]:
        """
        Audits whether the remitted employer deduction matches the statutory SHIF formula.
        """
        expected = self.calculate_employee_contribution(gross_salary)
        variance = round(remitted_amount - expected, 2)
        status = "COMPLIANT" if variance == 0 else ("UNDERPAID" if variance < 0 else "OVERPAID")

        audit_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "employee_id": employee_id,
            "month": month,
            "gross_salary": gross_salary,
            "expected_amount": expected,
            "remitted_amount": remitted_amount,
            "variance": variance,
            "status": status
        }

        self.audit_log.append(audit_record)
        logger.info(f"Audited SHIF for {employee_id} [{month}]: Status -> {status} (Variance: {variance} KES)")
        return audit_record

    def verify_facility_tier(self, facility_name: str, location: str) -> Dict[str, Any]:
        """
        Simulates local offline verification of SHA facility tier and accreditation
        across Nairobi corridors.
        """
        known_facilities = {
            "nairobi medical center": {"tier": "Level 4", "sha_accredited": True, "zone": "Nairobi"},
            "AAR nairobi": {"tier": "Level 4", "sha_accredited": True, "zone": "Nairobi"},
            "nairobi hospital": {"tier": "Level 6", "sha_accredited": True, "zone": "Nairobi"},
            "kenyatta national hospital": {"tier": "Level 6", "sha_accredited": True, "zone": "Nairobi"},
            "mater hospital": {"tier": "Level 5", "sha_accredited": True, "zone": "Nairobi"}
        }

        key = facility_name.strip().lower()
        facility_info = known_facilities.get(key, {
            "tier": "Unknown",
            "sha_accredited": False,
            "zone": location
        })

        return {
            "facility_name": facility_name,
            "queried_location": location,
            "accreditation_status": facility_info
        }

    def export_audit_report(self) -> str:
        """Exports the complete audit ledger as a JSON string."""
        return json.dumps(self.audit_log, indent=2)


if __name__ == "__main__":
    print("Initializing Cortanas SHIF Compliance & Audit Engine...")
    auditor = SHIFComplianceAuditor()

    # Test calculation
    sal = 85000.0
    contrib = auditor.calculate_employee_contribution(sal)
    print(f"Gross Salary: {sal} KES -> Expected SHIF (2.75%): {contrib} KES")

    # Test audit
    audit_res = auditor.audit_employer_remittance("MO-001", sal, 2337.50, "2025-03")
    print("Audit Result:", audit_res)

    # Test facility check
    fac_check = auditor.verify_facility_tier("Nairobi Medical Center", "Nairobi")
    print("Facility Verification:", json.dumps(fac_check, indent=2))

    # Self-test AST compilation
    code_source = open(__file__, "r", encoding="utf-8").read()
    ast.parse(code_source)
    print("AST Compilation check passed 100% cleanly.")
