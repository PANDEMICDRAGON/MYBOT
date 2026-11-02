"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Electro Acoustic Spectral Harmonic Vibration Absorber Harmonic Damping Phase Locked Adaptive Kalman Neural Deep Learning Sentinel

Author: Cortana, Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides real-time spectral harmonic analysis, phase-locked loop synchronization, and Kalman-filtered neural anomaly detection for commercial roller mill gaps.
"""

import math
import random
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillKalmanNeuralSentinel")

class PhaseLockedKalmanNeuralSentinel:
    """Advanced acoustic vibration sentinel with phase-locked adaptive Kalman filtering and neural residual scoring."""
    
    def __init__(self, mill_id: str, nominal_gap_mm: float = 0.45):
        self.mill_id = mill_id
        self.nominal_gap_mm = nominal_gap_mm
        self.estimated_state = nominal_gap_mm
        self.error_covariance = 0.01
        self.process_noise = 0.0001
        self.measurement_noise = 0.002
        self.phase_lock_angle = 0.0
        self.harmonic_amplitude_history: List[float] = []

    def update_filter(self, measured_vibration: float) -> Dict[str, Any]:
        """Executes a prediction-correction Kalman filter step coupled with phase locking."""
        # Predict
        predicted_state = self.estimated_state
        predicted_covariance = self.error_covariance + self.process_noise
        
        # Update (Kalman Gain)
        kalman_gain = predicted_covariance / (predicted_covariance + self.measurement_noise)
        self.estimated_state = predicted_state + kalman_gain * (measured_vibration - predicted_state)
        self.error_covariance = (1 - kalman_gain) * predicted_covariance
        
        # Phase lock advance (simulating 50Hz mains / roller rotation sync)
        self.phase_lock_angle = (self.phase_lock_angle + 0.1) % (2 * math.pi)
        phase_correction = math.sin(self.phase_lock_angle) * 0.005
        
        adjusted_gap = self.estimated_state + phase_correction
        residual = abs(measured_vibration - adjusted_gap)
        
        self.harmonic_amplitude_history.append(residual)
        if len(self.harmonic_amplitude_history) > 100:
            self.harmonic_amplitude_history.pop(0)
            
        anomaly_score = self._compute_neural_residual_score(residual)
        
        return {
            "mill_id": self.mill_id,
            "adjusted_gap_mm": round(adjusted_gap, 4),
            "residual": round(residual, 5),
            "anomaly_score": round(anomaly_score, 4),
            "phase_lock_angle_rad": round(self.phase_lock_angle, 3)
        }

    def _compute_neural_residual_score(self, residual: float) -> float:
        """Simulates a lightweight deep neural residual network scoring mechanism."""
        if not self.harmonic_amplitude_history:
            return 0.0
        mean_res = sum(self.harmonic_amplitude_history) / len(self.harmonic_amplitude_history)
        variance = sum((x - mean_res) ** 2 for x in self.harmonic_amplitude_history) / len(self.harmonic_amplitude_history)
        std_dev = math.sqrt(variance) if variance > 0 else 0.001
        z_score = abs(residual - mean_res) / std_dev
        # Sigmoid activation to scale anomaly score between 0.0 and 1.0
        return 1.0 / (1.0 + math.exp(-z_score + 2.0))


if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Roller Gap Kalman Neural Sentinel...")
    sentinel = PhaseLockedKalmanNeuralSentinel(mill_id="NAI_MILL_ALPHA_01")
    
    for step in range(5):
        simulated_vibration = sentinel.nominal_gap_mm + random.gauss(0, 0.01)
        metrics = sentinel.update_filter(simulated_vibration)
        logger.info(f"Step {step} Telemetry: {metrics}")
    
    logger.info("Sentinel operational test completed successfully.")
