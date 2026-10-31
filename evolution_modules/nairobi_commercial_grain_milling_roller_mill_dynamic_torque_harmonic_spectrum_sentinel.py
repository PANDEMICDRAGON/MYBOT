"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Harmonic Spectrum Sentinel Module."""

import math
import statistics
import time
from typing import Dict, List, Any, Optional


class RollerMillTorqueHarmonicSentinel:
    """Performs real-time Fast Fourier Transform (FFT) approximations on roller mill torque telemetry
    to identify harmonic spectrum anomalies, gear mesh wear, and belt slippage in Nairobi mills.
    """

    def __init__(self, sample_rate_hz: float = 50.0, harmonic_threshold: float = 2.5) -> None:
        self.sample_rate_hz = sample_rate_hz
        self.harmonic_threshold = harmonic_threshold
        self.anomaly_count = 0
        self.last_audit_timestamp = time.time()

    def _compute_dft_magnitudes(self, signal: List[float]) -> List[float]:
        """Computes discrete Fourier transform frequency bin magnitudes for the given signal."""
        N = len(signal)
        if N == 0:
            return []
        
        magnitudes = []
        # Analyze up to N//2 frequency bins
        for k in range(N // 2):
            real_sum = 0.0
            imag_sum = 0.0
            for n in range(N):
                angle = (2.0 * math.pi * k * n) / N
                real_sum += signal[n] * math.cos(angle)
                imag_sum -= signal[n] * math.sin(angle)
            magnitude = math.sqrt(real_sum**2 + imag_sum**2) / N
            magnitudes.append(magnitude)
        return magnitudes

    def analyze_spectrum(self, torque_samples: List[float]) -> Dict[str, Any]:
        """Analyzes the dynamic torque signal for harmonic abnormalities."""
        if not torque_samples or len(torque_samples) < 16:
            return {
                "status": "INSUFFICIENT_DATA",
                "anomaly_detected": False,
                "dominant_frequencies": [],
                "timestamp": time.time()
            }

        mean_val = statistics.mean(torque_samples)
        # Detrend signal
        detrended = [x - mean_val for x in torque_samples]
        magnitudes = self._compute_dft_magnitudes(detrended)

        if not magnitudes:
            return {
                "status": "ANALYSIS_FAILED",
                "anomaly_detected": False,
                "dominant_frequencies": [],
                "timestamp": time.time()
            }

        baseline_noise = statistics.median(magnitudes) if magnitudes else 0.001
        peak_magnitude = max(magnitudes)
        crest_factor = peak_magnitude / (baseline_noise if baseline_noise > 0 else 1.0)

        anomaly_detected = crest_factor > self.harmonic_threshold
        if anomaly_detected:
            self.anomaly_count += 1

        return {
            "status": "OPTIMAL" if not anomaly_detected else "HARMONIC_ANOMALY_DETECTED",
            "anomaly_detected": anomaly_detected,
            "peak_magnitude": peak_magnitude,
            "crest_factor": crest_factor,
            "anomaly_count": self.anomaly_count,
            "timestamp": time.time()
        }


if __name__ == "__main__":
    sentinel = RollerMillTorqueHarmonicSentinel()
    # Simulate normal torque telemetry with a subtle harmonic disturbance
    mock_torque = [10.5 + math.sin(i * 0.2) + (2.5 if i == 20 else 0.0) for i in range(64)]
    result = sentinel.analyze_spectrum(mock_torque)
    print("Sentinel Execution Result:", result)
