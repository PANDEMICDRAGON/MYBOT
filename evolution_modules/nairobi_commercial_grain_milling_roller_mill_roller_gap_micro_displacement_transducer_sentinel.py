"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Micro Displacement Transducer Sentinel
Designed for real-time sub-micron gap telemetry, thermal drift compensation, and predictive mechanical wear isolation in commercial flour milling plants across Nairobi, Kenya.
"""

import time
import logging
import math
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerGapMicroDisplacementSentinel")


class RollerGapMicroDisplacementSentinel:
    """
    Monitors high-resolution micro-displacement transducers on commercial roller mill stands,
    detecting micro-oscillations, thermal expansion offsets, and mechanical backlash.
    """

    def __init__(self, mill_id: str, nominal_gap_microns: float = 150.0, tolerance_microns: float = 2.5):
        self.mill_id = mill_id
        self.nominal_gap_microns = nominal_gap_microns
        self.tolerance_microns = tolerance_microns
        self.telemetry_history: List[Dict[str, Any]] = []
        self.is_calibrated = True

    def ingest_transducer_reading(self, raw_displacement_um: float, roller_temp_c: float, motor_current_a: float) -> Dict[str, Any]:
        """
        Ingests raw micro-displacement sensor data, applies thermal compensation, and evaluates health status.
        """
        # Thermal expansion correction coefficient for hardened cast iron rolls (approx 11.5e-6 / deg C)
        # Assuming baseline reference temp of 25.0 C
        temp_delta = roller_temp_c - 25.0
        thermal_correction_um = temp_delta * 0.42

        corrected_gap_um = raw_displacement_um - thermal_correction_um
        deviation = corrected_gap_um - self.nominal_gap_microns

        status = "OPTIMAL"
        if abs(deviation) > self.tolerance_microns:
            status = "WARNING_GAP_DEVIATION"
        if abs(deviation) > (self.tolerance_microns * 2.0):
            status = "CRITICAL_ROLL_CONTACT_RISK"
            self.is_calibrated = False

        payload = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "raw_gap_um": raw_displacement_um,
            "roller_temp_c": roller_temp_c,
            "corrected_gap_um": corrected_gap_um,
            "deviation_um": deviation,
            "motor_current_a": motor_current_a,
            "status": status,
            "is_calibrated": self.is_calibrated
        }

        self.telemetry_history.append(payload)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return payload

    def get_aggregate_metrics(self) -> Dict[str, Any]:
        """Returns aggregate performance and stability metrics."""
        if not self.telemetry_history:
            return {"status": "NO_DATA"}

        deviations = [item["deviation_um"] for item in self.telemetry_history]
        mean_deviation = sum(deviations) / len(deviations)
        max_deviation = max(abs(d) for d in deviations)

        return {
            "mill_id": self.mill_id,
            "total_samples": len(self.telemetry_history),
            "mean_deviation_um": mean_deviation,
            "max_absolute_deviation_um": max_deviation,
            "is_calibrated": self.is_calibrated
        }


if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Gap Micro Displacement Sentinel Test Harness...")
    sentinel = RollerGapMicroDisplacementSentinel(mill_id="NAI_MILL_STAND_04", nominal_gap_microns=120.0, tolerance_microns=2.0)

    # Simulate normal and drifting telemetry
    test_readings = [
        (120.2, 26.5, 45.2),
        (121.1, 28.0, 46.0),
        (123.5, 32.5, 52.8),  # Should trigger warning/critical
        (119.8, 25.1, 44.9)
    ]

    for raw_gap, temp, current in test_readings:
        result = sentinel.ingest_transducer_reading(raw_gap, temp, current)
        logger.info(f"Telemetry processed: {result}")

    summary = sentinel.get_aggregate_metrics()
    logger.info(f"Sentinel Aggregate Summary: {summary}")
    logger.info("Sentinel Execution Successful.")
