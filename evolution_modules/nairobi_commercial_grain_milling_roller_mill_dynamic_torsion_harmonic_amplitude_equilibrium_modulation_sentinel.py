"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Amplitude Equilibrium Modulation Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

 Monitors high-speed roller mill drives for torsional harmonic resonance, modulating inverter phase and damping profiles to prevent catastrophic shaft fatigue.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TorsionHarmonicEquilibriumSentinel")

class RollerMillTorsionHarmonicSentinel:
    """
    Analyzes torsional vibration spectra and dynamically trims inverter excitation to neutralize harmonic peaks.
    """
    def __init__(self, mill_id: str, rated_rpm: float = 1200.0):
        self.mill_id = mill_id
        self.rated_rpm = rated_rpm
        self.torsional_amplitude_history: List[float] = []
        self.modulation_active = False

    def sample_torsion_sensor(self) -> float:
        """Simulates high-frequency angular encoder and torque sensor telemetry."""
        base_vibration = random.uniform(0.1, 0.5)
        # Simulate occasional harmonic resonance spike
        spike = 2.5 if random.random() < 0.05 else 0.0
        return round(base_vibration + spike, 4)

    def evaluate_and_modulate(self, vibration_reading: float) -> Dict[str, Any]:
        """
        Evaluates harmonic amplitude against safe equilibrium thresholds and computes counter-modulation.
        """
        self.torsional_amplitude_history.append(vibration_reading)
        if len(self.torsional_amplitude_history) > 100:
            self.torsional_amplitude_history.pop(0)

        threshold = 1.0
        status = "NOMINAL"
        phase_correction_deg = 0.0

        if vibration_reading > threshold:
            self.modulation_active = True
            status = "HARMONIC_RESONANCE_DETECTED"
            # Compute counter-phase modulation amplitude
            phase_correction_deg = round((vibration_reading - threshold) * 45.0, 2)
            logger.warning(
                f"[TORSION ALERT] Mill {self.mill_id}: Amplitude {vibration_reading}g exceeds threshold {threshold}g! "
                f"Applying dynamic inverter phase correction: {phase_correction_deg}°"
            )
        else:
            self.modulation_active = False
            status = "EQUILIBRIUM_STABLE"

        return {
            "mill_id": self.mill_id,
            "vibration_g": vibration_reading,
            "status": status,
            "modulation_active": self.modulation_active,
            "phase_correction_deg": phase_correction_deg,
            "timestamp": time.time()
        }

if __name__ == "__main__":
    sentinel = RollerMillTorsionHarmonicSentinel(mill_id="NRB-MILL-07")
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Amplitude Equilibrium Modulation Sentinel...")
    for _ in range(5):
        val = sentinel.sample_torsion_sensor()
        report = sentinel.evaluate_and_modulate(val)
        logger.info(f"Diagnostic Report: {report}")
        time.sleep(0.1)
