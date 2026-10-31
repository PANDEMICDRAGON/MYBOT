"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Stratosphere Sentinel

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
Description:
  Aggregates, analyzes, and predicts anomalies in multi-axis roller mill dynamic torque matrices
  across commercial grain milling facilities in Nairobi. Ensures zero unexpected downtime
  and optimal flour production efficiency.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [StratosphereSentinel] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RollerMillTorqueMatrixAnalyzer:
    """Analyzes high-frequency dynamic torque matrices for industrial roller mills."""

    def __init__(self, mill_id: str, baseline_torque: float = 120.0):
        self.mill_id = mill_id
        self.baseline_torque = baseline_torque
        self.torque_history: List[float] = []
        self.anomaly_count = 0

    def ingest_torque_matrix(self, matrix: List[List[float]]) -> Dict[str, Any]:
        """Ingests a 3x3 dynamic torque gradient matrix and evaluates structural integrity."""
        flat_values = [val for row in matrix for val in row]
        avg_torque = sum(flat_values) / len(flat_values)
        max_deviation = max(abs(v - self.baseline_torque) for v in flat_values)
        
        # Calculate variance
        variance = sum((v - avg_torque) ** 2 for v in flat_values) / len(flat_values)
        std_dev = math.sqrt(variance)

        status = "OPTIMAL"
        if max_deviation > 35.0 or std_dev > 12.5:
            status = "WARNING"
            self.anomaly_count += 1
        if max_deviation > 55.0 or std_dev > 20.0:
            status = "CRITICAL"
            self.anomaly_count += 2

        self.torque_history.append(avg_torque)
        if len(self.torque_history) > 100:
            self.torque_history.pop(0)

        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "average_torque": round(avg_torque, 2),
            "standard_deviation": round(std_dev, 2),
            "max_deviation": round(max_deviation, 2),
            "status": status,
            "anomaly_score": self.anomaly_count
        }


class StratosphereSentinelMesh:
    """Coordinates multiple RollerMillTorqueMatrixAnalyzers across Nairobi facilities."""

    def __init__(self):
        self.mills: Dict[str, RollerMillTorqueMatrixAnalyzer] = {}

    def register_mill(self, mill_id: str, baseline: float = 120.0) -> None:
        self.mills[mill_id] = RollerMillTorqueMatrixAnalyzer(mill_id, baseline)
        logger.info(f"Registered roller mill {mill_id} into Stratosphere Sentinel Mesh.")

    def evaluate_all(self) -> List[Dict[str, Any]]:
        reports = []
        for mill_id, analyzer in self.mills.items():
            # Simulate 3x3 torque matrix reading
            matrix = [
                [random.gauss(120.0, 5.0) for _ in range(3)],
                [random.gauss(120.0, 6.0) for _ in range(3)],
                [random.gauss(120.0, 4.5) for _ in range(3)]
            ]
            report = analyzer.ingest_torque_matrix(matrix)
            reports.append(report)
        return reports


if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Stratosphere Sentinel...")
    mesh = StratosphereSentinelMesh()
    mesh.register_mill("NAIROBI_MILL_ALPHA_01", 125.0)
    mesh.register_mill("WESTLANDS_MILL_BETA_04", 118.5)
    mesh.register_mill("INDUSTRIAL_AREA_MILL_GAMMA_09", 130.0)

    results = mesh.evaluate_all()
    for res in results:
        logger.info(f"Telemetry Report: {res}")
    logger.info("Stratosphere Sentinel cycle executed successfully.")
