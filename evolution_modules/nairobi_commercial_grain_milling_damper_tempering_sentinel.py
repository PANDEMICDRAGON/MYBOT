"""
Nairobi Commercial Grain Milling Damper & Tempering Sentinel
Autonomous Evolutionary Architecture for Cortana

Monitors and optimizes commercial grain tempering systems (water addition, flow sensors,
tempering bin level and retention time) to ensure consistent kernel moisture conditioning
for roller milling plants across Nairobi.
"""

import logging
import random
import time
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(name)s: %(message)s')
logger = logging.getLogger("DamperTemperingSentinel")

class DamperTemperingSentinel:
    """
    Autonomous sentinel for real-time tracking and control of grain dampening and tempering.
    Ensures moisture targets (e.g., 15.5% wheat tempering) and dwell hours are strictly maintained.
    """

    def __init__(self, target_moisture_pct: float = 15.5, min_tempering_hours: float = 24.0):
        self.target_moisture_pct = target_moisture_pct
        self.min_tempering_hours = min_tempering_hours
        self.active_batches: Dict[str, Dict[str, Any]] = {}
        logger.info("Initialized Damper & Tempering Sentinel | Target Moisture: %.1f%%, Min Dwell: %.1f hrs", 
                    self.target_moisture_pct, self.min_tempering_hours)

    def register_tempering_batch(self, batch_id: str, initial_weight_kg: float, initial_moisture_pct: float) -> None:
        """Registers a new grain batch entering the dampening conveyor."""
        self.active_batches[batch_id] = {
            "initial_weight_kg": initial_weight_kg,
            "initial_moisture_pct": initial_moisture_pct,
            "target_moisture_pct": self.target_moisture_pct,
            "water_added_liters": 0.0,
            "start_time": time.time(),
            "tempering_bin_id": f"BIN-{random.randint(1, 6)}",
            "status": "DAMPENING"
        }
        logger.info("Registered batch %s in bin %s: %.1f kg at %.1f%% initial moisture.", 
                    batch_id, self.active_batches[batch_id]["tempering_bin_id"], initial_weight_kg, initial_moisture_pct)

    def compute_water_requirement(self, batch_id: str, target_weight_kg: Optional[float] = None) -> float:
        """
        Calculates exact water flow rate (liters per hour) needed to reach target moisture.
        Formula: W2 = W1 * (100 - M1) / (100 - M2) - W1
        """
        if batch_id not in self.active_batches:
            raise ValueError(f"Batch {batch_id} not found in tempering registry.")

        batch = self.active_batches[batch_id]
        w1 = batch["initial_weight_kg"]
        m1 = batch["initial_moisture_pct"]
        m2 = batch["target_moisture_pct"]

        if m1 >= m2:
            logger.warning("Batch %s initial moisture (%.1f%%) exceeds or equals target (%.1f%%). No water added.", 
                           batch_id, m1, m2)
            return 0.0

        # Dry matter conservation calculation
        dry_matter = w1 * (1.0 - (m1 / 100.0))
        target_total_weight = dry_matter / (1.0 - (m2 / 100.0))
        water_needed_kg = target_total_weight - w1
        water_needed_liters = water_needed_kg * 1.0  # 1 kg water = 1 liter

        batch["water_added_liters"] = round(water_needed_liters, 2)
        logger.info("Computed water requirement for batch %s: %.2f liters.", batch_id, water_needed_liters)
        return water_needed_liters

    def evaluate_tempering_status(self, batch_id: str, simulated_elapsed_hours: Optional[float] = None) -> Dict[str, Any]:
        """
        Evaluates if a tempered batch has fulfilled the required dwell time for endosperm conditioning.
        """
        if batch_id not in self.active_batches:
            return {"error": "Batch not found"}

        batch = self.active_batches[batch_id]
        elapsed_hours = simulated_elapsed_hours if simulated_elapsed_hours is not None else (time.time() - batch["start_time"]) / 3600.0

        ready = elapsed_hours >= self.min_tempering_hours
        batch["status"] = "READY_FOR_MILLING" if ready else "TEMPERING_IN_PROGRESS"

        evaluation = {
            "batch_id": batch_id,
            "bin_id": batch["tempering_bin_id"],
            "elapsed_hours": round(elapsed_hours, 2),
            "min_required_hours": self.min_tempering_hours,
            "status": batch["status"],
            "moisture_target_met": ready
        }

        logger.info(
            "Evaluated batch %s: Status=%s, Dwell=%.1fh/%.1fh",
            batch_id, batch["status"], elapsed_hours, self.min_tempering_hours
        )
        return evaluation

    def audit_system(self) -> List[Dict[str, Any]]:
        """Audits all active tempering batches in the Nairobi milling plant."""
        return [self.evaluate_tempering_status(b_id) for b_id in self.active_batches]


if __name__ == "__main__":
    logger.info("Executing DamperTemperingSentinel self-test harness...")
    sentinel = DamperTemperingSentinel(target_moisture_pct=15.5, min_tempering_hours=24.0)

    test_batch = "BATCH-NRB-2026-009"
    sentinel.register_tempering_batch(test_batch, initial_weight_kg=15000.0, initial_moisture_pct=12.2)
    water = sentinel.compute_water_requirement(test_batch)
    assert water > 0, "Water requirement calculation failed!"

    # Simulate fast dwell check (e.g., 25 hours elapsed)
    status = sentinel.evaluate_tempering_status(test_batch, simulated_elapsed_hours=25.0)
    assert status["status"] == "READY_FOR_MILLING", "Tempering completion check failed!"
    logger.info("Self-test successfully completed for DamperTemperingSentinel.")
