"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Spectrum Sentinel module. Provides real-time spectral decomposition and FFT-based anomaly detection for commercial roller mill drives."""

import math
import statistics
from typing import Dict, List, Any


class RollerMillTorqueSpectrumSentinel:
    """Monitors high-frequency torque telemetry from commercial roller mills using spectral analysis."""

    def __init__(self, sample_rate_hz: float = 1000.0, window_size: int = 512):
        self.sample_rate_hz = sample_rate_hz
        self.window_size = window_size
        self.baseline_spectral_energy: float = 0.0
        self.is_calibrated = False

    def calibrate(self, baseline_signals: List[List[float]]) -> None:
        """Calibrate baseline spectral energy profiles from nominal mill runs."""
        energies = []
        for signal in baseline_signals:
            energy = self._compute_approx_spectral_energy(signal)
            energies.append(energy)
        if energies:
            self.baseline_spectral_energy = statistics.mean(energies)
            self.is_calibrated = True

    def _compute_approx_spectral_energy(self, signal: List[float]) -> float:
        """Compute simplified discrete frequency band power as proxy for FFT energy."""
        if not signal:
            return 0.0
        mean_val = statistics.mean(signal)
        variance = statistics.variance(signal, mean_val) if len(signal) > 1 else 0.0
        # Parse alternating high-frequency fluctuations
        diffs = [abs(signal[i] - signal[i - 1]) for i in range(1, len(signal))]
        roughness = statistics.mean(diffs) if diffs else 0.0
        return variance + (roughness * 1.5)

    def analyze_torque_stream(self, torque_samples: List[float]) -> Dict[str, Any]:
        """Analyze a live torque telemetry window for anomalous spectral signatures."""
        if len(torque_samples) < 10:
            return {"status": "insufficient_data", "anomaly_detected": False}

        current_energy = self._compute_approx_spectral_energy(torque_samples)
        
        if not self.is_calibrated:
            return {
                "status": "uncalibrated",
                "current_spectral_energy": current_energy,
                "anomaly_detected": False
            }

        deviation = abs(current_energy - self.baseline_spectral_energy) / (self.baseline_spectral_energy + 1e-6)
        anomaly_detected = deviation > 0.35

        return {
            "status": "nominal" if not anomaly_detected else "spectral_anomaly_detected",
            "baseline_spectral_energy": round(self.baseline_spectral_energy, 4),
            "current_spectral_energy": round(current_energy, 4),
            "deviation_ratio": round(deviation, 4),
            "anomaly_detected": anomaly_detected
        }


if __name__ == "__main__":
    sentinel = RollerMillTorqueSpectrumSentinel()
    # Generate simulated nominal baseline torque oscillations
    nominal_baseline = [
        50.0 + 2.0 * math.sin(i * 0.1) + 0.5 * math.cos(i * 0.5)
        for i in range(512)
    ]
    sentinel.calibrate([nominal_baseline])

    # Test with normal stream
    normal_stream = [
        50.1 + 2.1 * math.sin(i * 0.1) + 0.4 * math.cos(i * 0.5)
        for i in range(512)
    ]
    res_normal = sentinel.analyze_torque_stream(normal_stream)
    print("Normal Stream Result:", res_normal)

    # Test with anomalous vibrating/choking stream
    anomalous_stream = [
        50.0 + 15.0 * math.sin(i * 0.8) + 8.0 * math.cos(i * 1.2)
        for i in range(512)
    ]
    res_anomaly = sentinel.analyze_torque_stream(anomalous_stream)
    print("Anomalous Stream Result:", res_anomaly)
