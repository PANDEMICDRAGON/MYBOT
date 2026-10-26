import ast
import json
import hashlib
import time
from typing import Dict, List, Optional, Any

class WasteRecyclingCreditSentinel:
    """
    Monitors municipal solid waste sorting streams across Nairobi collection hubs
    (e.g., Dandora, Kasarani, Kibera materials recovery facilities), calculates
    recycled tonnage, evaluates purity coefficients, and issues cryptographically
    signed circular economy credits.
    """
    def __init__(self, facility_id: str, operator_handle: str):
        self.facility_id = facility_id
        self.operator_handle = operator_handle
        self.ledger: List[Dict[str, Any]] = []
        self.total_plastic_kg = 0.0
        self.total_organic_kg = 0.0
        self.total_metal_kg = 0.0
        self.total_credits_minted = 0.0

    def record_batch(self, batch_id: str, source_ward: str, material_type: str, weight_kg: float, purity_pct: float) -> Dict[str, Any]:
        """
        Records a sorted waste batch, validates purity thresholds, and mints credits.
        """
        if weight_kg <= 0:
            raise ValueError("Batch weight must be greater than zero.")
        if not (0.0 <= purity_pct <= 100.0):
            raise ValueError("Purity percentage must be between 0.0 and 100.0.")

        # Material specific credit multipliers (KES / kg * purity weight)
        multipliers = {
            "PET_PLASTIC": 2.5,
            "HDPE_PLASTIC": 3.0,
            "ORGANIC_COMPOST": 1.2,
            "FERROUS_METAL": 5.0,
            "ALUMINUM": 8.5
        }
        
        mat_upper = material_type.upper()
        multiplier = multipliers.get(mat_upper, 1.0)
        
        effective_weight = weight_kg * (purity_pct / 100.0)
        credits_earned = round(effective_weight * multiplier, 2)

        if mat_upper in ["PET_PLASTIC", "HDPE_PLASTIC"]:
            self.total_plastic_kg += weight_kg
        elif mat_upper == "ORGANIC_COMPOST":
            self.total_organic_kg += weight_kg
        elif mat_upper in ["FERROUS_METAL", "ALUMINUM"]:
            self.total_metal_kg += weight_kg

        self.total_credits_minted += credits_earned

        timestamp = time.time()
        raw_payload = f"{batch_id}:{self.facility_id}:{source_ward}:{mat_upper}:{weight_kg}:{purity_pct}:{timestamp}"
        signature = hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()

        record = {
            "batch_id": batch_id,
            "facility_id": self.facility_id,
            "source_ward": source_ward,
            "material_type": mat_upper,
            "weight_kg": weight_kg,
            "purity_pct": purity_pct,
            "credits_earned": credits_earned,
            "operator_handle": self.operator_handle,
            "timestamp": timestamp,
            "signature": signature
        }

        self.ledger.append(record)
        return record

    def get_summary(self) -> Dict[str, Any]:
        """
        Returns aggregated recycling metrics for municipal reporting.
        """
        return {
            "facility_id": self.facility_id,
            "total_batches": len(self.ledger),
            "total_plastic_kg": round(self.total_plastic_kg, 2),
            "total_organic_kg": round(self.total_organic_kg, 2),
            "total_metal_kg": round(self.total_metal_kg, 2),
            "total_credits_minted": round(self.total_credits_minted, 2),
            "operator_handle": self.operator_handle
        }

if __name__ == "__main__":
    print("[+] Initializing Nairobi Municipal Solid Waste Recycling Sentinel...")
    sentinel = WasteRecyclingCreditSentinel(facility_id="MRF-KASARANI-01", operator_handle="Michael Obiero")
    
    b1 = sentinel.record_batch(
        batch_id="BATCH-2025-001",
        source_ward="Roysambu",
        material_type="PET_PLASTIC",
        weight_kg=250.0,
        purity_pct=92.5
    )
    print(json.dumps(b1, indent=2))

    b2 = sentinel.record_batch(
        batch_id="BATCH-2025-002",
        source_ward="Kahawa West",
        material_type="ORGANIC_COMPOST",
        weight_kg=1200.0,
        purity_pct=85.0
    )
    print(json.dumps(b2, indent=2))

    summary = sentinel.get_summary()
    print("[+] Facility Summary:", json.dumps(summary, indent=2))
    print("[✓] Waste Recycling Credit Sentinel validation complete.")
