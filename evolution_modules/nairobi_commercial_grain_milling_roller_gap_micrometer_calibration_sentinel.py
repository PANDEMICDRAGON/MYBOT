import logging
import time
import math
import random
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerGapMicrometerCalibrationSentinel")

class RollerGapMicrometerCalibrationSentinel:
    """
    Monitors and self-calibrates roller mill gap spacing using high-resolution
    optical micrometer feedback and thermal expansion compensation matrices.
    """
    def __init__(self, mill_id: str, target_gap_microns: float = 150.0):
        self.mill_id = mill_id
        self.target_gap_microns = target_gap_microns
        self.thermal_coefficient = 0.012  # microns per degree C shift
        self.current_calibration_offset = 0.0
        self.history: List[Dict[str, Any]] = []

    def measure_gap(self, raw_sensor_reading: float, mill_temperature_c: float) -> Dict[str, Any]:
        """
        Evaluates raw optical micrometer sensor feedback, accounts for thermal expansion,
        and calculates necessary stepper motor adjustments.
        """
        thermal_expansion_delta = (mill_temperature_c - 25.0) * self.thermal_coefficient
        adjusted_gap = raw_sensor_reading - thermal_expansion_delta + self.current_calibration_offset
        error = adjusted_gap - self.target_gap_microns

        status = "OPTIMAL"
        correction_step = 0.0

        if abs(error) > 5.0:
            status = "DRIFT_DETECTED"
            correction_step = -error * 0.5  # Proportional correction damping
            self.current_calibration_offset += correction_step
        elif abs(error) > 15.0:
            status = "CRITICAL_MISALIGNMENT"
            correction_step = -error
            self.current_calibration_offset += correction_step

        telemetry = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "raw_reading": raw_sensor_reading,
            "temperature_c": mill_temperature_c,
            "adjusted_gap_microns": adjusted_gap,
            "error_microns": error,
            "status": status,
            "applied_correction_microns": correction_step
        }

        self.history.append(telemetry)
        if len(self.history) > 1000:
            self.history.pop(0)

        return telemetry

    def run_diagnostic_sweep(self) -> Dict[str, Any]:
        """Simulates telemetry sweep across operational temperature bounds."""
        logger.info(f"Executing diagnostic gap calibration sweep for {self.mill_id}...")
        simulated_temp = 25.0 + random.uniform(0.0, 35.0)
        simulated_raw = self.target_gap_microns + random.uniform(-10.0, 12.0)
        result = self.measure_gap(simulated_raw, simulated_temp)
        logger.info(f"Diagnostic Result: {result}")
        return result

if __name__ == "__main__":
    sentinel = RollerGapMicrometerCalibrationSentinel(mill_id="MILL_NAIROBI_INDUSTRIAL_01")
    for _ in range(3):
        sentinel.run_diagnostic_sweep()
    logger.info("RollerGapMicrometerCalibrationSentinel test harness executed successfully.")
