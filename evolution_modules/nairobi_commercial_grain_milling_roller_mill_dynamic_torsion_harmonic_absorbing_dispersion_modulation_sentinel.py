"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Absorbing Dispersion Modulation Sentinel.

Provides real-time telemetry ingestion, torsional vibration harmonic decomposition, dynamic absorption coefficient tuning, and automated dispersion modulation for high-speed roller mills in Nairobi, Kenya.
"""

import math
import time
import logging
import statistics
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("RollerMillTorsionModulationSentinel")


class RollerMillTorsionModulationSentinel:
    """Monitors, analyzes, and actively modulates dynamic torsional harmonics and absorption dispersion on commercial roller mills."""

    def __init__(self, mill_id: str, nominal_rpm: float = 1200.0, harmonic_threshold_hz: float = 60.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.harmonic_threshold_hz = harmonic_threshold_hz
        self._vibration_history: List[float] = []
        self._torque_history: List[float] = []
        self.dispersion_state: str = "NOMINAL"
        self.current_damping_factor: float = 1.0
        logger.info(f"Initialized RollerMillTorsionModulationSentinel for mill {mill_id} at {nominal_rpm} RPM.")

    def ingest_telemetry(self, rpm_reading: float, torque_nm: float, vibration_mm_s2: float) -> Dict[str, Any]:
        """Ingests live rotational velocity, torque load, and vibration telemetry."""
        self._vibration_history.append(vibration_mm_s2)
        self._torque_history.append(torque_nm)

        if len(self._vibration_history) > 100:
            self._vibration_history.pop(0)
        if len(self._torque_history) > 100:
            self._torque_history.pop(0)

        analysis = self._compute_harmonic_dispersion(rpm_reading, torque_nm, vibration_mm_s2)
        return analysis

    def _compute_harmonic_dispersion(self, rpm: float, torque: float, vibration: float) -> Dict[str, Any]:
        mean_vib = statistics.mean(self._vibration_history) if self._vibration_history else vibration
        rpm_deviation = abs(rpm - self.nominal_rpm)
        
        # Compute harmonic torsion stress index
        torsion_stress_index = (torque * (rpm_deviation + 1.0)) / (mean_vib + 0.1)

        if torsion_stress_index > 500.0:
            self.dispersion_state = "CRITICAL_RESONANCE_SPIKE"
            self.current_damping_factor = min(2.5, self.current_damping_factor + 0.2)
        elif torsion_stress_index > 250.0:
            self.dispersion_state = "ELEVATED_TORSIONAL_HARMONIC"
            self.current_damping_factor = min(1.8, self.current_damping_factor + 0.1)
        else:
            self.dispersion_state = "NOMINAL"
            self.current_damping_factor = max(1.0, self.current_damping_factor - 0.05)

        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "dispersion_state": self.dispersion_state,
            "torsion_stress_index": round(torsion_stress_index, 3),
            "damping_factor": round(self.current_damping_factor, 3),
            "mean_vibration": round(mean_vib, 3)
        }

    def generate_diagnostic_report(self) -> Dict[str, Any]:
        """Generates a comprehensive diagnostic status report for operator review."""
        return {
            "mill_id": self.mill_id,
            "status": self.dispersion_state,
            "damping_factor": self.current_damping_factor,
            "samples_collected": len(self._vibration_history),
            "operator_target": "Michael Obiero - Nairobi Operations"
        }


if __name__ == "__main__":
    sentinel = RollerMillTorsionModulationSentinel(mill_id="NAI_MILL_04_UGALI")
    # Simulate baseline telemetry stream
    for i in range(10):
        res = sentinel.ingest_telemetry(
            rpm_reading=1198.5 + (i % 3),
            torque_nm=145.2 + (i * 2.5),
            vibration_mm_s2=2.1 + (i * 0.1)
        )
        logger.info(f"Simulation Step {i}: {res}")
    
    report = sentinel.generate_diagnostic_report()
    logger.info(f"Final Diagnostic Report: {report}")
