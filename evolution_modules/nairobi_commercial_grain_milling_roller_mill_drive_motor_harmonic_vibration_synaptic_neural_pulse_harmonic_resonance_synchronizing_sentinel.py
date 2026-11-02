"""Nairobi Commercial Grain Milling Roller Mill Drive Motor Harmonic Vibration Synaptic Neural Pulse Harmonic Resonance Synchronizing Sentinel."""

import ast
import logging
import math
import random
import time
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("RollerMillHarmonicSynchronizingSentinel")


class RollerMillHarmonicSynchronizingSentinel:
    """Monitors, analyzes, and synchronizes harmonic vibration pulses in roller mill drive motors."""

    def __init__(self, motor_id: str, nominal_rpm: float = 1450.0) -> None:
        self.motor_id = motor_id
        self.nominal_rpm = nominal_rpm
        self.resonance_history: List[float] = []
        self.sync_coefficient = 1.0

    def ingest_vibration_telemetry(self, vibration_spectrum: List[float]) -> Dict[str, Any]:
        """Analyze incoming vibration spectrum for harmonic dissonance and compute synchronization tuning."""
        try:
            if not vibration_spectrum:
                raise ValueError("Empty vibration spectrum received.")

            mean_amplitude = sum(vibration_spectrum) / len(vibration_spectrum)
            peak_amplitude = max(vibration_spectrum)
            variance = sum((v - mean_amplitude) ** 2 for v in vibration_spectrum) / len(vibration_spectrum)
            std_dev = math.sqrt(variance)

            # Harmonic anomaly index calculation
            harmonic_anomaly_index = (peak_amplitude / (mean_amplitude + 1e-6)) * (1.0 + std_dev)

            status = "NOMINAL"
            adjustment_factor = 0.0

            if harmonic_anomaly_index > 3.5:
                status = "CRITICAL_RESONANCE_DETECTED"
                adjustment_factor = -0.15 * math.copysign(1.0, harmonic_anomaly_index - 3.5)
                self.sync_coefficient = max(0.7, min(1.3, self.sync_coefficient + adjustment_factor))
            elif harmonic_anomaly_index > 2.2:
                status = "WARNING_ELEVATED_HARMONICS"
                adjustment_factor = -0.05
                self.sync_coefficient = max(0.85, min(1.15, self.sync_coefficient + adjustment_factor))

            self.resonance_history.append(harmonic_anomaly_index)
            if len(self.resonance_history) > 100:
                self.resonance_history.pop(0)

            telemetry = {
                "motor_id": self.motor_id,
                "timestamp": time.time(),
                "mean_amplitude": mean_amplitude,
                "peak_amplitude": peak_amplitude,
                "harmonic_anomaly_index": harmonic_anomaly_index,
                "sync_coefficient": self.sync_coefficient,
                "status": status
            }
            logger.info(f"Motor {self.motor_id} telemetry processed: status={status}, anomaly_index={harmonic_anomaly_index:.3f}")
            return telemetry
        except Exception as e:
            logger.error(f"Error processing vibration telemetry for motor {self.motor_id}: {e}")
            return {"motor_id": self.motor_id, "error": str(e), "status": "ERROR"}

    def generate_synaptic_neural_pulse(self) -> Dict[str, Any]:
        """Generate a corrective synaptic neural pulse to phase-lock drive motor frequency."""
        pulse_amplitude = random.uniform(0.95, 1.05) * self.sync_coefficient
        return {
            "motor_id": self.motor_id,
            "pulse_type": "SYNAPTIC_NEURAL_HARMONIC_LOCK",
            "target_frequency_multiplier": pulse_amplitude,
            "timestamp": time.time()
        }


if __name__ == "__main__":
    sentinel = RollerMillHarmonicSynchronizingSentinel(motor_id="MILL_MOTOR_NRB_04")
    sample_spectrum = [0.4, 0.5, 0.6, 2.1, 0.5, 0.4, 3.8, 0.6]
    result = sentinel.ingest_vibration_telemetry(sample_spectrum)
    pulse = sentinel.generate_synaptic_neural_pulse()
    print("Sentinel Execution Result:", result)
    print("Generated Neural Pulse:", pulse)
