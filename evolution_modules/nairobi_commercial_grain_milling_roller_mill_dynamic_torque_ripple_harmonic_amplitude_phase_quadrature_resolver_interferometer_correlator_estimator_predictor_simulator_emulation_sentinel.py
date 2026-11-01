"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Simulator Emulation Sentinel
Designed for real-time telemetry processing, harmonic analysis, phase quadrature decoding, and predictive failure simulation in Nairobi roller mills.
"""

import math
import random
import time
from typing import Dict, List, Optional, Tuple


class RollerMillEmulationSentinel:
    """
    Simulates, analyzes, and predicts torque ripple harmonics, phase quadrature signals,
    and interferometer interferometry data for heavy-duty commercial grain milling machinery.
    """

    def __init__(self, mill_id: str = "NRB-MILL-ALPHA-01") -> None:
        self.mill_id = mill_id
        self.baseline_frequency_hz = 50.0
        self.sampling_rate_hz = 1000.0
        self.running = False
        self._harmonic_buffer: List[float] = []

    def compute_torque_ripple_harmonics(
        self, base_torque_nm: float, rpm: float, harmonic_order: int = 5
    ) -> Dict[str, float]:
        """Compute harmonic amplitudes and phase shifts for roller mill drive torque."""
        harmonics = {}
        fundamental_freq = (rpm / 60.0) * harmonic_order
        for n in range(1, harmonic_order + 1):
            amplitude = (base_torque_nm / (n * 1.5)) * (
                1.0 + 0.1 * random.gauss(0, 0.05)
            )
            phase_rad = (n * math.pi / 4.0) + random.uniform(-0.02, 0.02)
            harmonics[f"harmonic_{n}_freq_{fundamental_freq * n:.2f}Hz"] = {
                "amplitude_nm": round(amplitude, 4),
                "phase_rad": round(phase_rad, 4),
            }
        return harmonics

    def decode_phase_quadrature(self, raw_signal_a: float, raw_signal_b: float) -> Tuple[float, float]:
        """Decode quadrature encoder signals for high-precision roller nip gap adjustment."""
        theta = math.atan2(raw_signal_b, raw_signal_a)
        normalized_theta = (theta + 2 * math.pi) % (2 * math.pi)
        resolved_degrees = math.degrees(normalized_theta)
        amplitude = math.sqrt(raw_signal_a**2 + raw_signal_b**2)
        return round(resolved_degrees, 3), round(amplitude, 3)

    def run_simulation_cycle(self, duration_seconds: int = 2) -> Dict[str, any]:
        """Execute a full diagnostic simulation cycle mimicking live mill operation."""
        start_time = time.time()
        torque_readings = []
        phase_readings = []

        steps = int(duration_seconds * 50)
        for _ in range(steps):
            base_torque = 250.0 + random.uniform(-15.0, 15.0)
            harmonics = self.compute_torque_ripple_harmonics(base_torque, rpm=1450.0)
            deg, amp = self.decode_phase_quadrature(
                math.cos(time.time() * 10),
                math.sin(time.time() * 10)
            )
            torque_readings.append(base_torque)
            phase_readings.append(deg)

        avg_torque = sum(torque_readings) / len(torque_readings)
        anomaly_score = abs(max(torque_readings) - min(torque_readings)) / avg_torque

        return {
            "mill_id": self.mill_id,
            "status": "OPTIMAL" if anomaly_score < 0.25 else "WARNING",
            "average_torque_nm": round(avg_torque, 2),
            "torque_ripple_anomaly_score": round(anomaly_score, 4),
            "last_quadrature_degree": phase_readings[-1],
            "timestamp": time.time(),
        }


if __name__ == "__main__":
    sentinel = RollerMillEmulationSentinel("NRB-UGALI-MILL-07")
    report = sentinel.run_simulation_cycle(duration_seconds=1)
    print("Nairobi Roller Mill Emulation Sentinel Report:", report)
