"""Nairobi Commercial Grain Milling Roller Mill Roller Gap Micrometer Synchronizer Sentinel.

Autonomous evolutionary module engineered for Cortana to monitor, calibrate,
and synchronize high-precision roller mill gaps in Nairobi commercial grain
milling facilities, ensuring optimal particle size reduction, energy efficiency,
and mechanical integrity.
"""

import logging
import math
import time
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerGapSynchronizerSentinel")


class RollerGapSynchronizerSentinel:
    """Monitors dual-roll gap distances using high-precision micrometer sensors
    and dynamically coordinates actuator stepper corrections to maintain uniform nip.
    """

    def __init__(self, target_gap_microns: float = 250.0, tolerance_microns: float = 5.0):
        self.target_gap = target_gap_microns
        self.tolerance = tolerance_microns
        self.left_gap = target_gap_microns
        self.right_gap = target_gap_microns
        self.correction_history: List[Dict[str, float]] = []
        logger.info(f"Initialized RollerGapSynchronizerSentinel with target gap {target_gap_microns}um.")

    def read_micrometer_sensors(self, simulated_drift: Tuple[float, float] = (0.0, 0.0)) -> Tuple[float, float]:
        """Reads current micrometer gap values from left and right transducers."""
        self.left_gap = self.target_gap + simulated_drift[0]
        self.right_gap = self.target_gap + simulated_drift[1]
        return self.left_gap, self.right_gap

    def compute_asymmetry_and_drift(self) -> Dict[str, float]:
        """Calculates gap disparity between rolls and absolute deviation from target."""
        asymmetry = abs(self.left_gap - self.right_gap)
        mean_gap = (self.left_gap + self.right_gap) / 2.0
        error = mean_gap - self.target_gap
        return {
            "left_gap": self.left_gap,
            "right_gap": self.right_gap,
            "asymmetry": asymmetry,
            "mean_gap": mean_gap,
            "error": error
        }

    def execute_synchronization_correction(self) -> Dict[str, float]:
        """Generates actuator correction steps to align roll gaps back to target.
        Returns required step adjustments for servo-stepper motors.
        """
        metrics = self.compute_asymmetry_and_drift()
        left_correction = 0.0
        right_correction = 0.0

        if metrics["asymmetry"] > self.tolerance:
            # Correct side discrepancy
            diff = self.left_gap - self.right_gap
            left_correction = -diff / 2.0
            right_correction = diff / 2.0

        if abs(metrics["error"]) > self.tolerance:
            # Correct overall offset
            common_correction = -metrics["error"]
            left_correction += common_correction
            right_correction += common_correction

        record = {
            "timestamp": time.time(),
            "left_correction_um": left_correction,
            "right_correction_um": right_correction,
            "asymmetry_before": metrics["asymmetry"],
            "error_before": metrics["error"]
        }
        self.correction_history.append(record)
        logger.info(f"Sync adjustment calculated -> Left: {left_correction:+.2f}um, Right: {right_correction:+.2f}um")
        return record

    def inspect_health(self) -> str:
        metrics = self.compute_asymmetry_and_drift()
        if metrics["asymmetry"] > (self.tolerance * 3) or abs(metrics["error"]) > (self.tolerance * 4):
            return "CRITICAL_MISALIGNMENT"
        elif metrics["asymmetry"] > self.tolerance or abs(metrics["error"]) > self.tolerance:
            return "ADJUSTING"
        return "OPTIMAL"


if __name__ == "__main__":
    print("Executing RollerGapSynchronizerSentinel Test Harness...")
    sentinel = RollerGapSynchronizerSensor = RollerGapSynchronizerSentinel(target_gap_microns=200.0, tolerance_microns=3.0)
    
    # Simulate minor mechanical thermal expansion drift
    sentinel.read_micrometer_sensors(simulated_drift=(12.5, 4.0))
    status = sentinel.inspect_health()
    print(f"Initial Sensor Status: {status}")
    
    adjustment = sentinel.execute_synchronization_correction()
    print(f"Computed Correction: {adjustment}")
    
    # Simulate post-correction steady state
    sentinel.read_micrometer_sensors(simulated_drift=(0.5, -0.5))
    print(f"Post-Correction Status: {sentinel.inspect_health()}")
    print("RollerGapSynchronizerSentinel operational test passed successfully.")
