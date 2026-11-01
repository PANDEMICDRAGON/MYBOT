"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Analyzer Module."""

import math
import time
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicAnalyzer")


class RollerMillHarmonicAnalyzer:
    """Analyzes dynamic torque ripple harmonics and quadrature resolver signals in commercial grain roller mills."""

    def __init__(self, mill_id: str, baseline_frequency_hz: float = 50.0):
        self.mill_id = mill_id
        self.baseline_frequency_hz = baseline_frequency_hz
        self.history: List[Dict[str, Any]] = []

    def compute_quadrature_interference(self, sine_wave: List[float], cosine_wave: List[float]) -> Dict[str, float]:
        """Correlates quadrature resolver signals to extract phase quadrature and harmonic amplitude."""
        if not sine_wave or not cosine_wave or len(sine_wave) != len(cosine_wave):
            return {"harmonic_amplitude": 0.0, "phase_quadrature_error": 0.0, "correlation_score": 0.0}

        dot_product = sum(s * c for s, c in zip(sine_wave, cosine_wave))
        norm_s = math.sqrt(sum(s**2 for s in sine_wave))
        norm_c = math.sqrt(sum(c**2 for c in cosine_wave))

        correlation = dot_product / (norm_s * norm_c) if (norm_s * norm_c) > 0 else 0.0
        amplitude = (norm_s + norm_c) / 2.0
        phase_error = math.acos(max(-1.0, min(1.0, correlation))) * (180.0 / math.pi)

        return {
            "harmonic_amplitude": round(amplitude, 4),
            "phase_quadrature_error": round(phase_error, 4),
            "correlation_score": round(correlation, 4)
        }

    def evaluate_torque_ripple(self, torque_samples: List[float]) -> Dict[str, Any]:
        """Estimates and predicts torque ripple anomalies for predictive maintenance."""
        timestamp = time.time()
        if len(torque_samples) < 5:
            return {"status": "insufficient_data", "timestamp": timestamp}

        mean_torque = sum(torque_samples) / len(torque_samples)
        ripple_amplitude = max(torque_samples) - min(torque_samples)
        ripple_factor = ripple_amplitude / mean_torque if mean_torque > 0 else 0.0

        # Synthesize simulated sine and cosine quadrature components from torque samples
        n = len(torque_samples)
        sine_comp = [t * math.sin(2.0 * math.pi * i / n) for i, t in enumerate(torque_samples)]
        cosine_comp = [t * math.cos(2.0 * math.pi * i / n) for i, t in enumerate(torque_samples)]

        quadrature_metrics = self.compute_quadrature_interference(sine_comp, cosine_comp)

        health_status = "OPTIMAL"
        if ripple_factor > 0.25 or quadrature_metrics["phase_quadrature_error"] > 15.0:
            health_status = "WARNING_HARMONIC_DEVIATION"

        analysis_result = {
            "mill_id": self.mill_id,
            "timestamp": timestamp,
            "mean_torque": round(mean_torque, 2),
            "ripple_amplitude": round(ripple_amplitude, 2),
            "ripple_factor": round(ripple_factor, 4),
            "harmonic_amplitude": quadrature_metrics["harmonic_amplitude"],
            "phase_quadrature_error": quadrature_metrics["phase_quadrature_error"],
            "health_status": health_status
        }

        self.history.append(analysis_result)
        return analysis_result


if __name__ == "__main__":
    logger.info("Initializing RollerMillHarmonicAnalyzer test harness for Nairobi Commercial Grain Milling...")
    analyzer = RollerMillHarmonicAnalyzer(mill_id="NAIROBI_ROLLER_MILL_07")
    
    # Simulate roller mill drive torque telemetry samples (Nm)
    sample_torque_data = [120.5, 135.2, 110.1, 142.8, 125.0, 138.4, 115.3, 140.1]
    result = analyzer.evaluate_torque_ripple(sample_torque_data)
    
    logger.info(f"Analysis complete for mill {result['mill_id']}: status={result['health_status']}, ripple_factor={result['ripple_factor']}")
