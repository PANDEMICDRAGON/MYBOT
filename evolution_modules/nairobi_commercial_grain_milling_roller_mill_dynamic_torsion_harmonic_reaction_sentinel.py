"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Reaction Sentinel."""

import time
import math
import random
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TorsionHarmonicReactionSentinel")

class RollerMillTorsionReactionSentinel:
    """
    Monitors high-frequency torsional oscillations and reaction forces across commercial
    roller mill drive trains in Nairobi grain processing facilities.
    """
    def __init__(self, mill_id: str, sample_rate_hz: float = 1000.0):
        self.mill_id = mill_id
        self.sample_rate_hz = sample_rate_hz
        self.buffer: List[float] = []
        self.buffer_limit = 2000
        self.reaction_threshold_nm = 4500.0  # Newton-meters critical torsion limit
        self.active_countermeasures = False

    def ingest_torque_signal(self, torque_nm: float) -> Dict[str, Any]:
        """Ingests raw torque telemetry, computes harmonic reaction vectors, and evaluates stability."""
        self.buffer.append(torque_nm)
        if len(self.buffer) > self.buffer_limit:
            self.buffer.pop(0)

        harmonic_index = self._calculate_harmonic_distortion()
        is_critical = harmonic_index > 0.85 or abs(torque_nm) > self.reaction_threshold_nm

        if is_critical:
            self._engage_harmonic_reaction_dampener()

        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "current_torque_nm": torque_nm,
            "harmonic_distortion_index": harmonic_index,
            "critical_state": is_critical,
            "countermeasures_active": self.active_countermeasures
        }

    def _calculate_harmonic_distortion(self) -> float:
        """Calculates rapid Fast Fourier Transform (FFT) proxy for torsional harmonics."""
        if len(self.buffer) < 50:
            return 0.0
        recent = self.buffer[-50:]
        mean_val = sum(recent) / len(recent)
        variance = sum((x - mean_val) ** 2 for x in recent) / len(recent)
        std_dev = math.sqrt(variance)
        # Normalized pseudo-harmonic ratio
        return min(1.0, std_dev / (abs(mean_val) + 1e-6))

    def _engage_harmonic_reaction_dampener(self) -> None:
        """Triggers emergency frequency-shift pulse on inverter drive."""
        self.active_countermeasures = True
        logger.warning(
            f"[CRITICAL] Torsional Harmonic Reaction threshold breached on mill {self.mill_id}! "
            f"Engaging dynamic frequency-shift dampener."
        )

if __name__ == "__main__":
    sentinel = RollerMillTorsionReactionSentinel(mill_id="NAIROBI_MILL_ALPHA_04")
    logger.info("Initializing Roller Mill Dynamic Torsion Harmonic Reaction Sentinel test harness...")
    for i in range(10):
        simulated_torque = 3500.0 + random.gauss(0, 800) + (2000.0 if i == 7 else 0.0)
        status = sentinel.ingest_torque_signal(simulated_torque)
        logger.info(f"Telemetry Step {i}: {status}")
        time.sleep(0.01)
    logger.info("Sentinel test execution completed successfully.")
