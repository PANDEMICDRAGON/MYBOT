"""
Module: nairobi_mango_ripening_sentinel.py
Description: Autonomous sentinel for monitoring peri-urban Nairobi mango cold-chain storage,
             ethylene ripening kinetics, and fungal rot risk thresholds.
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import json
import logging
import math
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MangoRipeningSentinel")


class MangoBatchState:
    """Represents a specific batch of mangoes in cold storage or transit."""
    def __init__(self, batch_id: str, variety: str, initial_firmness_kg: float, storage_temp_c: float, ethylene_ppm: float):
        self.batch_id = batch_id
        self.variety = variety  # e.g., 'Ngowe', 'Apple', 'Tommy Atkins'
        self.firmness_kg = initial_firmness_kg
        self.storage_temp_c = storage_temp_c
        self.ethylene_ppm = ethylene_ppm
        self.ripeness_stage = "Unripe"
        self.spoilage_risk_index = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "variety": self.variety,
            "firmness_kg": round(self.firmness_kg, 2),
            "storage_temp_c": round(self.storage_temp_c, 2),
            "ethylene_ppm": round(self.ethylene_ppm, 2),
            "ripeness_stage": self.ripeness_stage,
            "spoilage_risk_index": round(self.spoilage_risk_index, 4)
        }


class NairobiMangoRipeningSentinel:
    """Monitors, simulates, and optimizes mango ripening chambers in Nairobi cold-chain hubs."""

    def __init__(self, target_market: str = "Wakulima Market, Nairobi"):
        self.target_market = target_market
        self.batches: Dict[str, MangoBatchState] = {}
        logger.info(f"NairobiMangoRipeningSentinel initialized for target: {self.target_market}")

    def register_batch(self, batch_id: str, variety: str, firmness_kg: float, temp_c: float, ethylene: float) -> MangoBatchState:
        batch = MangoBatchState(batch_id, variety, firmness_kg, temp_c, ethylene)
        self._evaluate_batch(batch)
        self.batches[batch_id] = batch
        logger.info(f"Registered mango batch {batch_id} ({variety}). Initial stage: {batch.ripeness_stage}")
        return batch

    def update_telemetry(self, batch_id: str, current_temp_c: float, ethylene_ppm: float, hours_elapsed: float) -> Optional[MangoBatchState]:
        if batch_id not in self.batches:
            logger.error(f"Batch {batch_id} not found in sentinel registry.")
            return None

        batch = self.batches[batch_id]
        batch.storage_temp_c = current_temp_c
        batch.ethylene_ppm = ethylene_ppm

        # Kinetics simulation: Firmness decreases faster with higher temp and ethylene
        firmness_decay_rate = 0.05 * (current_temp_c / 15.0) * (1.0 + (ethylene_ppm / 10.0))
        batch.firmness_kg = max(1.0, batch.firmness_kg - (firmness_decay_rate * (hours_elapsed / 24.0)))

        # Spoilage risk increases if temp exceeds 18C and ethylene exceeds 50ppm for too long
        temp_penalty = max(0.0, current_temp_c - 14.0) * 0.03
        ethylene_penalty = max(0.0, ethylene_ppm - 20.0) * 0.005
        batch.spoilage_risk_index = min(1.0, batch.spoilage_risk_index + ((temp_penalty + ethylene_penalty) * (hours_elapsed / 24.0)))

        self._evaluate_batch(batch)
        return batch

    def _evaluate_batch(self, batch: MangoBatchState):
        # Determine ripeness stage based on firmness (kg pressure test)
        if batch.firmness_kg > 12.0:
            batch.ripeness_stage = "Green / Export Hard"
        elif batch.firmness_kg > 8.0:
            batch.ripeness_stage = "Breaker / Turning"
        elif batch.firmness_kg > 4.0:
            batch.ripeness_stage = "Eating Ripe / Local Retail"
        else:
            batch.ripeness_stage = "Overripe / Dispatch Immediate"

    def generate_ventilation_advice(self, batch_id: str) -> Dict[str, Any]:
        if batch_id not in self.batches:
            return {"status": "error", "message": "Batch not found"}

        batch = self.batches[batch_id]
        advice = "Maintain current environment."
        action_required = False

        if batch.ethylene_ppm > 80.0 and batch.ripeness_stage != "Overripe / Dispatch Immediate":
            advice = "High ethylene accumulation. Purge chamber ventilation to halt accelerated softening."
            action_required = True
        elif batch.storage_temp_c > 16.0 and batch.ripeness_stage == "Green / Export Hard":
            advice = "Temperature too high for green storage. Lower refrigeration to 12°C to prevent premature ripening."
            action_required = True
        elif batch.spoilage_risk_index > 0.7:
            advice = "CRITICAL: Anthracnose/Fungal rot risk elevated. Rapidly move batch to Wakulima Market for immediate clearance."
            action_required = True

        return {
            "batch_id": batch_id,
            "action_required": action_required,
            "recommended_action": advice,
            "current_state": batch.to_dict()
        }


if __name__ == "__main__":
    print("--- Executing Nairobi Mango Ripening Sentinel Test Harness ---")
    sentinel = NairobiMangoRipeningSentinel()
    
    # Register test batch of Ngowe mangoes from Machakos/Kitui transit
    test_batch = sentinel.register_batch(
        batch_id="MGO-NBO-2023-099",
        variety="Ngowe",
        initial_firmness_kg=15.5,
        temp_c=14.0,
        ethylene_ppm=5.0
    )
    print(json.dumps(test_batch.to_dict(), indent=2))

    # Simulate 48 hours with elevated ethylene ripening gas
    updated_batch = sentinel.update_telemetry(
        batch_id="MGO-NBO-2023-099",
        current_temp_c=17.5,
        ethylene_ppm=85.0,
        hours_elapsed=48.0
    )
    print(json.dumps(updated_batch.to_dict(), indent=2))

    advice = sentinel.generate_ventilation_advice("MGO-NBO-2023-099")
    print("Ventilation Advice:", json.dumps(advice, indent=2))
    print("--- Sentinel Test Complete ---")
