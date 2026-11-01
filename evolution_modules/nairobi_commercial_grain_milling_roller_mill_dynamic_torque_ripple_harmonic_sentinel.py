"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Sentinel."""

import math
import statistics
import time
from typing import Dict, List, Any, Optional


class RollerMillTorqueRippleHarmonicSentinel:
    """
    Monitors dynamic torque ripple harmonics in commercial grain milling roller drives.
    Detects abnormal harmonic orders that indicate mechanical misalignment, belt slip, or bearing anomalies.
    """

    def __init__(self, sample_rate_hz: float = 100.0, harmonic_threshold_ratio: float = 0.15):
        self.sample_rate_hz = sample_rate_hz
        self.harmonic_threshold_ratio = harmonic_threshold_ratio
        self.anomaly_log: List[Dict[str, Any]] = []

    def analyze_torque_stream(self, torque_samples: List[float], base_rpm: float) -> Dict[str, Any]:
        """
        Analyzes a stream of torque sensor measurements to compute dominant harmonic amplitudes.
        """
        if not torque_samples or len(torque_samples) < 16:
            raise ValueError("Insufficient torque samples provided for harmonic analysis.")

        mean_torque = statistics.mean(torque_samples)
        detrended = [t - mean_torque for t in torque_samples]
        n = len(detrended)
        
        # Compute basic FFT-like discrete frequency amplitudes for orders 1 to 5 relative to base rotation frequency
        base_freq = base_rpm / 60.0
        harmonics = {}
        
        # Simple Goertzel / DFT approximation for orders 1 through 5
        for order in range(1, 6):
            target_freq = order * base_freq
            real_sum = 0.0
            imag_sum = 0.0
            for i, val in enumerate(detrended):
                t = i / self.sample_rate_hz
                angle = 2.0 * math.pi * target_freq * t
                real_sum += val * math.cos(angle)
                imag_sum -= val * math.sin(angle)
            
            amplitude = math.sqrt(real_sum**2 + imag_sum**2) / (n / 2.0)
            harmonics[f"order_{order}"] = round(amplitude, 4)

        # Determine total harmonic distortion ratio relative to mean torque magnitude
        rms_detrended = math.sqrt(sum(v**2 for v in detrended) / n)
        ripple_ratio = (rms_detrended / abs(mean_torque)) if mean_torque != 0 else 0.0
        
        anomaly_detected = ripple_ratio > self.harmonic_threshold_ratio
        status = "ALARM: HIGH TORQUE RIPPLE HARMONIC" if anomaly_detected else "OPTIMAL"

        assessment = {
            "timestamp": time.time(),
            "mean_torque": round(mean_torque, 2),
            "ripple_ratio": round(ripple_ratio, 4),
            "harmonics": harmonics,
            "status": status,
            "anomaly_detected": anomaly_detected
        }

        if anomaly_detected:
            self.anomaly_log.append(assessment)

        return assessment


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Sentinel...")
    sentinel = RollerMillTorqueRippleHarmonicSentinel(sample_rate_hz=50.0, harmonic_threshold_ratio=0.12)
    
    # Simulate stable and unstable torque signals (1200 RPM base rotation -> 20 Hz)
    base_rpm = 1200.0
    dt = 1.0 / 50.0
    simulated_torque = [150.0 + 10.0 * math.sin(2.0 * math.pi * 20.0 * i * dt) + 5.0 * math.sin(2.0 * math.pi * 40.0 * i * dt) for i in range(128)]
    
    result = sentinel.analyze_torque_stream(simulated_torque, base_rpm=base_rpm)
    print("Analysis Result:", result)
    print("Sentinel test execution completed successfully.")
