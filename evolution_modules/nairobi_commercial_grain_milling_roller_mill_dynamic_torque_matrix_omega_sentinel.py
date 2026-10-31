"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Omega Sentinel
Autonomous Evolutionary Architecture Module for Industrial Roller Mill Health & Telemetry
"""

import os
import time
import logging
import json
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillOmegaSentinel")

class RollerMillOmegaSentinel:
    """
    Monitors multi-axis torque matrices on commercial grain milling roller mills,
    detecting harmonic aberrations, load imbalances, and potential mechanical failure vectors.
    """
    def __init__(self, mill_id: str, torque_tolerance_nm: float = 45.0):
        self.mill_id = mill_id
        self.torque_tolerance_nm = torque_tolerance_nm
        self.anomaly_log: List[Dict[str, Any]] = []

    def analyze_torque_matrix(self, matrix_readings: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyzes incoming torque matrix coordinates (e.g., drive-end, non-drive-end, axial, radial).
        """
        timestamp = time.time()
        status = "OPTIMAL"
        max_deviation = 0.0

        for axis, torque in matrix_readings.items():
            deviation = abs(torque - self.torque_tolerance_nm)
            if deviation > max_deviation:
                max_deviation = deviation

            if deviation > (self.torque_tolerance_nm * 0.35):
                status = "CRITICAL_ANOMALY"
                alert = {
                    "timestamp": timestamp,
                    "mill_id": self.mill_id,
                    "axis": axis,
                    "torque_nm": torque,
                    "deviation": deviation,
                    "message": f"Torque aberration detected on axis {axis} for mill {self.mill_id}!"
                }
                self.anomaly_log.append(alert)
                logger.warning(json.dumps(alert))

        return {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "status": status,
            "max_deviation": max_deviation,
            "anomalies_recorded": len(self.anomaly_log)
        }

    def get_telemetry_report(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "total_anomalies": len(self.anomaly_log),
            "log": self.anomaly_log[-5:]
        }

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Omega Sentinel...")
    sentinel = RollerMillOmegaSentinel(mill_id="NAI-MILL-042")
    
    # Simulate normal and anomalous readings
    readings_normal = {"axial": 44.5, "radial_left": 45.1, "radial_right": 44.9}
    readings_anomaly = {"axial": 72.3, "radial_left": 45.2, "radial_right": 48.0}
    
    print("Test 1 (Normal):", sentinel.analyze_torque_matrix(readings_normal))
    print("Test 2 (Anomaly):", sentinel.analyze_torque_matrix(readings_anomaly))
    print("Telemetry Report:", json.dumps(sentinel.get_telemetry_report(), indent=2))
    print("Omega Sentinel execution completed successfully.")
