"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Depolarizer Module

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import math
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueDepolarizer")


class RollerMillTorqueRippleDepolarizer:
    """
    Computes quadrature resolver interferometry on roller mill torque ripples,
    demodulating harmonic amplitudes and phases to synchronize mechanical
    drives and protect against catastrophic spindle depolarization in Nairobi mills.
    """

    def __init__(self, mill_id: str, nominal_rpm: float = 1450.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.history: List[Dict[str, Any]] = []

    def process_torque_signal(self, raw_torque_samples: List[float], harmonic_order: int = 3) -> Dict[str, Any]:
        """
        Processes raw torque transducer samples to extract quadrature resolver phase,
        amplitude, and compute depolarization compensation vectors.
        """
        if not raw_torque_samples:
            raise ValueError("Raw torque samples cannot be empty.")

        mean_torque = statistics.mean(raw_torque_samples)
        filtered_samples = [s - mean_torque for s in raw_torque_samples]
        
        # Simulate quadrature demodulation (Sine/Cosine orthogonal projection)
        n = len(filtered_samples)
        sin_sum = 0.0
        cos_sum = 0.0
        for i, val in enumerate(filtered_samples):
            angle = 2.0 * math.pi * harmonic_order * i / max(n, 1)
            sin_sum += val * math.sin(angle)
            cos_sum += val * math.cos(angle)

        amplitude = (2.0 / max(n, 1)) * math.sqrt(sin_sum**2 + cos_sum**2)
        phase_rad = math.atan2(cos_sum, sin_sum)
        phase_deg = math.degrees(phase_rad)

        # Depolarization / synchronization compensation factor
        compensation_factor = 1.0 / (1.0 + abs(amplitude * 0.05))
        synchronized_rpm = self.nominal_rpm * compensation_factor

        result = {
            "mill_id": self.mill_id,
            "mean_torque": mean_torque,
            "harmonic_order": harmonic_order,
            "amplitude": amplitude,
            "phase_degrees": phase_deg,
            "compensation_factor": compensation_factor,
            "synchronized_rpm": synchronized_rpm,
            "status": "OPTIMIZED"
        }

        self.history.append(result)
        logger.info(f"Processed mill {self.mill_id}: Amplitude={amplitude:.4f}, Phase={phase_deg:.2f} deg")
        return result

    def get_telemetry_summary(self) -> Dict[str, Any]:
        if not self.history:
            return {"status": "NO_DATA"}
        latest = self.history[-1]
        return {
            "mill_id": self.mill_id,
            "total_processed": len(self.history),
            "latest_amplitude": latest["amplitude"],
            "latest_phase": latest["phase_degrees"]
        }


if __name__ == "__main__":
    print("Initializing Nairobi Roller Mill Torque Depolarizer Test Harness...")
    depolarizer = RollerMillTorqueRippleDepolarizer(mill_id="NAI_MILL_WESTLANDS_04")
    # Generate dummy sinusoidal torque ripple data with noise
    sample_data = [100.0 + 5.0 * math.sin(i * 0.2) + (i % 3) * 0.1 for i in range(128)]
    metrics = depolarizer.process_torque_signal(sample_data, harmonic_order=3)
    print("Execution Metrics Result:", metrics)
    print("Summary telemetry:", depolarizer.get_telemetry_summary())
