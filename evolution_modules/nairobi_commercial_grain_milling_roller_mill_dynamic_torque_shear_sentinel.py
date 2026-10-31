"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Shear Sentinel.

Provides real-time monitoring and anomaly detection for roller mill shear stresses,
torsional harmonics, and differential roll speeds across industrial grain milling
installations in Nairobi, Kenya.
"""

import time
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillShearSentinel")


class RollerMillShearSentinel:
    """Monitors roller mill dynamic torque shear parameters to prevent catastrophic failure."""

    def __init__(self, mill_id: str, shear_threshold_nm: float = 450.0):
        self.mill_id = mill_id
        self.shear_threshold_nm = shear_threshold_nm
        self.shear_history: List[float] = []
        self.anomaly_count = 0
        logger.info("Initialized RollerMillShearSentinel for Mill: %s with threshold %.2f Nm", mill_id, shear_threshold_nm)

    def ingest_telemetry(self, timestamp: float, left_torque_nm: float, right_torque_nm: float, differential_rpm: float) -> Dict[str, Any]:
        """Ingests torque and differential speed telemetry to compute shear stress vector."""
        shear_stress = abs(left_torque_nm - right_torque_nm) * (1.0 + abs(differential_rpm) * 0.01)
        self.shear_history.append(shear_stress)
        if len(self.shear_history > 1000):
            self.shear_history.pop(0)

        is_anomaly = shear_stress > self.shear_threshold_nm
        if is_anomaly:
            self.anomaly_count += 1
            logger.warning("SHEAR ANOMALY DETECTED on Mill %s: Shear Stress %.2f Nm exceeds threshold!", self.mill_id, shear_stress)

        return {
            "mill_id": self.mill_id,
            "timestamp": timestamp,
            "shear_stress_nm": shear_stress,
            "anomaly": is_anomaly,
            "total_anomalies": self.anomaly_count
        }

    def get_diagnostic_report(self) -> Dict[str, Any]:
        """Returns rolling diagnostic statistics for the mill shear sentinel."""
        if not self.shear_history:
            return {"status": "no_data"}
        return {
            "mill_id": self.mill_id,
            "mean_shear": statistics.mean(self.shear_history),
            "max_shear": max(self.shear_history),
            "min_shear": min(self.shear_history),
            "anomaly_count": self.anomaly_count
        }


if __name__ == "__main__":
    sentinel = RollerMillShearSentinel(mill_id="NAI_MILL_042")
    now = time.time()
    
    # Simulate normal operation
    for i in range(5):
        res = sentinel.ingest_telemetry(now + i, 320.0, 325.0, 2.0)
        print(f"Telemetry {i}: {res}")

    # Simulate shear anomaly event
    anomaly_res = sentinel.ingest_telemetry(now + 6, 520.0, 380.0, 15.0)
    print(f"Telemetry Anomaly: {anomaly_res}")
    
    print("Diagnostic Report:", sentinel.get_diagnostic_report())
