"""
Nairobi Commercial Grain Milling Automatic Scale & Weigher Sentinel
Autonomous Evolutionary Architecture for Cortana

Monitors automatic bulk scales, hopper weighers, and load cell stability in high-volume
grain processing plants, preventing calibration drift, batch underweight anomalies, and
overfill hazards.
"""

import time
import math
import random
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GrainWeigherSentinel")


class GrainWeigherSentinel:
    def __init__(self, target_batch_kg: float = 500.0, tolerance_pct: float = 0.5):
        self.target_batch_kg = target_batch_kg
        self.tolerance_pct = tolerance_pct
        self.calibration_offset = 0.0
        self.batch_count = 0
        self.anomaly_count = 0
        self.drift_history: List[float] = []

    def inspect_batch(self, measured_weight: float, load_cell_impedance_ohms: float) -> Dict[str, Any]:
        """Inspects an incoming batch weight and load cell telemetry against target parameters."""
        self.batch_count += 1
        error_margin = ((measured_weight - self.target_batch_kg) / self.target_batch_kg) * 100.0
        self.drift_history.append(error_margin)
        if len(self.drift_history) > 50:
            self.drift_history.pop(0)

        status = "OPTIMAL"
        action_required = False

        # Check tolerance limits
        if abs(error_margin) > self.tolerance_pct:
            status = "OUT_OF_TOLERANCE"
            action_required = True
            self.anomaly_count += 1

        # Check load cell impedance anomaly (typical healthy range: 350 +/- 5 ohms)
        if not (345.0 <= load_cell_impedance_ohms <= 355.0):
            status = "ELECTRICAL_DRIFT"
            action_required = True
            self.anomaly_count += 1

        # Rolling drift analysis
        avg_drift = sum(self.drift_history) / len(self.drift_history)
        if abs(avg_drift) > (self.tolerance_pct / 2.0):
            self.calibration_offset -= avg_drift * 0.1  # Auto-compensate offset
            logger.warning(f"[WeigherSentinel] Systematic drift detected ({avg_drift:.3f}%). Auto-compensating offset.")

        return {
            "batch_id": self.batch_count,
            "target_kg": self.target_batch_kg,
            "measured_kg": measured_weight,
            "error_pct": round(error_margin, 3),
            "impedance_ohms": load_cell_impedance_ohms,
            "status": status,
            "action_required": action_required,
            "calibration_offset": round(self.calibration_offset, 4),
            "timestamp": time.time()
        }

    def get_diagnostics(self) -> Dict[str, Any]:
        """Returns system health diagnostics."""
        return {
            "total_batches_inspected": self.batch_count,
            "total_anomalies": self.anomaly_count,
            "current_calibration_offset": self.calibration_offset,
            "recent_mean_drift_pct": sum(self.drift_history) / len(self.drift_history) if self.drift_history else 0.0
        }


if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Automatic Scale & Weigher Sentinel...")
    sentinel = GrainWeigherSentinel(target_batch_kg=1000.0, tolerance_pct=0.3)

    # Simulate batch inspections
    for i in range(1, 6):
        simulated_weight = 1000.0 + random.uniform(-4.0, 4.0)
        if i == 4:
            simulated_weight = 1010.0  # Inject batch anomaly
        sim_impedance = 350.0 + random.uniform(-2.0, 2.0)
        
        report = sentinel.inspect_batch(simulated_weight, sim_impedance)
        logger.info(f"Batch Report #{i}: {report}")

    logger.info(f"Final Diagnostics: {sentinel.get_diagnostics()}")
    logger.info("Grain Weigher Sentinel test sequence completed successfully.")
