"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Rejuvenator Module."""

import math
import logging
import statistics
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillRejuvenator")


class RollerMillRejuvenator:
    """Advanced predictive harmonic resolver and torque ripple synchronizer for Nairobi commercial roller mills."""

    def __init__(self, mill_id: str, nominal_rpm: float = 1200.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.telemetry_history: List[Dict[str, float]] = []

    def ingest_telemetry(self, torque_ripple: float, phase_angle: float, harmonic_amplitude: float) -> None:
        """Ingest real-time sensor measurements from the resolver interferometer."""
        reading = {
            "torque_ripple": torque_ripple,
            "phase_angle": phase_angle,
            "harmonic_amplitude": harmonic_amplitude,
        }
        self.telemetry_history.append(reading)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

    def compute_quadrature_correction(self) -> Dict[str, Any]:
        """Compute phase quadrature adjustments and harmonic suppression parameters."""
        if not self.telemetry_history:
            return {"status": "insufficient_data", "compensation_factor": 1.0}

        recent = self.telemetry_history[-50:]
        ripples = [r["torque_ripple"] for r in recent]
        phases = [r["phase_angle"] for r in recent]
        amplitudes = [r["harmonic_amplitude"] for r in recent]

        mean_ripple = statistics.mean(ripples)
        mean_amplitude = statistics.mean(amplitudes)
        phase_variance = statistics.variance(phases) if len(phases) > 1 else 0.0

        # Mathematical quadrature synchronization model
        quadrature_factor = math.cos(math.radians(statistics.mean(phases)))
        rejuvenation_signal = mean_amplitude * abs(quadrature_factor) * (1.0 + mean_ripple)

        logger.info(f"Mill {self.mill_id}: Rejuvenation signal computed at {rejuvenation_signal:.4f}")

        return {
            "mill_id": self.mill_id,
            "status": "optimized",
            "mean_torque_ripple": mean_ripple,
            "mean_harmonic_amplitude": mean_amplitude,
            "phase_variance": phase_variance,
            "rejuvenation_signal": rejuvenation_signal,
            "action_required": rejuvenation_signal > 0.75,
        }


if __name__ == "__main__":
    rejuvenator = RollerMillRejuvenator(mill_id="NAI_MILL_042")
    # Simulate baseline sensor readings
    for i in range(25):
        rejuvenator.ingest_telemetry(
            torque_ripple=0.12 + (i % 3) * 0.01,
            phase_angle=45.0 + (i % 5) * 0.5,
            harmonic_amplitude=0.30 + (i % 2) * 0.02
        )
    result = rejuvenator.compute_quadrature_correction()
    print("Execution Result:", result)
