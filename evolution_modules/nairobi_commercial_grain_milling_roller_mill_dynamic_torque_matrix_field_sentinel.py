"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Field Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [TorqueMatrixField]: %(message)s')
logger = logging.getLogger("TorqueMatrixFieldSentinel")

class RollerMillTorqueMatrixSentinel:
    """
    Monitors spatial and temporal torque matrices across paired grinding rollers
    in commercial roller mills to detect anomalies before mechanical failure.
    """
    def __init__(self, mill_id: str, matrix_dim: int = 4):
        self.mill_id = mill_id
        self.matrix_dim = matrix_dim
        self.torque_matrix: List[List[float]] = [[0.0 for _ in range(matrix_dim)] for _ in range(matrix_dim)]
        self.baseline_matrix: List[List[float]] = [[100.0 for _ in range(matrix_dim)] for _ in range(matrix_dim)]
        self.anomaly_threshold = 25.0  # percentage deviation
        self.health_status = "NOMINAL"
        logger.info(f"Initialized Torque Matrix Field Sentinel for mill {mill_id} with {matrix_dim}x{matrix_dim} topology.")

    def ingest_sensor_readings(self, readings: List[List[float]]) -> None:
        """Ingests a 2D matrix of torque telemetry values from the roller motor drives."""
        if len(readings) != self.matrix_dim or any(len(row) != self.matrix_dim for row in readings):
            raise ValueError(f"Readings dimensions must match {self.matrix_dim}x{self.matrix_dim}")
        self.torque_matrix = readings
        self._evaluate_matrix_field()

    def _evaluate_matrix_field(self) -> None:
        """Evaluates spatial stress variance across the matrix field."""
        max_deviation = 0.0
        for r in range(self.matrix_dim):
            for c in range(self.matrix_dim):
                base = self.baseline_matrix[r][c]
                current = self.torque_matrix[r][c]
                deviation = abs(current - base) / base * 100.0
                if deviation > max_deviation:
                    max_deviation = deviation

        if max_deviation > self.anomaly_threshold * 1.5:
            self.health_status = "CRITICAL"
            logger.error(f"[{self.mill_id}] CRITICAL STRESS VARIANCE: {max_deviation:.2f}% deviation detected!")
        elif max_deviation > self.anomaly_threshold:
            self.health_status = "WARNING"
            logger.warning(f"[{self.mill_id}] Warning stress variance: {max_deviation:.2f}% deviation detected.")
        else:
            self.health_status = "NOMINAL"

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "health_status": self.health_status,
            "matrix_dim": self.matrix_dim,
            "current_matrix": self.torque_matrix
        }

if __name__ == "__main__":
    logger.info("Executing test harness for RollerMillTorqueMatrixSentinel...")
    sentinel = RollerMillTorqueMatrixSentinel(mill_id="MILL-NAI-04")
    
    # Simulate normal operation
    normal_readings = [
        [101.2, 99.8, 100.1, 100.5],
        [99.9, 100.4, 101.0, 99.5],
        [100.2, 100.1, 99.8, 100.3],
        [99.7, 100.2, 100.5, 100.0]
    ]
    sentinel.ingest_sensor_readings(normal_readings)
    logger.info(f"Status after normal readings: {sentinel.get_diagnostics()['health_status']}")

    # Simulate anomalous torque spike (e.g., foreign metal fragment entering roll gap)
    anomaly_readings = [
        [101.2, 99.8, 100.1, 100.5],
        [99.9, 145.0, 101.0, 99.5],
        [100.2, 100.1, 138.5, 100.3],
        [99.7, 100.2, 100.5, 100.0]
    ]
    sentinel.ingest_sensor_readings(anomaly_readings)
    logger.info(f"Status after anomaly readings: {sentinel.get_diagnostics()['health_status']}")
    logger.info("Test harness completed successfully.")
