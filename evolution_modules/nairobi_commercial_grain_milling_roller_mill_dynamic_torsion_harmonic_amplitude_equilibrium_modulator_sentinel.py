"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Amplitude Equilibrium Modulator Sentinel.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import logging
import random
import time
import ast
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [TORSION_MODULATOR] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class RollerMillTorsionEquilibriumModulator:
    """Monitors shaft torsion harmonics and modulates drive damping in commercial roller mills."""

    def __init__(self, mill_id: str, nominal_rpm: float = 1200.0) -> None:
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.torsion_history: List[float] = []
        self.damping_coefficient = 1.0
        logger.info(f"Initialized RollerMillTorsionEquilibriumModulator for {{self.mill_id}} at {{self.nominal_rpm}} RPM.")

    def sample_torsion_amplitude(self) -> float:
        """Simulates telemetry extraction for shaft torsional vibration amplitude."""
        # Base noise + occasional harmonic spikes
        noise = random.gauss(0.0, 0.2)
        spike = random.choice([0.0, 0.0, 0.0, 1.5, 3.2])
        amplitude = max(0.1, 1.0 + abs(noise) + spike)
        self.torsion_history.append(amplitude)
        if len(self.torsion_history) > 100:
            self.torsion_history.pop(0)
        return amplitude

    def compute_equilibrium(self, current_amplitude: float) -> Dict[str, Any]:
        """Calculates harmonic equilibrium status and adjusts damping coefficient."""
        mean_amp = sum(self.torsion_history) / len(self.torsion_history)
        
        status = "OPTIMAL"
        adjustment = 0.0

        if current_amplitude > 2.5:
            status = "CRITICAL_HARMONIC_RESONANCE"
            adjustment = -0.15
            self.damping_coefficient = max(0.5, self.damping_coefficient + adjustment)
        elif current_amplitude > 1.8:
            status = "ELEVATED_TORSION"
            adjustment = -0.05
            self.damping_coefficient = max(0.7, self.damping_coefficient + adjustment)
        else:
            status = "EQUILIBRIUM"
            adjustment = 0.02
            self.damping_coefficient = min(1.5, self.damping_coefficient + adjustment)

        return {
            "mill_id": self.mill_id,
            "current_amplitude": round(current_amplitude, 3),
            "mean_amplitude": round(mean_amp, 3),
            "damping_coefficient": round(self.damping_coefficient, 3),
            "status": status
        }

    def execute_stabilization_cycle(self) -> Dict[str, Any]:
        """Executes a single sampling and modulation cycle."""
        amp = self.sample_torsion_amplitude()
        telemetry = self.compute_equilibrium(amp)
        logger.info(f"Telemetry: {{telemetry}}")
        return telemetry

if __name__ == "__main__":
    modulator = RollerMillTorsionEquilibriumModulator(mill_id="MILL-NAI-01")
    for _ in range(5):
        modulator.execute_stabilization_cycle()
        time.sleep(0.1)

    # Validate source code AST compile
    source_code = open(__file__, "r", encoding="utf-8").read()
    ast.parse(source_code)
    logger.info("AST compilation check passed successfully for Torsion Equilibrium Modulator.")
