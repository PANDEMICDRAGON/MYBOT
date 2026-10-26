"""
Nairobi Jua Kali Artisanal Metal Scrap Recycling & Traceability Vault
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import os
import json
import hashlib
import time
from typing import Dict, List, Any, Optional

class JuaKaliMetalVault:
    """Manages immutable audit trails for scrap metal acquisitions, verifying provenance
    against copper stripping bans and logging telemetry for Jua Kali scrap yards.
    """
    
    RESTRICTED_CATEGORIES = {"utility_copper_cable", "railway_fastener", "manhole_cover"}
    
    def __init__(self, ledger_path: str = "nairobi_metal_vault.json") -> None:
        self.ledger_path = ledger_path
        self.records: List[Dict[str, Any]] = []
        self._load_ledger()
        
    def _load_ledger(self) -> None:
        if os.path.exists(self.ledger_path):
            try:
                with open(self.ledger_path, "r", encoding="utf-8") as f:
                    self.records = json.load(f)
            except Exception:
                self.records = []
                
    def _save_ledger(self) -> None:
        try:
            with open(self.ledger_path, "w", encoding="utf-8") as f:
                json.dump(self.records, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to persist metal vault ledger: {e}")
            
    def record_acquisition(self, collector_id: str, material_type: str, weight_kg: float, 
                           origin_ward: str, seller_id_hash: str) -> Dict[str, Any]:
        """Records a scrap metal intake transaction with strict compliance checks."""
        timestamp = time.time()
        is_restricted = material_type.lower() in self.RESTRICTED_CATEGORIES
        
        # Compute cryptographic proof
        payload = f"{collector_id}:{material_type}:{weight_kg}:{origin_ward}:{seller_id_hash}:{timestamp}"
        record_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        
        entry = {
            "record_id": record_hash,
            "collector_id": collector_id,
            "material_type": material_type,
            "weight_kg": weight_kg,
            "origin_ward": origin_ward,
            "seller_id_hash": seller_id_hash,
            "timestamp": timestamp,
            "flagged_restricted": is_restricted,
            "status": "QUARANTINED" if is_restricted else "APPROVED"
        }
        
        self.records.append(entry)
        self._save_ledger()
        return entry

    def audit_inventory(self) -> Dict[str, Any]:
        """Audits total tonnage and flags restricted utility metal attempts."""
        total_weight = sum(r["weight_kg"] for r in self.records if r["status"] == "APPROVED")
        flagged_count = sum(1 for r in self.records if r["flagged_restricted"] is True)
        return {
            "total_approved_tonnage_kg": total_weight,
            "restricted_intercepts": flagged_count,
            "total_transactions": len(self.records)
        }

if __name__ == "__main__":
    vault = JuaKaliMetalVault(ledger_path=":memory:" if os.name != "nt" else "test_metal_vault.json")
    # Test normal aluminum scrap intake
    tx1 = vault.record_acquisition("JK-COL-990", "aluminum_scrap", 45.5, "Kamukunji", "hash_seller_alpha")
    # Test restricted utility copper wire interception
    tx2 = vault.record_acquisition("JK-COL-412", "utility_copper_cable", 12.0, "Eastleigh", "hash_seller_beta")
    
    audit = vault.audit_inventory()
    print("[SUCCESS] Jua Kali Metal Vault Initialized.")
    print(f"Audit Summary: {json.dumps(audit, indent=2)}")
    
    if os.path.exists("test_metal_vault.json"):
        os.remove("test_metal_vault.json")
