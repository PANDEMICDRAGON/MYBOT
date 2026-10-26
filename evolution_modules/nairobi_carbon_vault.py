import hashlib
import json
import time
from typing import Dict, List, Optional, Any

class NairobiCarbonCreditVault:
    """
    Manages verifiable carbon credit generation units, offset calculations, and audit trails
    tailored for Nairobi community clean cooking and agroforestry projects.
    """

    OFFSET_FACTORS = {
        "clean_cookstove_bioethanol": 3.5,  # Tons CO2e offset per stove per year
        "agroforestry_grevillea": 0.25,     # Tons CO2e offset per mature tree per year
        "biogas_biodigestor": 5.2           # Tons CO2e offset per domestic unit per year
    }

    def __init__(self, operator_id: str = "Michael Obiero") -> None:
        self.operator_id = operator_id
        self.registry: List[Dict[str, Any]] = []
        self.ledger_head: str = "0" * 64

    def register_project(self, project_id: str, project_type: str, location: str, units_count: int) -> Dict[str, Any]:
        if project_type not in self.OFFSET_FACTORS:
            raise ValueError(f"Invalid project type. Choose from {list(self.OFFSET_FACTORS.keys())}")

        annual_offset = units_count * self.OFFSET_FACTORS[project_type]
        
        record = {
            "project_id": project_id,
            "operator": self.operator_id,
            "project_type": project_type,
            "location": location,
            "units_count": units_count,
            "estimated_annual_tco2e": annual_offset,
            "status": "VERIFIED_PENDING_ISSUANCE",
            "timestamp": time.time()
        }
        
        block_hash = self._commit_to_ledger(record)
        record["block_hash"] = block_hash
        self.registry.append(record)
        return record

    def _commit_to_ledger(self, record: Dict[str, Any]) -> str:
        block_data = json.dumps(record, sort_keys=True) + self.ledger_head
        new_hash = hashlib.sha256(block_data.encode("utf-8")).hexdigest()
        self.ledger_head = new_hash
        return new_hash

    def audit_registry(self) -> Dict[str, Any]:
        total_tco2e = sum(r["estimated_annual_tco2e"] for r in self.registry)
        return {
            "operator": self.operator_id,
            "total_projects": len(self.registry),
            "cumulative_verified_tco2e": total_tco2e,
            "ledger_head": self.ledger_head,
            "status": "SECURE"
        }

if __name__ == "__main__":
    vault = NairobiCarbonCreditVault()
    proj1 = vault.register_project("CC-KIBERA-01", "clean_cookstove_bioethanol", "Kibera, Nairobi", 1500)
    proj2 = vault.register_project("AG-KIAMBU-09", "agroforestry_grevillea", "Kiambu County", 8500)
    audit = vault.audit_registry()
    print(json.dumps({"status": "SUCCESS", "audit": audit}, indent=2))
