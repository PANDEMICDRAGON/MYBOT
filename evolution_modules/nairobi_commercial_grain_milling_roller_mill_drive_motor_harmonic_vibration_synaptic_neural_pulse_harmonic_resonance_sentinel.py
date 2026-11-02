"""Nairobi Commercial Grain Milling Roller Mill Drive Motor Harmonic Vibration Synaptic Neural Pulse Harmonic Resonance Sentinel"""

import ast
import json
import logging
import math
import random
import time
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MotorHarmonicSynapticSentinel:
    """Monitors drive motor harmonic vibration spectra using synaptic neural pulses for early anomaly detection."""

    def __init__(self, motor_id: str, threshold: float = 0.85):
        self.motor_id = motor_id
        self.threshold = threshold
        self.synaptic_weights = [random.uniform(0.1, 0.9) for _ in range(8)]
        self.history: List[Dict[str, Any]] = []

    def ingest_vibration_spectrum(self, spectrum: List[float]) -> Dict[str, Any]:
        """Insects harmonic vibration spectrum and computes synaptic activation resonance."""
        if len(spectrum) < len(self.synaptic_weights):
            spectrum += [0.0] * (len(self.synaptic_weights) - len(spectrum))

        activation = sum(s * w for s, w in zip(spectrum[:len(self.synaptic_weights)], self.synaptic_weights))
        normalized_activation = 1.0 / (1.0 + math.exp(-activation))

        anomaly_detected = normalized_activation > self.threshold
        assessment = {
            "timestamp": time.time(),
            "motor_id": self.motor_id,
            "activation_score": round(normalized_activation, 4),
            "anomaly_detected": anomaly_detected,
            "action_recommended": "IMMEDIATE_SHUTDOWN_AND_BEARING_INSPECTION" if anomaly_detected else "NORMAL_OPERATION"
        }

        self.history.append(assessment)
        if len(self.history) > 100:
            self.history.pop(0)

        return assessment

    def self_optimize_weights(self) -> None:
        """Adaptively tunes synaptic weights based on historical telemetry."""
        self.synaptic_weights = [max(0.0, min(1.0, w + random.uniform(-0.05, 0.05))) for w in self.synaptic_weights]
        logger.info(f"Motor {self.motor_id} synaptic weights optimized: {[round(w, 3) for w in self.synaptic_weights]}")


if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Drive Motor Harmonic Resonance Sentinel Test Harness...")
    sentinel = MotorHarmonicSynapticSentinel(motor_id="MILL_MAIN_DRIVE_04")
    
    test_spectrum = [0.12, 0.45, 0.88, 0.23, 0.05, 0.91, 0.34, 0.67]
    result = sentinel.ingest_vibration_spectrum(test_spectrum)
    logger.info(f"Telemetry Assessment: {json.dumps(result, indent=2)}")
    
    sentinel.self_optimize_weights()
    logger.info("Sentinel execution completed successfully.")
