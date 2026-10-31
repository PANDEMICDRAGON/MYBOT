"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Slip Sentinel
Designed for real-time slip anomaly detection across differential roller mills in Nairobi industrial milling complexes.
"""

import time
import math
import statistics
from typing import Dict, List, Any, Optional


class RollerMillTorqueSlipSentinel:
    """
    Monitors angular velocity and dynamic torque differentials between fast and slow rolls
    in commercial roller mills to detect micro-slippage, belt wear, and grain starvation.
    """

    def __init__(self, mill_id: str, nominal_differential_ratio: float = 2.5, slip_threshold_pct: float = 4.5):
        self.mill_id = mill_id
        self.nominal_ratio = nominal_differential_ratio
        self.slip_threshold = slip_threshold_pct
        self.telemetry_buffer: List[Dict[str, float]] = []
        self.alert_history: List[Dict[str, Any]] = []

    def ingest_telemetry(self, fast_roll_rpm: float, slow_roll_rpm: float, fast_torque_nm: float, slow_torque_nm: float) -> Dict[str, Any]:
        """
        Ingests high-frequency roll telemetry, computes instantaneous slip ratio,
        and evaluates mechanical integrity.
        """
        timestamp = time.time()
        
        # Avoid division by zero
        if slow_roll_rpm <= 0:
            measured_ratio = 0.0
            slip_pct = 100.0
        else:
            measured_ratio = fast_roll_rpm / slow_roll_rpm
            slip_pct = abs((measured_ratio - self.nominal_ratio) / self.nominal_ratio) * 100.0

        torque_asymmetry = abs(fast_torque_nm - slow_torque_nm) / max(1.0, (fast_torque_nm + slow_torque_nm) / 2.0) * 100.0

        record = {
            "timestamp": timestamp,
            "fast_rpm": fast_roll_rpm,
            "slow_rpm": slow_roll_rpm,
            "measured_ratio": measured_ratio,
            "slip_pct": slip_pct,
            "torque_asymmetry": torque_asymmetry
        }

        self.telemetry_buffer.append(record)
        if len(self.telemetry_buffer) > 1000:
            self.telemetry_buffer.pop(0)

        status = "NOMINAL"
        if slip_pct > self.slip_threshold:
            status = "CRITICAL_SLIP"
            alert = {
                "timestamp": timestamp,
                "mill_id": self.mill_id,
                "severity": "HIGH",
                "message": f"Roll slip detected: {slip_pct:.2f}% exceeds threshold {self.slip_threshold}%"
            }
            self.alert_history.append(alert)

        return {
            "mill_id": self.mill_id,
            "status": status,
            "slip_pct": round(slip_pct, 3),
            "torque_asymmetry_pct": round(torque_asymmetry, 3),
            "timestamp": timestamp
        }

    def get_diagnostics(self) -> Dict[str, Any]:
        """Returns aggregated health metrics and recent slip volatility."""
        if not self.telemetry_buffer:
            return {"status": "NO_DATA"}

        slips = [r["slip_pct"] for r in self.telemetry_buffer]
        return {
            "mill_id": self.mill_id,
            "samples_analyzed": len(self.telemetry_buffer),
            "mean_slip_pct": round(statistics.mean(slips), 3),
            "max_slip_pct": round(max(slips), 3),
            "total_alerts": len(self.alert_history)
        }


if __name__ == "__main__":
    sentinel = RollerMillTorqueSlipSentinel(mill_id="NAIROBI_MILL_ALPHA_04")
    
    # Simulate normal operation
    res1 = sentinel.ingest_telemetry(1200.0, 480.0, 150.2, 148.5)
    print("Normal Ingest:", res1)
    
    # Simulate sudden slip event
    res2 = sentinel.ingest_telemetry(1250.0, 420.0, 190.0, 110.0)
    print("Slip Event:", res2)
    
    print("Diagnostics:", sentinel.get_diagnostics())
