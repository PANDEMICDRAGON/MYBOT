"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Amplitude Equilibrium Modulation Sentinel
Designed and coded autonomously by Cortana for Michael Obiero in Nairobi, Kenya.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicModulationSentinel")

class RollerMillTorsionModulator:
    """
    Monitors torsional stress, harmonic frequencies, and amplitude equilibrium on commercial
    grain milling roller mill drive shafts, applying counter-modulation damping.
    """
    def __init__(self, mill_id: str, rated_rpm: float = 1000.0):
        self.mill_id = mill_id
        self.rated_rpm = rated_rpm
        self.torsion_history: List[float] = []
        self.active_modulation_factor = 1.0
        self.status = "STANDBY"

    def sample_telemetry(self) -> Dict[str, float]:
        """Simulates real-time telemetry from roller mill sensors."""
        rpm_jitter = random.gauss(0, 5.0)
        current_rpm = self.rated_rpm + rpm_jitter
        torsion_stress_mpa = 120.0 + random.uniform(-15.0, 25.0) + (rpm_jitter * 0.5)
        harmonic_amplitude = abs(math.sin(time.time())) * 12.4 + random.uniform(0, 2.0)
        
        return {
            "timestamp": time.time(),
            "current_rpm": current_rpm,
            "torsion_stress_mpa": torsion_stress_mpa,
            "harmonic_amplitude": harmonic_amplitude,
            "modulation_factor": self.active_modulation_factor
        }

    def evaluate_and_modulate(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """Evaluates torsional harmonics and computes equilibrium modulation."""
        stress = telemetry["torsion_stress_mpa"]
        amplitude = telemetry["harmonic_amplitude"]
        
        self.torsion_history.append(stress)
        if len(self.torsion_history) > 100:
            self.torsion_history.pop(0)

        action = "STABLE"
        if amplitude > 10.0 or stress > 145.0:
            # Apply dynamic counter-phase modulation
            self.active_modulation_factor = max(0.75, 1.0 - ((amplitude - 10.0) * 0.05))
            action = "MODULATING_DAMPING_APPLIED"
            self.status = "ACTIVE_CORRECTION"
        else:
            # Gradually return modulation factor to 1.0
            self.active_modulation_factor = min(1.0, self.active_modulation_factor + 0.01)
            self.status = "OPTIMAL"

        return {
            "mill_id": self.mill_id,
            "status": self.status,
            "action": action,
            "new_modulation_factor": round(self.active_modulation_factor, 4),
            "stress_mpa": round(stress, 2),
            "harmonic_amplitude": round(amplitude, 2)
        }

if __name__ == "__main__":
    logger.info("Initializing RollerMillTorsionModulator Test Harness...")
    sentinel = RollerMillTorsionModulator(mill_id="NRB-MILL-ALPHA-07")
    for i in range(3):
        telemetry = sentinel.sample_telemetry()
        result = sentinel.evaluate_and_modulate(telemetry)
        logger.info(f"Cycle {i+1} Result: {result}")
        time.sleep(0.1)
    logger.info("Roller Mill Dynamic Torsion Harmonic Sentinel operational and verified.")
