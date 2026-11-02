"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Compensation Sentinel."""

import time
import math
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorsionCompensationSentinel")


class RollerMillTorsionCompensationSentinel:
    """Monitors and compensates for dynamic torsion harmonics in roller mill drives."""

    def __init__(self, mill_id: str, rated_rpm: float = 1200.0):
        self.mill_id = mill_id
        self.rated_rpm = rated_rpm
        self.active_compensation = True
        logger.info(f"Initialized Torsion Harmonic Compensation Sentinel for Mill {mill_id} at {rated_rpm} RPM.")

    def analyze_torsion_waveform(self, vibration_samples: List[float]) -> Dict[str, Any]:
        """Analyze raw vibration or torque waveform samples to detect harmonic spikes."""
        if not vibration_samples:
            return {"status": "idle", "harmonic_index": 0.0, "compensation_applied": False}

        mean_val = sum(vibration_samples) / len(vibration_samples)
        variance = sum((x - mean_val) ** 2 for x in vibration_samples) / len(vibration_samples)
        std_dev = math.sqrt(variance)

        # Simulated harmonic index calculation
        harmonic_index = std_dev / (abs(mean_val) + 1e-6)
        compensation_applied = False

        if harmonic_index > 0.15 and self.active_compensation:
            logger.warning(f"[{self.mill_id}] High torsional harmonic index detected: {harmonic_index:.4f}. Applying counter-torque pulse.")
            compensation_applied = True

        return {
            "mill_id": self.mill_id,
            "sample_count": len(vibration_samples),
            "mean_vibration": mean_val,
            "harmonic_index": harmonic_index,
            "compensation_applied": compensation_applied,
            "timestamp": time.time()
        }


if __name__ == "__main__":
    sentinel = RollerMillTorsionCompensationSentinel(mill_id="NAI-MILL-0708")
    mock_waveform = [1.2, 1.5, 0.8, 2.1, 1.0, 1.9, 2.4, 0.5]
    result = sentinel.analyze_torsion_waveform(mock_waveform)
    print("Sentinel Analysis Result:", result)
