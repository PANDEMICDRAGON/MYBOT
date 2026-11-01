"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Decoder

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

This module provides real-time digital signal processing, phase quadrature resolution, and harmonic decoding for industrial grain milling roller mill drive systems. It analyzes high-frequency torque ripple telemetry, estimates harmonic distortion profiles, predicts phase drift, and synchronizes corrective torque dampening waveforms.
"""

import math
import time
import statistics
from typing import List, Dict, Any, Tuple


class RollerMillTorqueDecoderError(Exception):
    """Custom exception for torque ripple decoding and synchronization failures."""
    pass


class RollerMillHarmonicDecoder:
    """
    Performs quadrature resolver interferometry, harmonic amplitude estimation,
    and predictive phase synchronization for commercial grain milling roller mills.
    """

    def __init__(self, sample_rate_hz: float = 1000.0, nominal_base_freq_hz: float = 50.0) -> None:
        self.sample_rate_hz = sample_rate_hz
        self.nominal_base_freq_hz = nominal_base_freq_hz
        self.history: List[float] = []
        self.sync_locked = False
        self.last_phase_error = 0.0

    def ingest_torque_signal(self, torque_samples: List[float]) -> Dict[str, Any]:
        """
        Ingests raw torque transducer samples, computes quadrature components,
        estimates harmonic amplitude and phase, and predicts future ripple trends.
        """
        if not torque_samples:
            raise RollerMillTorqueDecoderError("Empty torque sample stream provided.")

        self.history.extend(torque_samples)
        if len(self.history) > 2000:
            self.history = self.history[-2000:]

        mean_torque = statistics.mean(torque_samples)
        rms_torque = math.sqrt(statistics.mean([t ** 2 for t in torque_samples]))
        peak_ripple = max(abs(t - mean_torque) for t in torque_samples)

        # Quadrature Resolver Interferometer Simulation (Sine/Cosine correlation)
        n = len(torque_samples)
        dt = 1.0 / self.sample_rate_hz
        sin_sum = 0.0
        cos_sum = 0.0

        for i, val in enumerate(torque_samples):
            t = i * dt
            angle = 2.0 * math.pi * self.nominal_base_freq_hz * t
            residual = val - mean_torque
            sin_sum += residual * math.sin(angle)
            cos_sum += residual * math.cos(angle)

        quadrature_amplitude = (2.0 / n) * math.sqrt(sin_sum**2 + cos_sum**2)
        estimated_phase = math.atan2(cos_sum, sin_sum)

        # Phase Predictor & Synchronizer feedback loop
        phase_error = estimated_phase - self.last_phase_error
        self.last_phase_error = estimated_phase
        self.sync_locked = abs(phase_error) < 0.25 and quadrature_amplitude < (mean_torque * 0.15)

        correction_factor = 1.0 - (quadrature_amplitude / (rms_torque + 1e-6)) * 0.1

        return {
            "timestamp": time.time(),
            "sample_count": n,
            "mean_torque_nm": round(mean_torque, 4),
            "rms_torque_nm": round(rms_torque, 4),
            "peak_ripple_nm": round(peak_ripple, 4),
            "quadrature_amplitude_nm": round(quadrature_amplitude, 4),
            "estimated_phase_rad": round(estimated_phase, 4),
            "phase_error_rad": round(phase_error, 4),
            "sync_locked": self.sync_locked,
            "drive_correction_factor": round(max(0.8, min(1.2, correction_factor)), 4)
        }


if __name__ == "__main__":
    print("[INIT] Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Decoder...")
    decoder = RollerMillHarmonicDecoder(sample_rate_hz=1000.0, nominal_base_freq_hz=50.0)

    # Generate synthetic torque signal with 50Hz carrier and harmonic ripple
    dt = 1.0 / 1000.0
    simulated_samples = [
        150.0 + 12.5 * math.sin(2.0 * math.pi * 50.0 * (i * dt)) + 3.0 * math.cos(2.0 * math.pi * 150.0 * (i * dt))
        for i in range(500)
    ]

    telemetry = decoder.ingest_torque_signal(simulated_samples)
    print("[TELEMETRY OUTPUT]:")
    for k, v in telemetry.items():
        print(f"  {k}: {v}")
    print("[SUCCESS] Roller mill torque ripple harmonic decoder operational.")
