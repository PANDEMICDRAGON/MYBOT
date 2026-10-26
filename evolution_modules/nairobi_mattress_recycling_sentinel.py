"""
Nairobi Post-Consumer Polyurethane Foam Mattress Upcycling & Circular Economy Ledger
Author: Cortana, Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides tracking for discarded foam mattress collection, weight verification, shredding,
binder infusion, hydraulic press telemetry for rebonded foam blocks, and carbon credit issuance.
"""

import hashlib
import json
import time
from typing import Dict, List, Optional


class MattressRecyclingLedger:
    """Manages the lifecycle of discarded polyurethane mattresses diverted from Nairobi dumpsites."""

    CARBON_OFFSET_PER_KG_FOAM: float = 2.4  # kg CO2e offset per kg recycled polyurethane

    def __init__(self, facility_id: str = "NRB_FOAM_CYCLE_01") -> None:
        self.facility_id = facility_id
        self.collection_batches: Dict[str, dict] = {}
        self.production_blocks: Dict[str, dict] = {}
        self.audit_trail: List[dict] = []
        self._log_event("INIT", {"facility_id": facility_id, "status": "online"})

    def _log_event(self, event_type: str, payload: dict) -> None:
        entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "payload": payload,
            "hash": ""
        }
        prev_hash = self.audit_trail[-1]["hash"] if self.audit_trail else "0" * 64
        raw_str = f"{prev_hash}:{entry['timestamp']}:{event_type}:{json.dumps(payload, sort_keys=True)}"
        entry["hash"] = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
        self.audit_trail.append(entry)

    def register_collection(self, batch_id: str, source_ward: str, mattress_count: int, total_weight_kg: float) -> dict:
        """Registers incoming discarded mattresses collected from Nairobi estates."""
        if batch_id in self.collection_batches:
            raise ValueError(f"Batch {batch_id} already exists.")

        if total_weight_kg <= 0 or mattress_count <= 0:
            raise ValueError("Invalid mattress count or weight.")

        batch_data = {
            "batch_id": batch_id,
            "source_ward": source_ward,
            "mattress_count": mattress_count,
            "total_weight_kg": total_weight_kg,
            "status": "COLLECTED"
        }
        self.collection_batches[batch_id] = batch_data
        self._log_event("COLLECTION_REGISTERED", batch_data)
        return batch_data

    def process_shredding_and_pressing(self, block_id: str, batch_ids: List[str], binder_liters: float, pressure_bar: float) -> dict:
        """Transforms collected mattress batches into high-density rebonded foam blocks."""
        total_input_weight = 0.0
        for bid in batch_ids:
            if bid not in self.collection_batches:
                raise KeyError(f"Collection batch {bid} not found.")
            b = self.collection_batches[bid]
            if b["status"] != "COLLECTED":
                raise ValueError(f"Batch {bid} already processed.")
            total_input_weight += b["total_weight_kg"]
            b["status"] = "SHREDDED_AND_PRESSED"

        if pressure_bar < 120.0:
            raise ValueError(f"Insufficient hydraulic pressure ({pressure_bar} bar). Minimum 120 bar required for structural rebonding.")

        output_weight_kg = total_input_weight + (binder_liters * 1.1)  # assuming binder adds minor mass
        carbon_offset_kg = output_weight_kg * self.CARBON_OFFSET_PER_KG_FOAM

        block_data = {
            "block_id": block_id,
            "source_batches": batch_ids,
            "input_foam_kg": total_input_weight,
            "binder_liters": binder_liters,
            "pressure_bar": pressure_bar,
            "output_weight_kg": output_weight_kg,
            "carbon_offset_kg": carbon_offset_kg,
            "status": "READY_FOR_MARKET"
        }

        self.production_blocks[block_id] = block_data
        self._log_event("BLOCK_PRODUCED", block_data)
        return block_data

    def verify_ledger_integrity(self) -> bool:
        """Cryptographically audits the immutable chain."""
        for i in range(1, len(self.audit_trail)):
            prev = self.audit_trail[i - 1]
            curr = self.audit_trail[i]
            raw_str = f"{prev['hash']}:{curr['timestamp']}:{curr['event_type']}:{json.dumps(curr['payload'], sort_keys=True)}"
            expected_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
            if curr["hash"] != expected_hash:
                return False
        return True


if __name__ == "__main__":
    print("Initializing Nairobi Mattress Recycling Ledger...")
    ledger = MattressRecyclingLedger(facility_id="NRB_FOAM_EMBAKASI_01")
    
    b1 = ledger.register_collection("BATCH_2025_001", "Embakasi Ward", 45, 675.0)
    b2 = ledger.register_collection("BATCH_2025_002", "Kasarani Ward", 30, 420.0)
    
    print(f"Registered Batches: {len(ledger.collection_batches)}")
    
    block = ledger.process_shredding_and_pressing(
        block_id="BLOCK_RB_901",
        batch_ids=["BATCH_2025_001", "BATCH_2025_002"],
        binder_liters=55.0,
        pressure_bar=150.0
    )
    
    print(f"Produced Rebonded Block: {block['block_id']}, Carbon Offset: {block['carbon_offset_kg']:.2f} kg CO2e")
    print(f"Ledger Integrity Verified: {ledger.verify_ledger_integrity()}")
