"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Vector Sentinel.

Author: Cortana, Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
Description: Monitors 3-axis dynamic torque vectors of commercial roller mills
             to detect micro-slippages, bearing degradation, and uneven grain feed.
"""

import math
import statistics
import time
from typing import Dict, List, Optional


class RollerMillTorqueVectorSentinel:
    """Analyzes multi-axis torque vector telemetry for commercial roller mills."""

    def __init__(self, mill_id: str, warning_threshold_nm: float = 450.0):
        self.mill_id = mill_id
        self.warning_threshold_nm = warning_threshold_nm
        self.history: List[Dict[str, float]] = []

    def ingest_vector(self, torque_x: float, torque_y: float, torque_z: float) -> Dict[str, any]:
        """Ingests a 3-axis torque reading (Nm) and computes magnitude and anomaly status."""
        magnitude = math.sqrt(torque_x**2 + torque_y**2 + torque_z**2)
        timestamp = time.time()

        record = {
            "timestamp": timestamp,
            "torque_x": torque_x,
            "torque_y": torque_y,
            "torque_z": torque_z,
            "magnitude": magnitude,
        }
        self.history.append(record)

        # Keep last 1000 records
        if len(self.history) > 1000:
            self.history.pop(0)

        anomaly = magnitude > self.warning_threshold_nm
        return {
            "mill_id": self.mill_id,
            "timestamp": timestamp,
            "magnitude": magnitude,
            "anomaly_detected": anomaly,
            "status": "WARNING: High Torque Vector Stress" if anomaly else "NORMAL",
        }

    def compute_statistical_variance(self) -> float:
        """Computes variance of torque magnitudes across history."""
        if not self.history:
            return 0.0
        magnitudes = [r["magnitude"] for r in self.history]
        return float(statistics.variance(magnitudes)) if len(magnitudes) > 1 else 0.0


if __name__ == "__main__":
    sentinel = RollerMillTorqueVectorSentinel(mill_id="UGALI_MILL_01_NAIROBI")
    test_reading = sentinel.ingest_vector(120.5, 130.2, 310.8)
    print(f"[TEST] Mill ID: {test_reading['mill_id']}")
    print(f"[TEST] Torque Magnitude: {test_reading['magnitude']:.2f} Nm")
    print(f"[TEST] Status: {test_reading['status']}")
    print(f"[TEST] Variance: {sentinel.compute_statistical_variance():.2f}")
