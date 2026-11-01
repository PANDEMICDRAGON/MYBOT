"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Investigator Module."""

import math
import time
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillInterferometerInvestigator")

class RollerMillTorqueInvestigator:
    """Performs quadrature resolver interferometry on roller mill torque ripple harmonics."""

    def __init__(self, mill_id: str, base_frequency_hz: float = 50.0):
        self.mill_id = mill_id
        self.base_frequency_hz = base_frequency_hz
        self.history: List[Dict[str, Any]] = []

    def measure_phase_quadrature(self, raw_torque_samples: List[float]) -> Dict[str, float]:
        """Compute harmonic amplitude and phase quadrature using simulated interferometer correlation."""
        if not raw_torque_samples:
            return {"amplitude": 0.0, "phase_quadrature": 0.0, "anomaly_score": 0.0}

        n = len(raw_torque_samples)
        mean_torque = sum(raw_torque_samples) / n
        
        # Compute fundamental harmonic components
        cos_sum = sum(val * math.cos(2 * math.pi * i / n) for i, val in enumerate(raw_torque_samples))
        sin_sum = sum(val * math.sin(2 * math.pi * i / n) for i, val in enumerate(raw_torque_samples))
        
        amplitude = math.sqrt(cos_sum**2 + sin_sum**2) / (n / 2)
        phase = math.atan2(sin_sum, cos_sum)
        
        # Variance as anomaly score indicator
        variance = sum((x - mean_torque) ** 2 for x in raw_torque_samples) / n
        anomaly_score = variance / (mean_torque + 1e-9)

        metrics = {
            "timestamp": time.time(),
            "mean_torque": mean_torque,
            "amplitude": amplitude,
            "phase_quadrature": phase,
            "anomaly_score": anomaly_score
        }
        self.history.append(metrics)
        return metrics

    def investigate_and_predict(self, samples: List[float]) -> Dict[str, Any]:
        metrics = self.measure_phase_quadrature(samples)
        status = "OPTIMAL"
        if metrics["anomaly_score"] > 0.75:
            status = "CRITICAL_HARMONIC_DEVIATION"
        elif metrics["anomaly_score"] > 0.40:
            status = "WARNING_ELEVATED_RIPPLE"

        report = {
            "mill_id": self.mill_id,
            "status": status,
            "metrics": metrics,
            "recommendation": "Inspect roller bearing clearance and inverter sync" if status != "OPTIMAL" else "No action required"
        }
        logger.info(f"Investigated mill {self.mill_id}: status={status}, anomaly_score={metrics['anomaly_score']:.4f}")
        return report

if __name__ == "__main__":
    investigator = RollerMillTorqueInvestigator(mill_id="NAIROBI_MILL_04_UGALI")
    mock_samples = [10.2 + math.sin(i * 0.2) * 1.5 + (0.5 if i % 7 == 0 else 0) for i in range(100)]
    report = investigator.investigate_and_predict(mock_samples)
    print("Execution Result:", report)
