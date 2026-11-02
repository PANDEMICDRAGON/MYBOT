"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Equilibrium Modulator Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import random
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorsionModulatorSentinel")

class RollerMillTorsionHarmonicEquilibriumModulator:
    """
    Monitors torsional stress and harmonic vibration across commercial roller mill pairs
    and applies real-time dynamic modulation signals to preserve drive train integrity.
    """
    def __init__(self, mill_id: str, fast_roll_rpm: float = 550.0, slow_roll_rpm: float = 220.0):
        self.mill_id = mill_id
        self.fast_roll_rpm = fast_roll_rpm
        self.slow_roll_rpm = slow_roll_rpm
        self.differential = fast_roll_rpm / slow_roll_rpm if slow_roll_rpm > 0 else 2.5
        self.torsion_history: List[float] = []
        self.modulation_factor = 1.0
        self.status = "INITIALIZED"

    def sample_torsion_telemetry(self) -> Dict[str, Any]:
        """Simulates high-frequency telemetry from dual roller shafts."""
        base_torsion = 45.0 + (self.fast_roll_rpm * 0.01)
        noise = random.gauss(0, 3.5)
        harmonic_spike = 12.0 * math.sin(time.time() * 3.14159) if random.random() < 0.2 else 0.0
        current_torsion = max(5.0, base_torsion + noise + harmonic_spike)
        
        self.torsion_history.append(current_torsion)
        if len(self.torsion_history) > 100:
            self.torsion_history.pop(0)

        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "torsion_nm": round(current_torsion, 2),
            "fast_roll_rpm": self.fast_roll_rpm,
            "slow_roll_rpm": self.slow_roll_rpm,
            "differential": self.differential
        }

    def compute_harmonic_equilibrium(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates required counter-modulation to damp torsional oscillations."""
        torsion = telemetry["torsion_nm"]
        mean_torsion = sum(self.torsion_history) / len(self.torsion_history)
        deviation = torsion - mean_torsion

        if abs(deviation) > 8.0:
            self.status = "MODULATING_HARMONIC_EQUILIBRIUM"
            self.modulation_factor = max(0.85, min(1.15, 1.0 - (deviation * 0.005)))
        else:
            self.status = "STEADY_STATE_OPTIMIZED"
            self.modulation_factor = 1.0

        return {
            "mill_id": self.mill_id,
            "status": self.status,
            "mean_torsion_nm": round(mean_torsion, 2),
            "deviation_nm": round(deviation, 2),
            "modulation_factor": round(self.modulation_factor, 4)
        }

    def execute_safeguard_cycle(self) -> Dict[str, Any]:
        telemetry = self.sample_torsion_telemetry()
        modulation = self.compute_harmonic_equilibrium(telemetry)
        logger.info(f"[{self.mill_id}] Torsion: {telemetry['torsion_nm']} Nm | Status: {modulation['status']} | ModFactor: {modulation['modulation_factor']}")
        return {**telemetry, **modulation}

if __name__ == "__main__":
    sentinel = RollerMillTorsionHarmonicEquilibriumModulator("NAIROBI_MAIZE_MILL_04")
    for _ in range(5):
        result = sentinel.execute_safeguard_cycle()
        time.sleep(0.2)
