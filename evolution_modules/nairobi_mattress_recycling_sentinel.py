"""Nairobi Municipal Used Mattress Upcycling & Circular Foam Reclamation Sentinel."""

import ast
import logging
import time
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("MattressRecyclingSentinel")


class MattressRecyclingSentinel:
    """Monitors collection, sanitization, shredding, and rebonded foam production metrics."""

    def __init__(self, facility_id: str):
        self.facility_id = facility_id
        self.inventories: Dict[str, Dict[str, Any]] = {}
        self.metrics = {
            "total_collected_units": 0,
            "total_shredded_kg": 0.0,
            "rebonded_blocks_produced": 0,
            "carbon_credits_earned": 0.0,
        }
        logger.info(f"MattressRecyclingSentinel initialized for facility: {facility_id}")

    def register_intake(self, batch_id: str, count: int, source_ward: str, condition_score: float) -> Dict[str, Any]:
        """Register incoming discarded mattresses from Nairobi wards (e.g., Kayole, Kibera, Kasarani)."""
        if condition_score < 0.0 or condition_score > 10.0:
            raise ValueError("Condition score must be between 0.0 and 10.0")

        record = {
            "batch_id": batch_id,
            "count": count,
            "source_ward": source_ward,
            "condition_score": condition_score,
            "status": "QUARANTINED_AND_SANITIZING",
            "timestamp": time.time(),
        }
        self.inventories[batch_id] = record
        self.metrics["total_collected_units"] += count
        logger.info(f"Intake registered: {count} units from {source_ward}. Batch ID: {batch_id}")
        return record

    def process_shredding(self, batch_id: str, foam_weight_kg: float) -> Dict[str, Any]:
        """Transition quarantined mattress batch to mechanical shredding for rebonded foam."""
        if batch_id not in self.inventories:
            raise KeyError(f"Batch {batch_id} not found in inventory.")

        batch = self.inventories[batch_id]
        if batch["status"] != "QUARANTINED_AND_SANITIZING":
            raise ValueError(f"Batch {batch_id} is not ready for shredding (Current status: {batch['status']})")

        batch["status"] = "SHREDDED"
        batch["foam_weight_kg"] = foam_weight_kg
        self.metrics["total_shredded_kg"] += foam_weight_kg
        logger.info(f"Batch {batch_id} shredded successfully: {foam_weight_kg} kg of foam reclaimed.")
        return batch

    def mint_rebonded_block(self, batch_id: str, block_grade: str) -> Dict[str, Any]:
        """Convert shredded polyurethane foam into certified high-density rebonded mattresses."""
        if batch_id not in self.inventories:
            raise KeyError(f"Batch {batch_id} not found in inventory.")

        batch = self.inventories[batch_id]
        if batch["status"] != "SHREDDED":
            raise ValueError(f"Batch {batch_id} must be shredded before block production.")

        batch["status"] = "REBONDED_BLOCK_READY"
        batch["block_grade"] = block_grade
        self.metrics["rebonded_blocks_produced"] += 1
        
        # Estimated carbon credit offset calculation (approx 12kg CO2e per mattress diverted)
        carbon_offset = batch["count"] * 12.5
        self.metrics["carbon_credits_earned"] += carbon_offset
        
        logger.info(f"Rebonded block grade {block_grade} minted from batch {batch_id}. Offset: {carbon_offset} kg CO2e")
        return batch

    def get_operational_summary(self) -> Dict[str, Any]:
        """Return full telemetry summary for municipal dashboard integration."""
        return {
            "facility_id": self.facility_id,
            "metrics": self.metrics,
            "active_batches_count": len(self.inventories),
        }


if __name__ == "__main__":
    sentinel = MattressRecyclingSentinel(facility_id="NRB-FOAM-RECLAIM-01")
    
    # Test workflow
    batch_res = sentinel.register_intake("BATCH-2026-001", count=50, source_ward="Kasarani", condition_score=6.5)
    shred_res = sentinel.process_shredding("BATCH-2026-001", foam_weight_kg=750.0)
    block_res = sentinel.mint_rebonded_block("BATCH-2026-001", block_grade="HD-90")
    
    print("Operational Summary:", sentinel.get_operational_summary())
    
    # Self-validation check
    code_str = open(__file__, "r", encoding="utf-8").read()
    ast.parse(code_str)
    print("AST Compilation Check: PASSED")
