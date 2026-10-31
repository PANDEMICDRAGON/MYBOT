"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Unity Sentinel.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
Description: Proactively monitors, aggregates, and analyzes dynamic torsional telemetry matrices
             across multi-roller milling lines in Nairobi commercial grain complexes to prevent
             drivetrain fatigue, harmonic resonance degradation, and catastrophic seizures.
"""

import ast
import logging
import statistics
import time
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("RollerMillTorqueMatrixUnitySentinel")

class RollerMillTorqueMatrixUnitySentinel:
    """Aggregates multi-axis torque telemetry vectors and computes holistic matrix unity scores."""

    def __init__(self, mill_id: str, torque_threshold_nm: float = 1450.0):
        self.mill_id = mill_id
        self.torque_threshold_nm = torque_threshold_nm
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillTorqueMatrixUnitySentinel for mill: {self.mill_id}")

    def ingest_telemetry_frame(self, roller_node: str, torque_nm: float, vibration_mm_s: float, temperature_c: float) -> Dict[str, Any]:
        """Ingests a real-time telemetry frame from a specific roller mill node."""
        timestamp = time.time()
        frame = {
            "timestamp": timestamp,
            "roller_node": roller_node,
            "torque_nm": torque_nm,
            "vibration_mm_s": vibration_mm_s,
            "temperature_c": temperature_c
        }
        self.telemetry_history.append(frame)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
        return frame

    def evaluate_matrix_unity(self) -> Dict[str, Any]:
        """Calculates statistical unity, anomaly states, and operational health coefficients."""
        if not self.telemetry_history:
            return {"status": "IDLE", "unity_score": 1.0, "recommendation": "Awaiting telemetry."}

        torques = [f["torque_nm"] for f in self.telemetry_history]
        vibrations = [f["vibration_mm_s"] for f in self.telemetry_history]
        temperatures = [f["temperature_c"] for f in self.telemetry_history]

        mean_torque = statistics.mean(torques)
        max_torque = max(torques)
        stdev_torque = statistics.stdev(torques) if len(torques) > 1 else 0.0

        unity_score = max(0.0, 1.0 - (max_torque / (self.torque_threshold_nm * 1.5)))

        status = "OPTIMAL"
        recommendation = "All roller torque matrices operating within nominal parameters."

        if max_torque > self.torque_threshold_nm:
            status = "CRITICAL_TORQUE_SPIKE"
            recommendation = "Immediate feed restriction and clutch decoupling advised."
        elif stdev_torque > (self.torque_threshold_nm * 0.2):
            status = "HARMONIC_INSTABILITY"
            recommendation = "Inspect drive belt tension and roller parallel alignment."

        return {
            "mill_id": self.mill_id,
            "status": status,
            "unity_score": round(unity_score, 4),
            "mean_torque_nm": round(mean_torque, 2),
            "max_torque_nm": round(max_torque, 2),
            "stdev_torque": round(stdev_torque, 2),
            "mean_vibration": round(statistics.mean(vibrations), 2),
            "mean_temperature_c": round(statistics.mean(temperatures), 2),
            "recommendation": recommendation
        }

def test_sentinel():
    sentinel = RollerMillTorqueMatrixUnitySentinel(mill_id="NAIROBI_MILL_ALPHA_04")
    sentinel.ingest_telemetry_frame("ROLL_A1", 1100.5, 1.2, 65.4)
    sentinel.ingest_telemetry_frame("ROLL_A2", 1250.0, 1.5, 68.1)
    sentinel.ingest_telemetry_frame("ROLL_B1", 1420.2, 2.1, 72.0)
    
    report = sentinel.evaluate_matrix_unity()
    assert report["mill_id"] == "NAIROBI_MILL_ALPHA_04"
    logger.info(f"Test telemetry matrix report generated: {report}")

if __name__ == "__main__":
    test_sentinel()
    source_code = open(__file__).read()
    ast.parse(source_code)
    logger.info("AST compilation check passed successfully.")
