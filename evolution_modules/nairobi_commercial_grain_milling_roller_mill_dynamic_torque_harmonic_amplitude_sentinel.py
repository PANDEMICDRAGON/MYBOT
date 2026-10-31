"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Harmonic Amplitude Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Monitors roller mill drive train torque harmonic amplitudes using Fast Fourier Transform
approximations to detect abnormal load profiles, structural resonance, and gear mesh faults.
"""

import math
import time
import statistics
from typing import List, Dict, Any, Tuple


class RollerMillTorqueHarmonicSentinel:
    """Analyzes high-frequency torque sensor telemetry for harmonic anomalies in commercial roller mills."""

    def __init__(self, sample_rate_hz: float = 100.0, harmonic_threshold_nm: float = 45.0):
        self.sample_rate_hz = sample_rate_hz
        self.harmonic_threshold_nm = harmonic_threshold_nm
        self.alert_history: List[Dict[str, Any]] = []

    def analyze_torque_stream(self, mill_id: str, torque_samples: List[float]) -> Dict[str, Any]:
        """Process a window of torque readings (Nm) and compute dominant harmonic amplitudes."""
        if not torque_samples:
            raise ValueError("Torque sample stream cannot be empty.")

        mean_torque = statistics.mean(torque_samples)
        detrended = [t - mean_torque for t in torque_samples]
        n = len(detrended)

        # Simple Goertzel / DFT approximation for primary harmonic frequencies (e.g., 5Hz, 15Hz, 30Hz)
        frequencies_to_check = [5.0, 15.0, 30.0]
        harmonic_amplitudes = {}

        for freq in frequencies_to_check:
            real_sum = 0.0
            imag_sum = 0.0
            for i, val in enumerate(detrended):
                t_sec = i / self.sample_rate_hz
                angle = 2.0 * math.pi * freq * t_sec
                real_sum += val * math.cos(angle)
                imag_sum -= val * math.sin(angle)
            
            amplitude = math.sqrt(real_sum**2 + imag_sum**2) / (n / 2.0) if n > 0 else 0.0
            harmonic_amplitudes[f"{freq}Hz"] = round(amplitude, 3)

        max_harmonic = max(harmonic_amplitudes.values(), default=0.0)
        status = "NORMAL"
        action_required = False

        if max_harmonic > self.harmonic_threshold_nm:
            status = "WARNING_HARMONIC_ELEVATED"
            action_required = True
            alert_record = {
                "timestamp": time.time(),
                "mill_id": mill_id,
                "max_harmonic_nm": max_harmonic,
                "amplitudes": harmonic_amplitudes,
                "status": status
            }
            self.alert_history.append(alert_record)

        return {
            "mill_id": mill_id,
            "mean_torque_nm": round(mean_torque, 2),
            "harmonic_amplitudes_nm": harmonic_amplitudes,
            "max_harmonic_nm": max_harmonic,
            "status": status,
            "action_required": action_required
        }

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "total_alerts": len(self.alert_history),
            "recent_alerts": self.alert_history[-5:]
        }


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Harmonic Amplitude Sentinel...")
    sentinel = RollerMillTorqueHarmonicSentinel(sample_rate_hz=50.0, harmonic_threshold_nm=30.0)
    
    # Simulate normal torque profile with minor 15Hz harmonic noise
    simulated_torque = [
        120.0 + 10.0 * math.sin(2.0 * math.pi * 15.0 * (i / 50.0)) + (i % 3)
        for i in range(250)
    ]
    
    result = sentinel.analyze_torque_stream("MILL_NAIROBI_INDUSTRIAL_01", simulated_torque)
    print("Analysis Result:", result)
    
    # Simulate high harmonic anomaly
    abnormal_torque = [
        120.0 + 50.0 * math.sin(2.0 * math.pi * 30.0 * (i / 50.0)) + (i % 7)
        for i in range(250)
    ]
    result_anomaly = sentinel.analyze_torque_stream("MILL_NAIROBI_INDUSTRIAL_01", abnormal_torque)
    print("Anomaly Analysis Result:", result_anomaly)
    print("Diagnostics:", sentinel.get_diagnostics())
    print("Execution complete. Sentinel active for Michael Obiero.")
