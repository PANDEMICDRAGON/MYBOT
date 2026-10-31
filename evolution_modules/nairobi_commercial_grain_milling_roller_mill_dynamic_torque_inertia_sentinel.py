"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Inertia Sentinel.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
Description: Monitors rotational inertia, transient shock loads, and torque disparities
on commercial grain milling roller mill assemblies. Protects drive mechanisms and electrical drives.
"""

import time
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RollerMillInertiaSentinel")

class RollerMillInertiaSentinel:
    """Analyzes and manages transient inertia and torque variance in commercial roller mills."""

    def __init__(self, mill_id: str, baseline_inertia_nm_s2: float = 1450.0, tolerance_pct: float = 7.5):
        self.mill_id = mill_id
        self.baseline_inertia = baseline_inertia_nm_s2
        self.tolerance_pct = tolerance_pct
        self.inertia_log: List[float] = []
        self.anomaly_count = 0
        logger.info(f"Initialized RollerMillInertiaSentinel for mill {self.mill_id} with baseline inertia {self.baseline_inertia} Nms^2.")

    def ingest_telemetry(self, current_inertia: float, motor_slip_hz: float) -> Dict[str, Any]:
        """Ingests live rotational inertia and slip metrics to evaluate mechanical stability."""
        try:
            self.inertia_log.append(current_inertia)
            if len(self.inertia_log) > 100:
                self.inertia_log.pop(0)

            deviation = ((current_inertia - self.baseline_inertia) / self.baseline_inertia) * 100.0
            status = "NOMINAL"
            corrective_action = None

            if abs(deviation) > self.tolerance_pct:
                self.anomaly_count += 1
                status = "ALERT_INERTIA_ANOMALY"
                if deviation > 0:
                    corrective_action = "ENGAGE_DYNAMIC_BRAKING_CHOPPER"
                    logger.warning(f"[{self.mill_id}] High inertia spike detected (+{deviation:.2f}%). {corrective_action}")
                else:
                    corrective_action = "BOOST_INVERTER_TORQUE_VECTOR"
                    logger.warning(f"[{self.mill_id}] Low inertia / load drop detected ({deviation:.2f}%). {corrective_action}")

            return {
                "timestamp": time.time(),
                "mill_id": self.mill_id,
                "current_inertia": current_inertia,
                "baseline_inertia": self.baseline_inertia,
                "deviation_pct": round(deviation, 2),
                "motor_slip_hz": motor_slip_hz,
                "status": status,
                "anomaly_count": self.anomaly_count,
                "corrective_action": corrective_action
            }
        except Exception as e:
            logger.error(f"Error processing inertia telemetry: {str(e)}")
            return {
                "timestamp": time.time(),
                "mill_id": self.mill_id,
                "status": "ERROR",
                "error": str(e)
            }

    def get_diagnostics(self) -> Dict[str, Any]:
        """Returns historical diagnostic aggregates."""
        if not self.inertia_log:
            return {"status": "NO_DATA"}
        return {
            "mill_id": self.mill_id,
            "mean_inertia": round(statistics.mean(self.inertia_log), 2),
            "max_inertia": round(max(self.inertia_log), 2),
            "min_inertia": round(min(self.inertia_log), 2),
            "total_anomalies": self.anomaly_count
        }

if __name__ == "__main__":
    print("--- Executing Self-Test for RollerMillInertiaSentinel ---")
    sentinel = RollerMillInertiaSentinel(mill_id="NAI_MILL_04_UGALI_LINE")
    
    # Simulate normal and anomalous telemetry feeds
    test_readings = [
        (1455.2, 1.2),
        (1448.9, 1.1),
        (1580.4, 2.5),  # Spike exceeding tolerance
        (1330.1, 0.4)   # Drop exceeding tolerance
    ];

    for inertia, slip in test_readings:
        result = sentinel.ingest_telemetry(inertia, slip)
        print(f"Telemetry Result: {result}")

    print("Diagnostics:", sentinel.get_diagnostics())
    print("--- Test Complete ---")
