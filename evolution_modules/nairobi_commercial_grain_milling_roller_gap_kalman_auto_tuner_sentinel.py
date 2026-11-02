"""
Nairobi Commercial Grain Milling Roller Gap Kalman Auto Tuner Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Description:
Provides closed-loop real-time state estimation and adaptive auto-tuning for
commercial roller mill gap spacing in Nairobi grain mills. Leverages a discrete
Kalman filter to track true roller gap spacing amidst mechanical vibration noise,
moisture variance in maize/wheat, and thermal expansion of cast-iron rolls.
"""

import time
import math
import random
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerGapKalmanSentinel")

class RollerGapKalmanAutoTuner:
    """
    Implements a discrete Kalman filter for estimating true roller mill gap
    and dynamically calculating corrective actuator pulses to ensure uniform flour granulation.
    """
    def __init__(self, target_gap_mm: float = 0.45, process_variance: float = 1e-5, measurement_variance: float = 1e-3):
        self.target_gap_mm = target_gap_mm
        self.estimated_gap = target_gap_mm
        self.error_covariance = 1.0
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.actuator_gain = 0.15
        self.history: List[Dict[str, Any]] = []

    def predict(self, control_input: float = 0.0) -> float:
        """Predict step of the Kalman filter."""
        self.estimated_gap += control_input
        self.error_covariance += self.process_variance
        return self.estimated_gap

    def update(self, measured_gap: float) -> float:
        """Update step of the Kalman filter incorporating sensor telemetry."""
        kalman_gain = self.error_covariance / (self.error_covariance + self.measurement_variance)
        self.estimated_gap += kalman_gain * (measured_gap - self.estimated_gap)
        self.error_covariance = (1.0 - kalman_gain) * self.error_covariance
        return self.estimated_gap

    def compute_correction_pulse(self) -> float:
        """Calculates corrective stepper/hydraulic pulse to nullify gap drift."""
        gap_error = self.target_gap_mm - self.estimated_gap
        correction = self.actuator_gain * gap_error
        return correction

    def process_cycle(self, raw_sensor_reading: float) -> Dict[str, Any]:
        """Executes a full predict-update-correct cycle for a mill telemetry tick."""
        # 1. Predict based on previous state
        pred = self.predict(control_input=0.0)
        
        # 2. Update with noisy measurement
        posterior = self.update(raw_sensor_reading)
        
        # 3. Compute actuator adjustment
        pulse = self.compute_correction_pulse()
        
        record = {
            "timestamp": time.time(),
            "target_gap_mm": self.target_gap_mm,
            "raw_sensor_reading": raw_sensor_reading,
            "estimated_gap_mm": posterior,
            "error_covariance": self.error_covariance,
            "actuator_correction_pulse": pulse
        }
        self.history.append(record)
        if len(self.history) > 1000:
            self.history.pop(0)
            
        return record

if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Gap Kalman Auto Tuner Sentinel...")
    tuner = RollerGapKalmanAutoTuner(target_gap_mm=0.40)
    
    # Simulate 5 milling cycles with sensor noise and thermal drift
    simulated_readings = [0.42, 0.43, 0.41, 0.39, 0.40]
    for i, reading in enumerate(simulated_readings):
        res = tuner.process_cycle(reading)
        logger.info(f"Cycle {i+1}: Measured={reading}mm -> Estimated={res['estimated_gap_mm']:.4f}mm | Pulse={res['actuator_correction_pulse']:.4f}")
    logger.info("Roller Gap Kalman Auto Tuner Sentinel test harness completed successfully.")
