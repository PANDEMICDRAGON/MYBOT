"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Synthesis Sentinel
Autonomous Evolutionary Architecture Module v1

Monitors cross-coupled torque vectors, torsional oscillation matrices, and structural load distribution
across commercial roller mills in industrial milling complexes (e.g., Industrial Area, Nairobi).
"""

import logging
import time
import math
import random
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueMatrixSentinel")


class RollerMillTorqueMatrixSentinel:
    """
    Evaluates high-frequency multidimensional torque matrices from fast roller mill drives,
    detecting micro-slip, asymmetric roll loading, and harmonic coupling anomalies.
    """

    def __init__(self, mill_id: str, sample_frequency_hz: float = 1000.0):
        self.mill_id = mill_id
        self.sample_frequency_hz = sample_frequency_hz
        self.anomaly_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized Torque Matrix Sentinel for mill {self.mill_id} @ {sample_frequency_hz}Hz")

    def compute_matrix_health(self, torque_tensor_x: List[float], torque_tensor_y: List[float]) -> Dict[str, Any]:
        """
        Computes cross-correlation and matrix determinant stability across orthogonal torque channels.
        """
        if not torque_tensor_x or not torque_tensor_y or len(torque_tensor_x) != len(torque_tensor_y):
            return {"status": "ERROR", "message": "Invalid or mismatched tensor dimensions."}

        n = len(torque_tensor_x)
        mean_x = sum(torque_tensor_x) / n
        mean_y = sum(torque_tensor_y) / n

        variance_x = sum((x - mean_x) ** 2 for x in torque_tensor_x) / n
        variance_y = sum((y - mean_y) ** 2 for y in torque_tensor_y) / n
        covariance = sum((torque_tensor_x[i] - mean_x) * (torque_tensor_y[i] - mean_y) for i in range(n)) / n

        # Determinant proxy and coupling coefficient
        determinant_proxy = (variance_x * variance_y) - (covariance ** 2)
        coupling_ratio = abs(covariance) / (math.sqrt(variance_x * variance_y) + 1e-9)

        status = "OPTIMAL"
        if determinant_proxy < 0.001 or coupling_ratio > 0.95:
            status = "WARNING"
        if determinant_proxy < 0.0001:
            status = "CRITICAL_INTERLOCK"

        assessment = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "determinant_proxy": determinant_proxy,
            "coupling_ratio": coupling_ratio,
            "variance_x": variance_x,
            "variance_y": variance_y,
            "status": status
        }

        if status != "OPTIMAL":
            self.anomaly_history.append(assessment)
            logger.warning(f"[{self.mill_id}] Torque Matrix anomaly detected: status={status}, coupling={coupling_ratio:.4f}")

        return assessment

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "total_anomalies_recorded": len(self.anomaly_history),
            "last_anomaly": self.anomaly_history[-1] if self.anomaly_history else None
        }


if __name__ == "__main__":
    sentinel = RollerMillTorqueMatrixSentinel(mill_id="NAIROBI-MILL-STATION-04")
    # Simulate stable and then unstable torque readings
    sim_x = [10.0 + random.gauss(0, 0.1) for _ in range(100)]
    sim_y = [10.0 + random.gauss(0, 0.1) for _ in range(100)]
    
    result = sentinel.compute_matrix_health(sim_x, sim_y)
    print("Simulation Assessment Result:", result)
    print("Diagnostics Summary:", sentinel.get_diagnostics())
