"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Sentinel

Analyzes cross-coupled torque matrices between fast and slow rolls in commercial
roller mills across Nairobi milling facilities to optimize extraction rates and prevent mechanical failure.
"""

import math
import statistics
import time
from typing import Dict, List, Any


class RollerMillTorqueMatrixSentinel:
    """Monitors and evaluates multi-axis torque cross-coupling matrices in roller mills."""

    def __init__(self, mill_id: str, threshold_matrix_deviation: float = 0.15):
        self.mill_id = mill_id
        self.threshold = threshold_matrix_deviation
        self.telemetry_history: List[Dict[str, float]] = []

    def ingest_torque_matrix(self, fast_roll_torque: float, slow_roll_torque: float, differential_speed: float) -> Dict[str, Any]:
        """Ingests dual-roll torque metrics and calculates cross-coupling interaction indices."""
        timestamp = time.time()
        ratio = slow_roll_torque / (fast_roll_torque + 1e-6)
        matrix_energy = math.sqrt(fast_roll_torque**2 + slow_roll_torque**2)
        interaction_index = abs(ratio - 1.25) * differential_speed

        record = {
            "timestamp": timestamp,
            "fast_roll_torque": fast_roll_torque,
            "slow_roll_torque": slow_roll_torque,
            "torque_ratio": ratio,
            "matrix_energy": matrix_energy,
            "interaction_index": interaction_index
        }

        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        anomaly_detected = interaction_index > self.threshold

        return {
            "mill_id": self.mill_id,
            "status": "WARNING_MATRIX_DEVIATION" if anomaly_detected else "OPTIMAL",
            "interaction_index": interaction_index,
            "matrix_energy": matrix_energy,
            "torque_ratio": ratio,
            "timestamp": timestamp
        }

    def diagnostic_summary(self) -> Dict[str, Any]:
        """Generates summary telemetry across historical ingestion cycles."""
        if not self.telemetry_history:
            return {"status": "NO_DATA"}

        indices = [r["interaction_index"] for r in self.telemetry_history]
        energies = [r["matrix_energy"] for r in self.telemetry_history]

        return {
            "mill_id": self.mill_id,
            "samples_analyzed": len(self.telemetry_history),
            "mean_interaction_index": statistics.mean(indices),
            "peak_matrix_energy": max(energies),
            "sentinel_status": "ARMED"
        }


if __name__ == "__main__":
    sentinel = RollerMillTorqueMatrixSentinel(mill_id="NAIROBI_MILL_ALPHA_04")
    print("Initializing RollerMillTorqueMatrixSentinel for Nairobi Operations...")
    
    # Simulate healthy and anomalous readings
    test_samples = [
        (45.0, 36.0, 1.25),
        (46.2, 36.8, 1.25),
        (78.5, 30.1, 1.90)  # Should trigger anomaly
    ]
    
    for fast, slow, diff in test_samples:
        res = sentinel.ingest_torque_matrix(fast, slow, diff)
        print(f"-> Ingested: {res}")
        
    print("Diagnostic Summary:", sentinel.diagnostic_summary())
