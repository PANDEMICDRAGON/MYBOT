"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Modulator

Provides real-time quadrature phase correlation, harmonic amplitude estimation, and torque ripple mitigation for high-speed roller mill spindles.
"""

import math
import time
import logging
from typing import Dict, List, Any, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillModulator")

class RollerMillModulator:
    def __init__(self, spindle_id: str, baseline_freq_hz: float = 50.0):
        self.spindle_id = spindle_id
        self.baseline_freq_hz = baseline_freq_hz
        self.phase_quadrature_offset = 0.0
        self.harmonic_amplitude = 1.0
        self.torque_ripple_compensation = 0.0
        logger.info(f"Initialized RollerMillModulator for spindle {spindle_id} at {baseline_freq_hz}Hz")

    def measure_resolver_signals(self, raw_sine: float, raw_cosine: float) -> Tuple[float, float]:
        """Correlates sine and cosine resolver signals to extract instantaneous phase angle."""
        amplitude = math.sqrt(raw_sine**2 + raw_cosine**2)
        if amplitude == 0:
            return 0.0, 0.0
        normalized_sine = raw_sine / amplitude
        normalized_cosine = raw_cosine / amplitude
        phase_angle = math.atan2(normalized_sine, normalized_cosine)
        return phase_angle, amplitude

    def estimate_torque_harmonics(self, phase_history: List[float]) -> float:
        """Estimates harmonic amplitude and phase quadrature from recent phase angle telemetry."""
        if len(phase_history) < 3:
            return 0.0
        
        # Compute numerical derivative (angular velocity fluctuation / ripple)
        deltas = [phase_history[i] - phase_history[i-1] for i in range(1, len(phase_history))]
        mean_delta = sum(deltas) / len(deltas)
        variance = sum((d - mean_delta)**2 for d in deltas) / len(deltas)
        self.harmonic_amplitude = math.sqrt(variance) * self.baseline_freq_hz
        return self.harmonic_amplitude

    def modulate_synchronization(self, torque_ripple: float) -> Dict[str, Any]:
        """Computes adaptive correction vector to suppress torque ripple harmonics."""
        self.torque_ripple_compensation = -0.75 * torque_ripple
        correction_signal = {
            "spindle_id": self.spindle_id,
            "timestamp": time.time(),
            "torque_ripple_detected": torque_ripple,
            "harmonic_amplitude": self.harmonic_amplitude,
            "compensation_output": self.torque_ripple_compensation,
            "status": "SYNCHRONIZED_AND_MODULATED"
        }
        return correction_signal

if __name__ == "__main__":
    modulator = RollerMillModulator("MILL-SPINDLE-04X")
    
    # Simulate resolver telemetry stream
    history = []
    for i in range(10):
        t = i * 0.01
        sine = math.sin(2 * math.pi * 50.0 * t + 0.1 * math.sin(2 * math.pi * 5.0 * t))
        cosine = math.cos(2 * math.pi * 50.0 * t + 0.1 * math.sin(2 * math.pi * 5.0 * t))
        phase, amp = modulator.measure_resolver_signals(sine, cosine)
        history.append(phase)
        ripple = modulator.estimate_torque_harmonics(history)
        payload = modulator.modulate_synchronization(ripple)
        logger.info(f"Simulation Step {i}: {payload}")
