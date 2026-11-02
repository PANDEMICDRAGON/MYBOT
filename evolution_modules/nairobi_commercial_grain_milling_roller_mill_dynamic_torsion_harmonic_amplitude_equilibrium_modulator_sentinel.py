"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Amplitude Equilibrium Modulator Sentinel
Designed for real-time telemetry ingestion, torsional harmonic analysis, and active resonance suppression in commercial flour mills.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillHarmonicEquilibriumSentinel")


class RollerMillTorsionModulator:
    """Monitors torsional load, computes harmonic amplitude equilibrium, and modulates roller mill feedback."""

    def __init__(self, mill_id: str, baseline_rpm: float = 1450.0, harmonic_threshold: float = 0.85):
        self.mill_id = mill_id
        self.baseline_rpm = baseline_rpm
        self.harmonic_threshold = harmonic_threshold
        self.telemetry_history: List[Dict[str, Any]] = []
        self.modulation_state = "OPTIMAL"

    def evaluate_torsion_telemetry(self, current_rpm: float, torque_nm: float, vibration_mm_s: float) -> Dict[str, Any]:
        """Ingests raw sensor feeds and calculates harmonic equilibrium indices."""
        rpm_deviation = abs(current_rpm - self.baseline_rpm) / self.baseline_rpm
        torsional_stress = (torque_nm * vibration_mm_s) / max(self.baseline_rpm, 1.0)
        harmonic_index = min(1.0, (rpm_deviation * 2.0) + (torsional_stress / 500.0))

        if harmonic_index > self.harmonic_threshold:
            self.modulation_state = "CRITICAL_ATTENUATION_REQUIRED"
            modulation_factor = self._compute_modulation_damping(harmonic_index)
        elif harmonic_index > (self.harmonic_threshold * 0.7):
            self.modulation_state = "ADAPTIVE_MODULATION_ACTIVE"
            modulation_factor = 0.95
        else:
            self.modulation_state = "OPTIMAL"
            modulation_factor = 1.0

        telemetry_packet = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "current_rpm": current_rpm,
            "torque_nm": torque_nm,
            "vibration_mm_s": vibration_mm_s,
            "harmonic_index": round(harmonic_index, 4),
            "modulation_state": self.modulation_state,
            "modulation_factor": round(modulation_factor, 4)
        }

        self.telemetry_history.append(telemetry_packet)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return telemetry_packet

    def _compute_modulation_damping(self, index: float) -> float:
        """Calculates active inverter damping frequency modulation factor."""
        return max(0.70, 1.0 - (index * 0.3))


if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Amplitude Equilibrium Modulator Sentinel...")
    sentinel = RollerMillTorsionModulator(mill_id="NAIROBI_INDUSTRIAL_MILL_04")
    
    # Simulate runtime telemetry stream
    for step in range(5):
        sim_rpm = 1450.0 + random.uniform(-45.0, 50.0)
        sim_torque = 320.0 + random.uniform(-30.0, 85.0)
        sim_vibration = 2.1 + random.uniform(0.1, 1.8)
        
        result = sentinel.evaluate_torsion_telemetry(sim_rpm, sim_torque, sim_vibration)
        logger.info(f"Telemetry Step {step+1}: {result}")
        time.sleep(0.1)
    
    logger.info("Roller Mill Harmonic Equilibrium Sentinel verification completed successfully.")
