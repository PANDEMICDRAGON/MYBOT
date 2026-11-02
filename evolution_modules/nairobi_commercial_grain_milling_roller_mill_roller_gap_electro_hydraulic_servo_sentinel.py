"""Nairobi Commercial Grain Milling Roller Mill Roller Gap Electro Hydraulic Servo Sentinel

Provides real-time closed-loop monitoring and electro-hydraulic servo correction for roller mill nip gaps in Nairobi commercial grain mills, ensuring precise particle size reduction and preventing mill jamming under fluctuating electrical supply.
"""

import time
import math
import random
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerGapElectroHydraulicServoSentinel")


class RollerGapElectroHydraulicServoSentinel:
    """Monitors and modulates roller mill gap electro-hydraulic actuators in real-time."""

    def __init__(self, target_gap_microns: float = 250.0, tolerance_microns: float = 3.5):
        self.target_gap = target_gap_microns
        self.tolerance = tolerance_microns
        self.hydraulic_pressure_bar = 145.0  # Normal operating bar
        self.servo_valve_position_pct = 50.0
        self.oil_temperature_c = 42.0
        self.error_history: List[float] = []
        self.active_corrections = 0

    def sample_and_compensate(self, measured_gap_microns: float, system_vibration_g: float) -> Dict[str, Any]:
        """Evaluate measured roller gap against target and compute hydraulic servo adjustment."""
        error = measured_gap_microns - self.target_gap
        self.error_history.append(error)
        if len(self.error_history) > 50:
            self.error_history.pop(0)

        correction_needed = abs(error) > self.tolerance
        servo_adjustment = 0.0

        if correction_needed:
            self.active_corrections += 1
            # Proportional-Integral corrective actuator signal
            servo_adjustment = -0.45 * error
            self.servo_valve_position_pct = max(0.0, min(100.0, self.servo_valve_position_pct + servo_adjustment))
            # Simulated slight pressure shift based on valve movement
            self.hydraulic_pressure_bar += servo_adjustment * 0.05

        # Thermal drift simulation
        self.oil_temperature_c += (random.random() - 0.48) * 0.1

        status = {
            "timestamp": time.time(),
            "target_gap_microns": self.target_gap,
            "measured_gap_microns": measured_gap_microns,
            "error_microns": round(error, 2),
            "correction_active": correction_needed,
            "servo_valve_position_pct": round(self.servo_valve_position_pct, 2),
            "hydraulic_pressure_bar": round(self.hydraulic_pressure_bar, 2),
            "oil_temperature_c": round(self.oil_temperature_c, 2),
            "system_vibration_g": round(system_vibration_g, 2),
            "total_corrections": self.active_corrections
        }

        if correction_needed:
            logger.warning(f"[GAP DRIFT DETECTED] Error: {error:.2f}um. Servo adjusted to {self.servo_valve_position_pct:.1f}%")
        else:
            logger.info(f"[STABLE] Roller gap within tolerance ({measured_gap_microns:.2f}um).")

        return status

    def get_diagnostic_report(self) -> Dict[str, Any]:
        """Return summary diagnostics for operator review."""
        avg_error = sum(self.error_history) / len(self.error_history) if self.error_history else 0.0
        return {
            "status": "OPERATIONAL",
            "mean_recent_error_microns": round(avg_error, 2),
            "total_corrections_logged": self.active_corrections,
            "current_oil_temp_c": round(self.oil_temperature_c, 2),
            "hydraulic_health": "OPTIMAL" if self.oil_temperature_c < 65.0 else "THERMAL_WARNING"
        }


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Roller Gap Electro Hydraulic Servo Sentinel...")
    sentinel = RollerGapElectroHydraulicServoSentinel(target_gap_microns=200.0, tolerance_microns=2.0)
    
    # Simulate minor gap variations under mill load
    simulated_readings = [
        (200.5, 0.4),
        (201.2, 0.5),
        (205.8, 1.2),  # Out of tolerance
        (202.1, 0.6),
        (199.1, 0.3),
        (195.4, 1.5)   # Out of tolerance
    ];

    for gap, vib in simulated_readings:
        res = sentinel.sample_and_compensate(gap, vib)
        print(res)

    print("Diagnostic Report:", sentinel.get_diagnostic_report())
    print("Sentinel test complete.")
