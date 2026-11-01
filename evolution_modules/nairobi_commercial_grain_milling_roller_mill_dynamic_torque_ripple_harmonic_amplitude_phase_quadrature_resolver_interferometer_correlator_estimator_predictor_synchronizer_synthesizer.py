"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude
Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Synthesizer

Advanced signal processing and quadrature resolver analysis for industrial roller mills.
"""

import math
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicSynthesizer")


class RollerMillHarmonicSynthesizer:
    """
    Computes quadrature phase resolver interferometry and harmonic torque ripple correlation
    for heavy industrial commercial grain milling roller mills.
    """
    def __init__(self, mill_id: str, nominal_rpm: float = 1200.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.history: List[Dict[str, float]] = []

    def process_telemetry(self, raw_torque_samples: List[float], vibration_amplitude: float) -> Dict[str, Any]:
        """
        Analyzes raw torque ripple samples and vibration data using quadrature resolver algorithms.
        """
        if not raw_torque_samples:
            raise ValueError("Raw torque samples cannot be empty.")

        mean_torque = statistics.mean(raw_torque_samples)
        torque_ripple_rms = statistics.stdev(raw_torque_samples) if len(raw_torque_samples) > 1 else 0.0
        
        # Simulated quadrature phase detection (sine/cosine resolver simulation)
        phase_quadrature_vector = [
            math.sin(i * 0.1) * val for i, val in enumerate(raw_torque_samples)
        ]
        interferometer_signal = sum(phase_quadrature_vector) / max(len(phase_quadrature_vector), 1)
        
        harmonic_amplitude = torque_ripple_rms * math.sqrt(2)
        predicted_bearing_stress = harmonic_amplitude * (self.nominal_rpm / 1000.0) + (vibration_amplitude * 1.5)
        
        status = "OPTIMAL"
        if predicted_bearing_stress > 75.0:
            status = "WARNING_HIGH_HARMONIC_STRESS"
        elif predicted_bearing_stress > 110.0:
            status = "CRITICAL_INTERFEROMETER_MISALIGNMENT"

        result = {
            "mill_id": self.mill_id,
            "mean_torque": round(mean_torque, 4),
            "torque_ripple_rms": round(torque_ripple_rms, 4),
            "harmonic_amplitude": round(harmonic_amplitude, 4),
            "interferometer_signal": round(interferometer_signal, 4),
            "predicted_bearing_stress": round(predicted_bearing_stress, 4),
            "status": status
        }
        
        self.history.append(result)
        logger.info(f"Processed mill {self.mill_id} telemetry. Status: {status}")
        return result

    def get_operational_summary(self) -> Dict[str, Any]:
        """
        Returns summary telemetry across all processing cycles.
        """
        if not self.history:
            return {"total_cycles": 0, "average_stress": 0.0}
        avg_stress = statistics.mean([h["predicted_bearing_stress"] for h in self.history])
        return {
            "total_cycles": len(self.history),
            "average_stress": round(avg_stress, 4),
            "last_status": self.history[-1]["status"]
        }


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Harmonic Synthesizer Test Harness...")
    synthesizer = RollerMillHarmonicSynthesizer(mill_id="NAIROBI_MILL_ALPHA_01", nominal_rpm=1250.0)
    sample_torque = [45.2, 48.1, 44.9, 52.3, 47.6, 46.8, 50.1, 43.9]
    telemetry_result = synthesizer.process_telemetry(sample_torque, vibration_amplitude=12.4)
    print("Telemetry Result:", telemetry_result)
    print("Operational Summary:", synthesizer.get_operational_summary())
    print("Evolution Module Executed Successfully.")
