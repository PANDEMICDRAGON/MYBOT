"""Nairobi Commercial Grain Milling Roller Mill Burr Clearance and Grind Consistency Sentinel."""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillBurrClearanceSentinel")


class RollerMillBurrClearanceSentinel:
    """Monitors roller mill burr/roll clearance micro-metrics, thermal expansion shifts,
    and particle size grind consistency for industrial grain milling operations in Nairobi.
    """

    def __init__(self, target_clearance_mm: float = 0.45, tolerance_mm: float = 0.05):
        self.target_clearance = target_clearance_mm
        self.tolerance = tolerance_mm
        self.clearance_history: List[float] = []
        self.anomaly_count = 0
        logger.info("Initialized RollerMillBurrClearanceSentinel | Target Clearance: %.3fmm", target_clearance_mm)

    def ingest_sensor_reading(self, raw_clearance_mm: float, vibration_hz: float, motor_current_amps: float) -> Dict[str, Any]:
        """Ingests live sensor telemetry from roller mill gap detectors and computes health vectors."""
        self.clearance_history.append(raw_clearance_mm)
        if len(self.clearance_history) > 100:
            self.clearance_history.pop(0)

        delta = raw_clearance_mm - self.target_clearance
        deviation = abs(delta)
        status = "OPTIMAL"
        action_required = False

        if deviation > self.tolerance * 1.5:
            status = "CRITICAL_MISALIGNMENT"
            action_required = True
            self.anomaly_count += 1
        elif deviation > self.tolerance:
            status = "WARNING_DRIFT"
            action_required = True

        # Estimate grind consistency score based on clearance stability and vibration
        stability_factor = max(0.0, 100.0 - (deviation * 200.0) - (vibration_hz * 0.1))

        telemetry = {
            "timestamp": time.time(),
            "raw_clearance_mm": raw_clearance_mm,
            "target_clearance_mm": self.target_clearance,
            "clearance_delta_mm": round(delta, 4),
            "status": status,
            "action_required": action_required,
            "grind_consistency_score": round(stability_factor, 2),
            "motor_load_amps": motor_current_amps,
            "anomaly_count": self.anomaly_count
        }

        if action_required:
            logger.warning("Roller mill gap anomaly detected: %s (Telemetry: %s)", status, telemetry)

        return telemetry

    def calibrate_gap(self, calibration_offset_mm: float) -> bool:
        """Dynamically adjusts target clearance baseline to compensate for thermal expansion."""
        self.target_clearance += calibration_offset_mm
        logger.info("Calibrated roller mill clearance baseline. New target: %.3fmm", self.target_clearance)
        return True


if __name__ == "__main__":
    logger.info("Executing self-test harness for RollerMillBurrClearanceSentinel...")
    sentinel = RollerMillBurrClearanceSentinel(target_clearance_mm=0.40, tolerance_mm=0.03)
    
    # Simulate normal and anomalous readings
    test_readings = [
        (0.402, 12.5, 45.2),
        (0.398, 12.4, 45.0),
        (0.445, 18.2, 52.8),  # Drift warning
        (0.510, 24.1, 61.4)   # Critical misalignment
    ]

    for clearance, vib, amps in test_readings:
        res = sentinel.ingest_sensor_reading(clearance, vib, amps)
        print(f"Telemetry Output: {res}")

    sentinel.calibrate_gap(-0.01)
    print("Self-test complete. Sentinel fully operational.")
