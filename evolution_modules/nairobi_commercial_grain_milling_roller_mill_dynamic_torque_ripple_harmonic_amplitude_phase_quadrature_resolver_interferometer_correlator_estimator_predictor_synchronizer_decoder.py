"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Decoder Module."""

import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueDecoder")

class RollerMillTorqueRippleDecoder:
    """Decodes and correlates torque ripple harmonics using quadrature resolver interferometry."""

    def __init__(self, sample_rate_hz: float = 1000.0):
        self.sample_rate_hz = sample_rate_hz
        self.harmonic_orders = [1, 2, 3, 6, 12]

    def decode_quadrature_signals(self, sin_wave: List[float], cos_wave: List[float]) -> Dict[str, Any]:
        """Extracts instantaneous phase, amplitude, and quadrature error."""
        if len(sin_wave) != len(cos_wave) or not sin_wave:
            raise ValueError("Sin and cos wave inputs must be of equal non-zero length.")
        
        amplitudes = []
        phases = []
        quadrature_errors = []

        for s, c in zip(sin_wave, cos_wave):
            amp = math.sqrt(s**2 + c**2)
            phase = math.atan2(s, c)
            # Ideal orthogonal error is 0 when amp is stable and s^2 + c^2 = 1 (normalized)
            err = abs(1.0 - amp)
            amplitudes.append(amp)
            phases.append(phase)
            quadrature_errors.append(err)

        mean_amplitude = sum(amplitudes) / len(amplitudes)
        mean_phase = sum(phases) / len(phases)
        max_error = max(quadrature_errors)

        logger.info(f"Decoded quadrature resolver: Mean Amp={mean_amplitude:.4f}, Mean Phase={mean_phase:.4f} rad, Max Err={max_error:.4f}")

        return {
            "mean_amplitude": mean_amplitude,
            "mean_phase_rad": mean_phase,
            "max_quadrature_error": max_error,
            "status": "STABLE" if max_error < 0.15 else "DEGRADED"
        }

    def estimate_torque_harmonics(self, torque_stream: List[float]) -> Dict[str, float]:
        """Estimates harmonic amplitudes from torque ripple data."""
        n = len(torque_stream)
        if n == 0:
            return {}
        
        mean_torque = sum(torque_stream) / n
        results = {"mean_torque_nm": mean_torque}

        # Simple discrete harmonic energy estimation
        for order in self.harmonic_orders:
            harm_sum = sum(
                t * math.cos(2.0 * math.pi * order * i / n)
                for i, t in enumerate(torque_stream)
            )
            results[f"harmonic_{order}_amplitude"] = abs(harm_sum) / (n / 2.0)

        return results

    def predict_mechanical_failure(self, telemetry: Dict[str, Any]) -> bool:
        """Predicts imminent mechanical failure based on quadrature and harmonic anomaly."""
        max_err = telemetry.get("max_quadrature_error", 0.0)
        h3 = telemetry.get("harmonic_3_amplitude", 0.0)
        
        if max_err > 0.2 or h3 > 50.0:
            logger.warning("CRITICAL: Roller mill mechanical anomaly detected. Preventive maintenance recommended.")
            return True
        return False

if __name__ == "__main__":
    decoder = RollerMillTorqueRippleDecoder()
    # Generate dummy sine/cosine resolver waveforms
    t_pts = [i * 0.01 for i in range(100)]
    s_wave = [math.sin(2 * math.pi * 50 * t) for t in t_pts]
    c_wave = [math.cos(2 * math.pi * 50 * t) for t in t_pts]
    torque_data = [150.0 + 10.0 * math.sin(2 * math.pi * 50 * t) + 5.0 * math.cos(2 * math.pi * 150 * t) for t in t_pts]

    quad_res = decoder.decode_quadrature_signals(s_wave, c_wave)
    harm_res = decoder.estimate_torque_harmonics(torque_data)
    combined = {**quad_res, **harm_res}
    failure_predicted = decoder.predict_mechanical_failure(combined)
    logger.info(f"Test execution completed successfully. Failure predicted: {failure_predicted}")
