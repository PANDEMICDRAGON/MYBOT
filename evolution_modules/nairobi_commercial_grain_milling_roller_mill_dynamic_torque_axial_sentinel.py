"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Axial Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Monitors axial torque telemetry and torsional stress variances on industrial grain milling machinery.
"""

import ast
import logging
import math
import statistics
import time
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillAxialSentinel")


class RollerMillAxialSentinel:
    """
    Analyzes high-frequency axial torque telemetry from roller mill shafts to detect
    imminent mechanical binding, bearing misalignment, or catastrophic shear fatigue.
    """

    def __init__(self, mill_id: str, axial_threshold_nm: float = 450.0):
        self.mill_id = mill_id
        self.axial_threshold_nm = axial_threshold_nm
        self.telemetry_history: List[float] = []
        self.anomaly_count = 0
        logger.info(f"Initialized Axial Sentinel for Roller Mill [{self.mill_id}] at threshold {axial_threshold_nm} Nm.")

    def ingest_reading(self, axial_torque_nm: float) -> Dict[str, any]:
        """
        Ingests a real-time axial torque sensor reading and evaluates structural integrity.
        """
        self.telemetry_history.append(axial_torque_nm)
        if len(self.telemetry_history) > 100:
            self.telemetry_history.pop(0)

        status = "NOMINAL"
        action_required = False

        if abs(axial_torque_nm) > self.axial_threshold_nm:
            self.anomaly_count += 1
            status = "CRITICAL_AXIAL_STRESS"
            action_required = True
            logger.warning(f"[{self.mill_id}] Axial stress anomaly detected! Torque: {axial_torque_nm} Nm")

        # Check for rapid variance (chatter or bearing slip)
        variance = 0.0
        if len(self.telemetry_history) >= 5:
            variance = statistics.variance(self.telemetry_history[-5:])
            if variance > (self.axial_threshold_nm * 0.15):
                status = "WARNING_HIGH_VARIANCE"
                logger.info(f"[{self.mill_id}] High axial torque variance detected: {variance:.2f}")

        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "axial_torque_nm": axial_torque_nm,
            "variance": variance,
            "anomaly_count": self.anomaly_count,
            "status": status,
            "action_required": action_required
        }

    def generate_diagnostic_report(self) -> Dict[str, any]:
        """
        Generates a statistical summary of the milling roller axle health.
        """
        if not self.telemetry_history:
            return {"mill_id": self.mill_id, "status": "NO_DATA"}

        return {
            "mill_id": self.mill_id,
            "samples_analyzed": len(self.telemetry_history),
            "mean_torque": statistics.mean(self.telemetry_history),
            "max_torque": max(self.telemetry_history),
            "min_torque": min(self.telemetry_history),
            "total_anomalies": self.anomaly_count
        }


if __name__ == "__main__":
    # Test Harness
    sentinel = RollerMillAxialSentinel(mill_id="NAI-MILL-04")
    test_readings = [120.5, 125.0, 130.2, 465.8, 122.1, 119.4]
    
    for reading in test_readings:
        result = sentinel.ingest_reading(reading)
        logger.info(f"Test telemetry result: {result}")

    report = sentinel.generate_diagnostic_report()
    logger.info(f"Diagnostic Report: {report}")

    # Validate Python source code with ast.parse
    with open(__file__, "r", encoding="utf-8") as f:
        source_code = f.read()
    ast.parse(source_code)
    logger.info("AST compilation check passed successfully.")
