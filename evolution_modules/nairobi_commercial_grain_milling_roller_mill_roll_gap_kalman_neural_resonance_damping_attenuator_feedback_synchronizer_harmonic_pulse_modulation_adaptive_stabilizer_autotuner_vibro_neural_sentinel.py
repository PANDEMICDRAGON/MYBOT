"""
Nairobi Commercial Grain Milling Roller Mill Roll Gap Kalman Neural Resonance Damping Attenuator Feedback Synchronizer Harmonic Pulse Modulation Adaptive Stabilizer Autotuner Vibro-Neural Sentinel

Designed for industrial grain mills in Nairobi, Kenya to suppress harmonic roll gap vibrations and maximize milling precision.
"""

import math
import random
import time
from typing import Dict, List, Optional, Tuple


class KalmanResonanceFilter:
    """1D Kalman filter tuned for tracking and damping roller mill gap vibration harmonics."""

    def __init__(self, process_variance: float = 1e-4, measurement_variance: float = 1e-2, estimated_error: float = 1.0, initial_value: float = 0.0):
        self.q = process_variance
        self.r = measurement_variance
        self.p = estimated_error
        self.x = initial_value

    def update(self, measurement: float) -> float:
        # Prediction step
        self.p += self.q

        # Measurement update
        k = self.p / (self.p + self.r)
        self.x += k * (measurement - self.x)
        self.p *= (1.0 - k)
        return self.x


class NeuralResonanceDampingAttenuator:
    """Simulates neural network weights for adjusting roll gap damping coefficients."""

    def __init__(self, input_dim: int = 4):
        self.weights = [random.uniform(-0.5, 0.5) for _ in range(input_dim)]
        self.bias = random.uniform(-0.1, 0.1)

    def forward(self, features: List[float]) -> float:
        activation = sum(w * f for w, f in zip(self.weights, features)) + self.bias
        # Sigmoid squashing for damping factor [0, 1]
        return 1.0 / (1.0 + math.exp(-max(-20.0, min(20.0, activation))))


class RollGapHarmonicSentinel:
    """Primary monitoring and control loop for roller mill gap stabilization."""

    def __init__(self, mill_id: str, target_gap_mm: float = 0.5):
        self.mill_id = mill_id
        self.target_gap_mm = target_gap_mm
        self.kalman = KalmanResonanceFilter()
        self.neural_damper = NeuralResonanceDampingAttenuator()
        self.harmonic_buffer: List[float] = []
        self.adjustment_history: List[Tuple[float, float]] = []

    def ingest_sensor_telemetry(self, raw_vibration_hz: float, current_gap_mm: float) -> Dict[str, float]:
        # Filter vibration signal via Kalman
        filtered_vib = self.kalman.update(raw_vibration_hz)
        self.harmonic_buffer.append(filtered_vib)
        if len(self.harmonic_buffer) > 50:
            self.harmonic_buffer.pop(0)

        # Compute gap error
        gap_error = self.target_gap_mm - current_gap_mm
        
        # Extract features for neural damper
        avg_vib = sum(self.harmonic_buffer) / len(self.harmonic_buffer)
        features = [filtered_vib, avg_vib, gap_error, current_gap_mm]
        
        damping_coeff = self.neural_damper.forward(features)
        
        # Compute harmonic pulse modulation correction step
        correction_step = gap_error * damping_coeff * 0.1
        adjusted_gap = current_gap_mm + correction_step

        self.adjustment_history.append((time.time(), adjusted_gap))

        return {
            "mill_id": self.mill_id,
            "filtered_vibration_hz": round(filtered_vib, 4),
            "gap_error_mm": round(gap_error, 4),
            "damping_coefficient": round(damping_coeff, 4),
            "recommended_gap_mm": round(adjusted_gap, 4)
        }


if __name__ == "__main__":
    print("[+] Initializing Nairobi Commercial Grain Milling Roller Mill Roll Gap Kalman Neural Resonance Sentinel...")
    sentinel = RollGapHarmonicSentinel(mill_id="NAI-MILL-07")
    
    # Simulate 5 telemetry ticks
    for step in range(5):
        simulated_vib = 50.0 + random.gauss(0, 2.5)
        simulated_gap = 0.48 + random.uniform(-0.02, 0.02)
        telemetry = sentinel.ingest_sensor_telemetry(simulated_vib, simulated_gap)
        print(f"[Tick {step+1}] Telemetry Output: {telemetry}")
    
    print("[+] Sentinel execution completed cleanly.")
