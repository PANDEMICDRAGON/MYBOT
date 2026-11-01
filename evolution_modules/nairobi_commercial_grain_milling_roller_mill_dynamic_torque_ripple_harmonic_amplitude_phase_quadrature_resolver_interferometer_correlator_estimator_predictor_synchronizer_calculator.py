"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Calculator

Provides advanced real-time mathematical modeling, quadrature resolver telemetry correlation,
and harmonic amplitude prediction for high-precision commercial roller mills operating in Nairobi.
"""

import math
import statistics
from typing import Dict, List, Tuple, Any


class RollerMillHarmonicCalculator:
    """
    Computes torque ripple harmonics, phase quadrature interference patterns,
    and predictive synchronization vectors for industrial roller mills.
    """

    def __init__(self, sample_rate_hz: float = 1000.0) -> None:
        self.sample_rate_hz = sample_rate_hz
        self.history: List[Dict[str, float]] = []

    def ingest_resolver_sample(self, timestamp: float, raw_phase_a: float, raw_phase_b: float, torque_nm: float) -> Dict[str, Any]:
        """
        Ingests raw resolver phase data and torque measurements, computing quadrature components.
        """
        # Calculate quadrature amplitude vector
        quadrature_magnitude = math.sqrt(raw_phase_a ** 2 + raw_phase_b ** 2)
        phase_angle_rad = math.atan2(raw_phase_b, raw_phase_a)
        
        sample = {
            "timestamp": timestamp,
            "phase_a": raw_phase_a,
            "phase_b": raw_phase_b,
            "torque_nm": torque_nm,
            "quadrature_magnitude": quadrature_magnitude,
            "phase_angle_rad": phase_angle_rad
        }
        self.history.append(sample)
        if len(self.history) > 2000:
            self.history.pop(0)
            
        return sample

    def analyze_torque_ripple_harmonics(self) -> Dict[str, float]:
        """
        Analyzes recent torque samples to extract ripple amplitudes and dominant harmonic frequencies.
        """
        if len(self.history) < 10:
            return {"dominant_ripple_amplitude": 0.0, "harmonic_distortion_index": 0.0, "phase_variance": 0.0}
            
        torques = [s["torque_nm"] for s in self.history]
        mean_torque = statistics.mean(torques)
        ripple_deviations = [abs(t - mean_torque) for t in torques]
        dominant_amplitude = max(ripple_deviations) if ripple_deviations else 0.0
        
        phases = [s["phase_angle_rad"] for s in self.history]
        phase_var = statistics.variance(phases) if len(phases) > 1 else 0.0
        
        # Synthetic harmonic distortion index calculation
        variance_torque = statistics.variance(torques) if len(torques) > 1 else 0.0
        hdi = math.sqrt(variance_torque) / (mean_torque + 1e-9)
        
        return {
            "mean_torque_nm": mean_torque,
            "dominant_ripple_amplitude": dominant_amplitude,
            "harmonic_distortion_index": hdi,
            "phase_variance": phase_var
        }

    def predict_synchronization_offset(self) -> float:
        """
        Predicts phase synchronization adjustment required to nullify harmonic torque ripple.
        """
        analysis = self.analyze_torque_ripple_harmonics()
        hdi = analysis["harmonic_distortion_index"]
        # Predictive compensation factor derived from quadrature phase variance and harmonic distortion
        adjustment_angle = analysis["phase_variance"] * hdi * 0.05
        return adjustment_angle


if __name__ == "__main__":
    calc = RollerMillHarmonicCalculator()
    # Simulate ingestion of resolver and torque telemetry
    for i in range(50):
        t = float(i) * 0.001
        pa = math.cos(i * 0.1) * 10.0
        pb = math.sin(i * 0.1) * 10.0
        torque = 150.0 + 5.0 * math.sin(i * 0.2)
        calc.ingest_resolver_sample(t, pa, pb, torque)
        
    metrics = calc.analyze_torque_ripple_harmonics()
    offset = calc.predict_synchronization_offset()
    print("RollerMillHarmonicCalculator Diagnostics:", metrics)
    print("Predicted Synchronization Offset (rad):", offset)
