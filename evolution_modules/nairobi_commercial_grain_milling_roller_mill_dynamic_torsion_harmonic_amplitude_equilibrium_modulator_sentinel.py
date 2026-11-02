"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Amplitude Equilibrium Modulator Sentinel."""

import ast
import logging
import random
import time
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillHarmonicModulator")

class RollerMillHarmonicModulator:
    """Monitors and modulates dynamic torsion harmonic amplitude equilibrium for industrial roller mills."""

    def __init__(self, mill_id: str, baseline_frequency_hz: float = 50.0):
        self.mill_id = mill_id
        self.baseline_frequency = baseline_frequency_hz
        self.resonance_history: List[float] = []
        self.modulation_factor: float = 1.0
        self.active_status: bool = True
        logger.info(f"Initialized RollerMillHarmonicModulator for mill: {self.mill_id} at {baseline_frequency_hz}Hz")

    def ingest_telemetry(self, vibration_amplitude: float, torsion_stress_mpa: float) -> Dict[str, Any]:
        """Ingests live telemetry and computes necessary harmonic modulation offsets."""
        if not self.active_status:
            return {"status": "inactive"}

        self.resonance_history.append(vibration_amplitude)
        if len(self.resonance_history) > 100:
            self.resonance_history.pop(0)

        mean_amplitude = sum(self.resonance_history) / len(self.resonance_history)
        
        # Compute dynamic damping offset
        if vibration_amplitude > (mean_amplitude * 1.35):
            self.modulation_factor = max(0.5, self.modulation_factor - 0.05)
            adjustment_action = "DAMPEN_AMPLITUDE"
        elif vibration_amplitude < (mean_amplitude * 0.75):
            self.modulation_factor = min(1.5, self.modulation_factor + 0.02)
            adjustment_action = "BOOST_TORQUE"
        else:
            adjustment_action = "EQUILIBRIUM_MAINTAINED"

        return {
            "mill_id": self.mill_id,
            "vibration_amplitude": vibration_amplitude,
            "torsion_stress_mpa": torsion_stress_mpa,
            "mean_amplitude": mean_amplitude,
            "modulation_factor": self.modulation_factor,
            "action": adjustment_action,
            "timestamp": time.time()
        }

    def emergency_lockdown(self) -> bool:
        """Executes emergency damping lockdown in case of catastrophic torsional resonance."""
        self.modulation_factor = 0.0
        self.active_status = False
        logger.warning(f"EMERGENCY LOCKDOWN executed for roller mill {self.mill_id}.")
        return True


def __main__() -> None:
    modulator = RollerMillHarmonicModulator("NBI-MILL-07")
    for i in range(5):
        vib = random.uniform(1.2, 3.8)
        stress = random.uniform(45.0, 85.0)
        telemetry = modulator.ingest_telemetry(vib, stress)
        logger.info(f"Telemetry iteration {i+1}: {telemetry}")
        time.sleep(0.01)
    
    modulator.emergency_lockdown()


if __name__ == "__main__":
    __main__()
