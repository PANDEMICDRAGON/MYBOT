"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Thermal Expansion Compensation Sentinel

Monitors roller bearing temperatures, ambient mill housing thermal gradients, and real-time
micrometer gap feedback to compute dynamic thermal expansion offsets. Automatically compensates
for metal growth to ensure consistent extraction quality in high-throughput maize and wheat mills.
"""

import time
import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("ThermalExpansionSentinel")

class RollerGapThermalExpansionSentinel:
    """
    Calculates and applies thermal expansion compensation coefficients for roller mill gaps
    operating under variable thermal loads in Nairobi industrial milling facilities.
    """
    def __init__(self, baseline_temp_c: float = 25.0, expansion_coefficient: float = 0.012):
        self.baseline_temp_c = baseline_temp_c
        self.expansion_coefficient = expansion_coefficient  # microns per degree Celsius
        self.active_offsets: Dict[str, float] = {}
        logger.info("RollerGapThermalExpansionSentinel initialized with baseline %.1f°C", baseline_temp_c)

    def compute_thermal_offset(self, roller_id: str, current_temp_c: float) -> float:
        """
        Computes the required micrometer gap correction based on temperature deviation from baseline.
        """
        temp_delta = current_temp_c - self.baseline_temp_c
        # Expansion offset in microns
        offset = temp_delta * self.expansion_coefficient
        self.active_offsets[roller_id] = offset
        return offset

    def evaluate_mill_status(self, telemetry_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluates a batch of sensor readings from multiple roller stands and flags thermal anomalies.
        """
        results = []
        for item in telemetry_batch:
            r_id = item.get("roller_id", "UNKNOWN")
            temp = item.get("temperature_c", 25.0)
            nominal_gap = item.get("nominal_gap_microns", 200.0)

            offset = self.compute_thermal_offset(r_id, temp)
            adjusted_gap = nominal_gap - offset

            status = "OPTIMAL"
            if abs(offset) > 15.0:
                status = "HIGH_THERMAL_DRIFT"
            elif abs(offset) > 25.0:
                status = "CRITICAL_THERMAL_ALARM"

            results.append({
                "roller_id": r_id,
                "temperature_c": temp,
                "thermal_offset_microns": round(offset, 3),
                "adjusted_gap_microns": round(adjusted_gap, 3),
                "status": status
            })
        return results

if __name__ == "__main__":
    sentinel = RollerGapThermalExpansionSentinel()
    sample_telemetry = [
        {"roller_id": "STAND_A_FAST", "temperature_c": 42.5, "nominal_gap_microns": 250.0},
        {"roller_id": "STAND_A_SLOW", "temperature_c": 68.0, "nominal_gap_microns": 250.0},
        {"roller_id": "STAND_B_FAST", "temperature_c": 26.1, "nominal_gap_microns": 180.0}
    ]
    evaluations = sentinel.evaluate_mill_status(sample_telemetry)
    for eval_res in evaluations:
        logger.info("Evaluation result: %s", eval_res)
