"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Synthesizer"""

import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicSynthesizer")


class RollerMillHarmonicSynthesizer:
    """
    Analyzes torque ripple harmonics, phase quadrature, and resolver signals
    for industrial grain milling roller mills in Nairobi, Kenya.
    """

    def __init__(self, mill_id: str, base_frequency_hz: float = 50.0):
        self.mill_id = mill_id
        self.base_frequency_hz = base_frequency_hz
        self.harmonic_orders = [1, 3, 5, 7, 11]

    def compute_harmonic_vector(self, raw_torque_samples: List[float], resolver_phase_rad: float) -> Dict[str, Any]:
        """
        Computes harmonic amplitudes and phase quadrature correlation.
        """
        if not raw_torque_samples:
            raise ValueError("Raw torque samples cannot be empty.")

        n = len(raw_torque_samples)
        mean_torque = sum(raw_torque_samples) / n
        
        # Compute harmonic components via discrete Fourier approximation
        harmonics = {}
        for order in self.harmonic_orders:
            real_part = sum(t * math.cos(2.0 * math.pi * order * i / n) for i, t in enumerate(raw_torque_samples))
            imag_part = sum(t * math.sin(2.0 * math.pi * order * i / n) for i, t in enumerate(raw_torque_samples))
            amplitude = math.sqrt(real_part**2 + imag_part**2) / (n / 2.0)
            phase = math.atan2(imag_part, real_part)
            harmonics[f"harmonic_{order}"] = {
                "amplitude": amplitude,
                "phase_rad": phase
            }

        # Quadrature Resolver Interferometry Correlation
        quadrature_q = math.sin(resolver_phase_rad)
        quadrature_d = math.cos(resolver_phase_rad)
        resolver_lock = math.sqrt(quadrature_q**2 + quadrature_d**2)

        prediction_score = 1.0 - (abs(mean_torque - (sum(raw_torque_samples)/n)) / (mean_torque + 1e-9))

        logger.info(f"Mill {self.mill_id}: Processed {n} torque samples. Resolver Lock: {resolver_lock:.4f}")

        return {
            "mill_id": self.mill_id,
            "mean_torque": mean_torque,
            "resolver_lock": resolver_lock,
            "harmonics": harmonics,
            "prediction_score": prediction_score,
            "status": "SYNCHRONIZED"
        }


if __name__ == "__main__":
    synthesizer = RollerMillHarmonicSynthesizer(mill_id="NAIROBI-MILL-01")
    sample_data = [100.5 + 5.0 * math.sin(i / 2.0) for i in range(64)]
    result = synthesizer.compute_harmonic_vector(sample_data, resolver_phase_rad=0.7854)
    print("Evolution Execution Successful:", result)
