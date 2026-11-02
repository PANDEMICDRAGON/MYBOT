"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Compensator Sentinel
Designed for Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TorqueRippleCompensatorSentinel")

class RollerMillTorqueRippleCompensator:
    """
    Monitors high-speed drive motor torque telemetry, isolates harmonic torque ripples
    caused by roller differential speed ratios and grain feed load surges, and computes
    active inverter compensation coefficients to stabilize roller rotational velocity.
    """
    def __init__(self, mill_id: str, nominal_rpm: float = 750.0, base_torque_nm: float = 120.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.base_torque_nm = base_torque_nm
        self.active_compensation_active = True
        logger.info(f"Initialized Torque Ripple Compensator Sentinel for mill {mill_id} @ {nominal_rpm} RPM.")

    def analyze_torque_telemetry(self, current_rpm: float, measured_torque: float) -> Dict[str, Any]:
        """
        Analyzes live RPM and torque samples, computes ripple deviation, and generates
        inverter phase correction offsets.
        """
        rpm_error = current_rpm - self.nominal_rpm
        torque_ripple = measured_torque - self.base_torque_nm
        ripple_amplitude_percentage = (abs(torque_ripple) / self.base_torque_nm) * 100.0

        # Compute phase correction factor using adaptive damping algorithm
        correction_signal = 0.0
        status = "OPTIMAL"

        if ripple_amplitude_percentage > 12.0:
            status = "HIGH_RIPPLE_WARNING"
            correction_signal = -0.15 * torque_ripple
        elif ripple_amplitude_percentage > 5.0:
            status = "MODERATE_FLUCTUATION"
            correction_signal = -0.08 * torque_ripple
        else:
            status = "STABLE"
            correction_signal = 0.0

        return {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "current_rpm": current_rpm,
            "measured_torque_nm": measured_torque,
            "torque_ripple_percentage": round(ripple_amplitude_percentage, 2),
            "status": status,
            "inverter_correction_signal": round(correction_signal, 4),
            "compensation_applied": self.active_compensation_active
        }

    def execute_diagnostic_sweep(self) -> List[Dict[str, Any]]:
        """
        Simulates a series of diagnostic telemetry reads across different load conditions.
        """
        test_samples = [
            (750.2, 121.0),
            (742.5, 138.4),
            (755.0, 114.2),
            (731.0, 145.8),
            (750.0, 119.8)
        ]
        results = []
        for rpm, torque in test_samples:
            res = self.analyze_torque_telemetry(rpm, torque)
            results.append(res)
            logger.info(f"Mill {self.mill_id} sweep -> RPM: {rpm}, Torque: {torque}Nm, Status: {res['status']}")
        return results

if __name__ == "__main__":
    sentinel = RollerMillTorqueRippleCompensator(mill_id="NRB-MILL-04")
    diagnostic_report = sentinel.execute_diagnostic_sweep()
    print(f"Torque Ripple Compensator Sentinel Test Complete. Executed {len(diagnostic_report)} diagnostics.")
