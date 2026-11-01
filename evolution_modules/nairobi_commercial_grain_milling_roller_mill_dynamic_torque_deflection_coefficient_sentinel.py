"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Deflection Coefficient Sentinel."""

import time
import math
import random
from typing import Dict, List, Any


class TorqueDeflectionSentinel:
    """Monitors roller mill drive shaft torque deflection coefficients and flags anomalies."""

    def __init__(self, warning_threshold: float = 0.85, critical_threshold: float = 0.95):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.telemetry_history: List[Dict[str, Any]] = []

    def evaluate_deflection(self, mill_id: str, torque_nm: float, rpm: float, twist_angle_deg: float) -> Dict[str, Any]:
        """Evaluate shaft deflection coefficient based on torque and twist angle."""
        # Coefficient formula: normalized ratio of measured angular deflection vs rated baseline
        baseline_twist_per_nm = 0.0012  
        expected_twist = torque_nm * baseline_twist_per_nm
        coefficient = twist_angle_deg / (expected_twist if expected_twist > 0 else 0.0001)
        coefficient = min(max(coefficient, 0.0), 2.0)

        status = "NOMINAL"
        if coefficient >= self.critical_threshold:
            status = "CRITICAL_DEFLECTION_ANOMALY"
        elif coefficient >= self.warning_threshold:
            status = "WARNING_ELEVATED_STRESS"

        record = {
            "timestamp": time.time(),
            "mill_id": mill_id,
            "torque_nm": torque_nm,
            "rpm": rpm,
            "twist_angle_deg": twist_angle_deg,
            "deflection_coefficient": round(coefficient, 4),
            "status": status
        }
        self.telemetry_history.append(record)
        return record

    def get_summary(self) -> Dict[str, Any]:
        """Return summary statistics of recent telemetry evaluations."""
        if not self.telemetry_history:
            return {"total_events": 0, "active_alerts": 0}

        alerts = sum(1 for r in self.telemetry_history if r["status"] != "NOMINAL")
        return {
            "total_events": len(self.telemetry_history),
            "active_alerts": alerts,
            "last_evaluated": self.telemetry_history[-1]
        }


if __name__ == "__main__":
    sentinel = TorqueDeflectionSentinel()
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Deflection Coefficient Sentinel...")
    
    # Simulate telemetry stream
    for i in range(5):
        sample_torque = 1200.0 + random.uniform(-50.0, 150.0)
        sample_rpm = 750.0 + random.uniform(-10.0, 10.0)
        sample_twist = 1.45 + (0.1 if i == 3 else 0.0)  # Simulate spike on 4th iteration
        result = sentinel.evaluate_deflection(f"MILL-NAI-0{i+1}", sample_torque, sample_rpm, sample_twist)
        print(f"Iteration {i+1} Result: {result}")

    print("Sentinel Summary:", sentinel.get_summary())
    print("Sentinel execution completed successfully.")
