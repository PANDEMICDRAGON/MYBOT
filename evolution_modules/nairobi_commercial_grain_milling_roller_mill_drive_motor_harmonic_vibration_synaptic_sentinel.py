"""Nairobi Commercial Grain Milling Roller Mill Drive Motor Harmonic Vibration Synaptic Sentinel."""

import math
import time
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DriveMotorHarmonicSentinel")


class MotorHarmonicSynapse:
    """Simulates synaptic filtering for stator current and vibration harmonics."""

    def __init__(self, alpha: float = 0.15):
        self.alpha = alpha
        self.weights = [0.5, 0.3, 0.2]
        self.bias = 0.05

    def compute_synapse_response(self, harmonics: List[float]) -> float:
        if len(harmonics) < 3:
            return 0.0
        activation = sum(w * h for w, h in zip(self.weights, harmonics[:3])) + self.bias
        return 1.0 / (1.0 + math.exp(-activation))


class RollerMillDriveMotorHarmonicSentinel:
    """Monitors high-power induction motor harmonics and isolates impending mechanical faults."""

    def __init__(self, motor_id: str, rated_rpm: int = 1480):
        self.motor_id = motor_id
        self.rated_rpm = rated_rpm
        self.synapse = MotorHarmonicSynapse()
        self.baseline_harmonic_distortion = 0.035  # 3.5% THD baseline
        logger.info(f"Initialized Drive Motor Harmonic Sentinel for motor {motor_id} at {rated_rpm} RPM.")

    def analyze_vibration_spectrum(self, spectrum_data: Dict[str, float]) -> Dict[str, Any]:
        thd = spectrum_data.get("total_harmonic_distortion", 0.04)
        vibration_g = spectrum_data.get("vibration_acceleration_g", 0.12)
        stator_current_imbalance = spectrum_data.get("current_imbalance_pct", 1.2)

        harmonics = [thd, vibration_g, stator_current_imbalance / 10.0]
        synapse_score = self.synapse.compute_synapse_response(harmonics)

        anomaly_detected = thd > (self.baseline_harmonic_distortion * 1.8) or vibration_g > 0.35
        action_required = "IMMEDIATE_SHUTDOWN" if anomaly_detected and synapse_score > 0.75 else "MONITOR"

        report = {
            "motor_id": self.motor_id,
            "timestamp": time.time(),
            "synapse_activation": round(synapse_score, 4),
            "anomaly_flag": anomaly_detected,
            "action": action_required,
            "diagnostics": {
                "thd": thd,
                "vibration_g": vibration_g,
                "stator_current_imbalance_pct": stator_current_imbalance
            }
        }
        return report


if __name__ == "__main__":
    sentinel = RollerMillDriveMotorHarmonicSentinel("RM-MOTOR-NBI-04")
    sample_spectrum = {
        "total_harmonic_distortion": 0.068,
        "vibration_acceleration_g": 0.42,
        "current_imbalance_pct": 3.5
    }
    result = sentinel.analyze_vibration_spectrum(sample_spectrum)
    print("Drive Motor Harmonic Analysis Result:", result)
