"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Sentinel"""

import math
import random
import time
from typing import Dict, List, Any


class RollerMillQuadratureSynchronizerSentinel:
    """
    Monitors, correlates, and predicts phase quadrature and harmonic amplitude anomalies
    in Nairobi commercial grain milling roller mill drive spindles using high-frequency
    interferometer telemetry streams.
    """

    def __init__(self, mill_id: str, nominal_rpm: float = 1200.0) -> None:
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.history: List[Dict[str, Any]] = []
        self.active_state = "INITIALIZING"

    def sample_telemetry(self) -> Dict[str, float]:
        """Simulate high-resolution resolver telemetry."""
        t = time.time()
        # Generate synthetic quadrature signals with minor harmonic disturbances
        base_freq = self.nominal_rpm / 60.0
        phase_sin = math.sin(2.0 * math.pi * base_freq * t)
        phase_cos = math.cos(2.0 * math.pi * base_freq * t + 0.002 * random.gauss(0, 1))
        ripple = 0.05 * math.sin(2.0 * math.pi * base_freq * 6.0 * t)
        
        return {
            "timestamp": t,
            "quadrature_sine": phase_sin + ripple,
            "quadrature_cosine": phase_cos,
            "interferometer_phase_error": 0.001 * random.gauss(0, 1) + 0.0005 * ripple,
            "torque_ripple_amplitude": abs(ripple) * 150.0,
        }

    def evaluate_synchronization(self, sample: Dict[str, float]) -> Dict[str, Any]:
        """Correlate phase quadrature and estimate synchronization health."""
        sin_val = sample["quadrature_sine"]
        cos_val = sample["quadrature_cosine"]
        phase_error = sample["interferometer_phase_error"]
        amplitude = sample["torque_ripple_amplitude"]

        # Quadrature orthogonality check: sin^2 + cos^2 should approximate 1.0
        orthogonality_metric = (sin_val ** 2) + (cos_val ** 2)
        deviation = abs(1.0 - orthogonality_metric)

        status = "OPTIMAL"
        if deviation > 0.15 or abs(phase_error) > 0.01:
            status = "PHASE_DRIFT_WARNING"
        if deviation > 0.30 or amplitude > 12.0:
            status = "CRITICAL_HARMONIC_INSTABILITY"

        self.active_state = status
        
        result = {
            "mill_id": self.mill_id,
            "timestamp": sample["timestamp"],
            "orthogonality_metric": round(orthogonality_metric, 4),
            "phase_deviation": round(deviation, 4),
            "harmonic_amplitude": round(amplitude, 4),
            "status": status,
            "compensation_vector": round(-phase_error * 0.75, 5)
        }
        self.history.append(result)
        if len(self.history) > 100:
            self.history.pop(0)
        return result

    def run_diagnostic_cycle(self, iterations: int = 3) -> List[Dict[str, Any]]:
        """Run multiple telemetry and synchronization evaluation cycles."""
        reports = []
        for _ in range(iterations):
            sample = self.sample_telemetry()
            evaluation = self.evaluate_synchronization(sample)
            reports.append(evaluation)
            time.sleep(0.01)
        return reports


if __name__ == "__main__":
    sentinel = RollerMillQuadratureSynchronizerSentinel("NAI-MILL-ALPHA-07")
    diagnostic_results = sentinel.run_diagnostic_cycle(5)
    for res in diagnostic_results:
        print(f"[SENTINEL_EVAL] Mill: {res['mill_id']} | Status: {res['status']} | Phase Deviation: {res['phase_deviation']}")
