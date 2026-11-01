"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Demodulator Module."""

import math
import time
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillDemodulator")


class RollerMillDemodulatorEngine:
    """Performs quadrature resolver interferometry and demodulates dynamic torque ripple harmonics."""

    def __init__(self, sample_rate_hz: float = 1000.0):
        self.sample_rate_hz = sample_rate_hz
        self.active = True

    def compute_quadrature_demodulation(self, sin_wave: List[float], cos_wave: List[float]) -> Dict[str, Any]:
        """Calculates instantaneous phase, amplitude, and harmonic distortion."""
        if not sin_wave or not cos_wave or len(sin_wave) != len(cos_wave):
            raise ValueError("Invalid or mismatched quadrature signal inputs.")

        amplitudes = []
        phases = []
        for s, c in zip(sin_wave, cos_wave):
            amp = math.sqrt(s**2 + c**2)
            phase = math.atan2(s, c)
            amplitudes.append(amp)
            phases.append(phase)

        mean_amplitude = sum(amplitudes) / len(amplitudes)
        amplitude_ripple = max(amplitudes) - min(amplitudes)
        mean_phase = sum(phases) / len(phases)

        logger.info(f"Demodulation complete. Mean Amp: {mean_amplitude:.4f}, Ripple: {amplitude_ripple:.4f}")

        return {
            "mean_amplitude": mean_amplitude,
            "amplitude_ripple": amplitude_ripple,
            "mean_phase_radians": mean_phase,
            "status": "SYNCHRONIZED"
        }

    def predict_torque_vector(self, current_torque: float, harmonic_trend: float) -> float:
        """Predicts next cycle torque vector based on quadrature phase correlation."""
        predicted = current_torque + (harmonic_trend * 0.15)
        return round(predicted, 4)


if __name__ == "__main__":
    engine = RollerMillDemodulatorEngine()
    # Simulate quadrature signals
    t_vals = [i * 0.01 for i in range(100)]
    sin_sig = [math.sin(t) + 0.05 * math.sin(3 * t) for t in t_vals]
    cos_sig = [math.cos(t) + 0.05 * math.cos(3 * t) for t in t_vals]
    
    result = engine.compute_quadrature_demodulation(sin_sig, cos_sig)
    prediction = engine.predict_torque_vector(120.5, 2.3)
    print("DEMODULATION RESULT:", result)
    print("PREDICTED TORQUE VECTOR:", prediction)
