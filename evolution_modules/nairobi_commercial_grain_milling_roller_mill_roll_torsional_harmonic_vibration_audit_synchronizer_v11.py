"""
Nairobi Commercial Grain Milling Roller Mill Roll Torsional Harmonic Vibration Audit Synchronizer v11
Designed to protect grain milling machinery infrastructure in Nairobi, Kenya.
"""

import time
import math
import random
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("TorsionalHarmonicVibrationSynchronizerV11")

class TorsionalHarmonicVibrationSynchronizerV11:
    """
    Monitors torsional harmonic vibrations across roller mill shafts, computing resonance indices
    and emitting real-time telemetry to prevent mechanical fatigue and shaft shear.
    """
    def __init__(self, mill_id: str, baseline_rpm: float = 1200.0):
        self.mill_id = mill_id
        self.baseline_rpm = baseline_rpm
        self.audit_history: List[Dict[str, Any]] = []

    def audit_cycle(self, raw_vibration_spectrum: List[float]) -> Dict[str, Any]:
        """
        Perform a single audit cycle over the provided vibration spectrum.
        """
        if not raw_vibration_spectrum:
            return {"status": "error", "message": "Empty spectrum"}

        peak_amplitude = max(raw_vibration_spectrum)
        rms_amplitude = math.sqrt(sum(v ** 2 for v in raw_vibration_spectrum) / len(raw_vibration_spectrum))
        harmonic_distortion_index = peak_amplitude / (rms_amplitude if rms_amplitude > 0 else 1e-6)
        
        # Torsional stress estimation
        torsional_stress_mpa = rms_amplitude * 14.5 + (random.uniform(0.1, 0.5))
        status = "OPTIMAL"
        if torsional_stress_mpa > 75.0:
            status = "CRITICAL_RESONANCE_WARNING"
        elif torsional_stress_mpa > 50.0:
            status = "ELEVated_FATIGUE_RISK"

        audit_result = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "peak_amplitude": peak_amplitude,
            "rms_amplitude": rms_amplitude,
            "harmonic_distortion_index": harmonic_distortion_index,
            "torsional_stress_mpa": torsional_stress_mpa,
            "status": status
        }

        self.audit_history.append(audit_result)
        logger.info(f"Mill {self.mill_id} Audit: Torsional Stress={torsional_stress_mpa:.2f} MPa | Status={status}")
        return audit_result

if __name__ == "__main__":
    logger.info("Initializing TorsionalHarmonicVibrationSynchronizerV11 Test Harness...")
    synchronizer = TorsionalHarmonicVibrationSynchronizerV11(mill_id="NAI-MILL-04")
    mock_spectrum = [random.uniform(0.5, 3.8) for _ in range(64)]
    result = synchronizer.audit_cycle(mock_spectrum)
    print("Test Audit Result:", result)
