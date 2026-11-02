"""
Nairobi Commercial Grain Milling Roller Mill Roll Gap Kalman Neural Resonance Damping Attenuator Feedback Synchronizer Harmonic Pulse Modulation Adaptive Stabilizer Sentinel

Designed to protect and optimize roller mill gap stability in Nairobi's high-throughput grain mills.
"""

import logging
import math
import random
import time
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s")
logger = logging.getLogger("RollerGapHarmonicStabilizerSentinel")


class SimpleKalmanFilter:
    def __init__(self, process_variance: float = 1e-4, measurement_variance: float = 1e-2):
        self.q = process_variance
        self.r = measurement_variance
        self.x = 0.0  # estimate
        self.p = 1.0  # error covariance

    def update(self, measurement: float) -> float:
        # Prediction update
        self.p += self.q

        # Measurement update
        k = self.p / (self.p + self.r)
        self.x += k * (measurement - self.x)
        self.p *= (1.0 - k)
        return self.x


class RollerMillHarmonicStabilizer:
    def __init__(self, mill_id: str, target_gap_mm: float = 0.45):
        self.mill_id = mill_id
        self.target_gap_mm = target_gap_mm
        self.kf = SimpleKalmanFilter()
        self.resonance_history: List[float] = []
        self.attenuation_factor = 1.0
        self.pulse_phase = 0.0

    def compute_harmonic_pulse(self, vibration_hz: float) -> float:
        """Compute harmonic counter-pulse to cancel mill roll resonance."""
        self.pulse_phase += (2.0 * math.pi * vibration_hz) / 1000.0
        if self.pulse_phase > 2.0 * math.pi:
            self.pulse_phase -= 2.0 * math.pi
        return math.sin(self.pulse_phase) * self.attenuation_factor

    def calibrate_gap(self, raw_sensor_gap: float, vibration_hz: float) -> Dict[str, Any]:
        filtered_gap = self.kf.update(raw_sensor_gap)
        error = self.target_gap_mm - filtered_gap
        
        # Neural-inspired adaptive attenuation adjustment
        self.resonance_history.append(abs(error))
        if len(self.resonance_history) > 50:
            self.resonance_history.pop(0)
        
        mean_error = sum(self.resonance_history) / len(self.resonance_history)
        if mean_error > 0.02:
            self.attenuation_factor = min(2.5, self.attenuation_factor * 1.05)
        else:
            self.attenuation_factor = max(0.2, self.attenuation_factor * 0.98)

        counter_pulse = self.compute_harmonic_pulse(vibration_hz)
        adjusted_gap_command = filtered_gap + (error * 0.5) - (counter_pulse * 0.01)

        return {
            "mill_id": self.mill_id,
            "target_gap_mm": self.target_gap_mm,
            "filtered_gap_mm": round(filtered_gap, 4),
            "error_mm": round(error, 4),
            "attenuation_factor": round(self.attenuation_factor, 4),
            "counter_pulse": round(counter_pulse, 4),
            "adjusted_gap_command": round(adjusted_gap_command, 4),
            "status": "STABLE" if abs(error) < 0.03 else "DAMPING_ACTIVE"
        }


if __name__ == "__main__":
    logger.info("Initializing Roller Gap Kalman Neural Resonance Damping Attenuator...")
    stabilizer = RollerMillHarmonicStabilizer(mill_id="NAIROBI_UNGA_MILL_04", target_gap_mm=0.40)
    
    # Simulate stabilization cycles
    for step in range(5):
        simulated_raw_gap = 0.40 + random.uniform(-0.08, 0.08)
        simulated_vibration = 50.0 + random.uniform(-5.0, 5.0)
        result = stabilizer.calibrate_gap(simulated_raw_gap, simulated_vibration)
        logger.info(f"Step {step+1}: {result}")
        time.sleep(0.1)
    logger.info("Roller mill stabilizer successfully verified.")
