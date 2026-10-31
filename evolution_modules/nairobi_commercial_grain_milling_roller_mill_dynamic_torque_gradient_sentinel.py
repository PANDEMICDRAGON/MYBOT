"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Gradient Sentinel. pydantic-free implementation."""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TorqueGradientSentinel")


class RollerMillTorqueGradientAnalyzer:
    """Monitors high-frequency torque gradient changes on commercial roller mill drives."""

    def __init__(self, mill_id: str, max_allowable_gradient: float = 45.0):
        self.mill_id = mill_id
        self.max_allowable_gradient = max_allowable_gradient
        self.history: List[Dict[str, Any]] = []
        self.anomaly_count = 0

    def evaluate_gradient(self, current_torque: float, previous_torque: float, dt: float) -> Dict[str, Any]:
        """Calculate torque change per second and flag steep gradients."""
        if dt <= 0:
            gradient = 0.0
        else:
            gradient = (current_torque - previous_torque) / dt

        is_anomaly = abs(gradient) > self.max_allowable_gradient
        if is_anomaly:
            self.anomaly_count += 1
            logger.warning(f"[!] ANOMALY: Roller mill {self.mill_id} torque gradient {gradient:.2f} Nm/s exceeds limit {self.max_allowable_gradient}")

        record = {
            "timestamp": time.time(),
            "current_torque": current_torque,
            "previous_torque": previous_torque,
            "dt": dt,
            "gradient": gradient,
            "is_anomaly": is_anomaly
        }
        self.history.append(record)
        if len(self.history) > 1000:
            self.history.pop(0)
        return record

    def get_telemetry(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "anomaly_count": self.anomaly_count,
            "total_records": len(self.history)
        }


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Gradient Sentinel...")
    sentinel = RollerMillTorqueGradientAnalyzer(mill_id="MILL-NAI-04")
    res1 = sentinel.evaluate_gradient(120.0, 100.0, 0.1)
    res2 = sentinel.evaluate_gradient(190.0, 120.0, 0.1)
    print("Test Result 1:", res1)
    print("Test Result 2:", res2)
    print("Sentinel Telemetry:", sentinel.get_telemetry())
    print("Sentinel verification complete.")
