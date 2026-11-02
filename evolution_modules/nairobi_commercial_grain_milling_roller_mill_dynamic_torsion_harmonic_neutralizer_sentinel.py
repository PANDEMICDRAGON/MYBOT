import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("TorsionHarmonicNeutralizer")

class RollerMillTorsionNeutralizerEngine:
    """
    Monitors torsional harmonic frequencies on commercial roller mill drive shafts
    and computes real-time counter-torque phase shifts to neutralize damaging resonances.
    """
    def __init__(self, mill_id: str, base_rpm: float = 1200.0):
        self.mill_id = mill_id
        self.base_rpm = base_rpm
        self.active_neutralization_engaged = False
        self.harmonic_history: List[float] = []
        logger.info(f"Initialized Torsion Harmonic Neutralizer for Mill {self.mill_id} at {self.base_rpm} RPM")

    def sample_torsion_frequency(self) -> float:
        """Simulates telemetry reading of torsional harmonic frequency in Hz."""
        # Base rotational frequency + harmonic jitter
        base_freq = self.base_rpm / 60.0
        jitter = random.uniform(-2.5, 3.2)
        # Introduce occasional resonant spikes to test dampening
        resonance_spike = 15.0 if random.random() < 0.1 else 0.0
        return max(5.0, base_freq + jitter + resonance_spike)

    def calculate_counter_phase_torque(self, freq: float) -> Dict[str, Any]:
        """Calculates required phase shift and counter-torque magnitude."""
        target_freq = self.base_rpm / 60.0
        deviation = freq - target_freq
        
        if abs(deviation) > 4.0:
            self.active_neutralization_engaged = True
            # Phase angle calculation in radians (180 deg out of phase for cancellation)
            phase_shift = (math.pi + (deviation * 0.1)) % (2 * math.pi)
            counter_torque_nm = min(500.0, abs(deviation) * 35.5)
        else:
            self.active_neutralization_engaged = False
            phase_shift = 0.0
            counter_torque_nm = 0.0

        return {
            "frequency_hz": round(freq, 3),
            "deviation_hz": round(deviation, 3),
            "neutralization_engaged": self.active_neutralization_engaged,
            "phase_shift_radians": round(phase_shift, 4),
            "counter_torque_nm": round(counter_torque_nm, 2)
        }

    def run_diagnostic_cycle(self, iterations: int = 5) -> List[Dict[str, Any]]:
        results = []
        for i in range(iterations):
            freq = self.sample_torsion_frequency()
            action = self.calculate_counter_phase_torque(freq)
            self.harmonic_history.append(freq)
            results.append(action)
            logger.info(f"Cycle {i+1}: {action}")
            time.sleep(0.05)
        return results

if __name__ == "__main__":
    print("Executing Roller Mill Dynamic Torsion Harmonic Neutralizer Sentinel...")
    engine = RollerMillTorsionNeutralizerEngine(mill_id="NRB-MILL-09")
    diagnostic_report = engine.run_diagnostic_cycle(iterations=5)
    print(f"Diagnostic Report Complete: {len(diagnostic_report)} cycles recorded.")
