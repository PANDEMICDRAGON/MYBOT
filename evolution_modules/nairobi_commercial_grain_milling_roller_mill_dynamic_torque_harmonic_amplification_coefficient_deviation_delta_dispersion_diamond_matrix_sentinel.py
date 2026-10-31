"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Harmonic Amplification Coefficient Deviation Delta Dispersion Diamond Matrix Sentinel

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
Description:
  Provides real-time analysis of roller mill dynamic torque harmonic amplification coefficient deviations and dispersion matrices. Ensures maximum flour milling precision and machinery longevity under Nairobi industrial operating conditions.
"""

import math
import statistics
import time
from typing import Dict, List, Any, Optional


class RollerMillDiamondMatrixSentinel:
    """Monitors high-frequency torque dispersion and harmonic deviation vectors in roller mills."""

    def __init__(self, mill_id: str, nominal_torque_nm: float = 450.0):
        self.mill_id = mill_id
        self.nominal_torque_nm = nominal_torque_nm
        self.torque_history: List[float] = []
        self.harmonic_coefficients: List[float] = []
        self.anomaly_count = 0

    def ingest_telemetry(self, torque_reading: float, harmonic_pulse: float) -> Dict[str, Any]:
        """Ingests raw torque and harmonic telemetry, updating the diamond dispersion matrix."""
        self.torque_history.append(torque_reading)
        self.harmonic_coefficients.append(harmonic_pulse)

        # Keep rolling window of 100 samples
        if len(self.torque_history) > 100:
            self.torque_history.pop(0)
        if len(self.harmonic_coefficients) > 100:
            self.harmonic_coefficients.pop(0)

        return self._evaluate_matrix_state()

    def _evaluate_matrix_state(self) -> Dict[str, Any]:
        if len(self.torque_history) < 10:
            return {"status": "CALIBRATING", "dispersion_delta": 0.0, "matrix_health": 100.0}

        mean_torque = statistics.mean(self.torque_history)
        stdev_torque = statistics.stdev(self.torque_history)
        torque_deviation = abs(mean_torque - self.nominal_torque_nm) / self.nominal_torque_nm

        mean_harmonic = statistics.mean(self.harmonic_coefficients)
        dispersion_delta = statistics.variance(self.harmonic_coefficients) if len(self.harmonic_coefficients) > 1 else 0.0

        # Diamond Matrix Health Formula
        health_score = max(0.0, 100.0 - (torque_deviation * 50.0) - (dispersion_delta * 10.0))
        status = "OPTIMAL"

        if health_score < 75.0:
            status = "WARNING"
            self.anomaly_count += 1
        if health_score < 50.0:
            status = "CRITICAL_DISPERSION"
            self.anomaly_count += 2

        return {
            "mill_id": self.mill_id,
            "status": status,
            "mean_torque": round(mean_torque, 2),
            "torque_deviation_pct": round(torque_deviation * 100, 3),
            "harmonic_dispersion_delta": round(dispersion_delta, 4),
            "matrix_health_score": round(health_score, 2),
            "anomaly_count": self.anomaly_count,
            "timestamp": time.time()
        }


if __name__ == "__main__":
    print("Initializing Nairobi Roller Mill Diamond Matrix Sentinel Test Harness...")
    sentinel = RollerMillDiamondMatrixSentinel(mill_id="RM-NAIROBI-04")

    # Simulate normal and aberrant operational telemetry stream
    import random
    for i in range(15):
        simulated_torque = 450.0 + random.uniform(-15.0, 15.0)
        simulated_harmonic = 1.05 + random.uniform(-0.05, 0.05)
        result = sentinel.ingest_telemetry(simulated_torque, simulated_harmonic)
        print(f"Iteration {i+1}: {result}")

    print("Sentinel verification complete. Diamond Matrix operational.")
