"""Nairobi Commercial Grain Milling Roller Mill Drive Motor Harmonic Vibration Synaptic Neural Pulse Harmonic Resonance Synchronizer."""

import logging
import time
import math
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicResonanceSynchronizer")

class RollerMillHarmonicResonanceSynchronizer:
    """
    Monitors and synchronizes drive motor harmonic vibrations in commercial grain milling facilities in Nairobi.
    """
    def __init__(self, motor_id: str, base_frequency_hz: float = 50.0):
        self.motor_id = motor_id
        self.base_frequency_hz = base_frequency_hz
        self.synaptic_pulse_state = 1.0
        self.resonance_history: List[float] = []

    def analyze_vibration(self, vibration_spectrum: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyzes incoming vibration frequency magnitudes and computes resonance adjustments.
        """
        peak_freq = vibration_spectrum.get('peak_frequency', self.base_frequency_hz)
        amplitude = vibration_spectrum.get('amplitude_mm_s', 0.1)
        
        # Compute harmonic deviation from baseline grid frequency (50Hz in Kenya)
        deviation = abs(peak_freq - self.base_frequency_hz)
        resonance_risk = amplitude * (1.0 + (deviation / self.base_frequency_hz))
        
        self.resonance_history.append(resonance_risk)
        if len(self.resonance_history) > 100:
            self.resonance_history.pop(0)
            
        # Synaptic neural dampening adjustment
        adjustment_factor = 1.0
        if resonance_risk > 0.75:
            adjustment_factor = max(0.85, 1.0 - (resonance_risk * 0.1))
            logger.warning(f"[HARMONIC ALERT] Motor {self.motor_id}: High resonance detected ({resonance_risk:.3f}). Applying synaptic dampening factor: {adjustment_factor:.3f}")
        else:
            logger.info(f"[STABLE] Motor {self.motor_id}: Vibration spectrum nominal. Resonance index: {resonance_risk:.3f}")
            
        return {
            "motor_id": self.motor_id,
            "resonance_risk": resonance_risk,
            "adjustment_factor": adjustment_factor,
            "timestamp": time.time()
        }

if __name__ == "__main__":
    synchronizer = RollerMillHarmonicResonanceSynchronizer("MILL_DRIVE_MOTOR_ALPHA_01")
    sample_spectrum = {"peak_frequency": 52.3, "amplitude_mm_s": 0.82}
    result = synchronizer.analyze_vibration(sample_spectrum)
    print(f"Execution test result: {result}")
