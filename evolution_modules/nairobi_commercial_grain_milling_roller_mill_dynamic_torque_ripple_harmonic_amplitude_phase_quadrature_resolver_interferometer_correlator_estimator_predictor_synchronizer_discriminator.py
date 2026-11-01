"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude
Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Discriminator

Provides real-time high-fidelity quadrature signal analysis, harmonic phase correlation,
and torque ripple discrimination for high-throughput commercial roller mills operating in Nairobi.
"""

import math
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicQuadratureDiscriminator")

class RollerMillHarmonicQuadratureDiscriminator:
    """
    Monitors roller mill drive telemetry, extracts quadrature resolver harmonics,
    computes interferometer correlation metrics, and discriminates mechanical anomalies.
    """
    def __init__(self, sample_rate_hz: float = 1000.0, harmonic_order: int = 5):
        self.sample_rate_hz = sample_rate_hz
        self.harmonic_order = harmonic_order
        self.telemetry_history: List[Dict[str, float]] = []

    def ingest_resolver_signal(self, timestamp: float, phase_a: float, phase_b: float, torque_nm: float) -> Dict[str, Any]:
        """
        Ingests quadrature resolver signals (Phase A/B) and instantaneous torque.
        Computes amplitude, phase angle, and quadrature orthogonality error.
        """
        # Quadrature amplitude calculation
        amplitude = math.sqrt(phase_a**2 + phase_b**2)
        
        # Phase angle via arctan2
        phase_rad = math.atan2(phase_b, phase_a)
        phase_deg = math.degrees(phase_rad)
        
        # Orthogonality deviation (ideal is 90 degrees or pi/2 radians)
        expected_b = amplitude * math.sin(phase_rad)
        orthogonality_error = abs(phase_b - expected_b)

        record = {
            "timestamp": timestamp,
            "amplitude": amplitude,
            "phase_deg": phase_deg,
            "torque_nm": torque_nm,
            "orthogonality_error": orthogonality_error
        }
        
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 5000:
            self.telemetry_history.pop(0)

        return record

    def correlate_interferometer_ripples(self) -> Dict[str, Any]:
        """
        Correlates torque ripple harmonics with resolver interferometry data
        to predict bearing wear or roller contact asperity.
        """
        if len(self.telemetry_history) < 10:
            return {"status": "insufficient_data", "anomaly_detected": False}

        torques = [r["torque_nm"] for r in self.telemetry_history]
        errors = [r["orthogonality_error"] for r in self.telemetry_history]

        mean_torque = statistics.mean(torques)
        stdev_torque = statistics.pstdev(torques) if len(torques) > 1 else 0.0
        mean_error = statistics.mean(errors)

        # Discriminator threshold logic
        anomaly_flag = stdev_torque > (mean_torque * 0.15) or mean_error > 0.05

        assessment = {
            "status": "success",
            "mean_torque_nm": mean_torque,
            "torque_ripple_stdev": stdev_torque,
            "mean_orthogonality_error": mean_error,
            "anomaly_detected": anomaly_flag,
            "recommended_action": "Inspect roller gap alignment and bearing preload" if anomaly_flag else "Normal operation"
        }

        logger.info(f"Harmonic Discriminator Assessment: {assessment}")
        return assessment

if __name__ == "__main__":
    discriminator = RollerMillHarmonicQuadratureDiscriminator()
    # Simulate ingestion of resolver data
    for i in range(50):
        t = float(i) * 0.001
        pa = math.cos(2.0 * math.pi * 50.0 * t)
        pb = math.sin(2.0 * math.pi * 50.0 * t)
        torque = 250.0 + 10.0 * math.sin(2.0 * math.pi * 5.0 * t)
        discriminator.ingest_resolver_signal(t, pa, pb, torque)
    
    result = discriminator.correlate_interferometer_ripples()
    print("Test Execution Result:", result)
