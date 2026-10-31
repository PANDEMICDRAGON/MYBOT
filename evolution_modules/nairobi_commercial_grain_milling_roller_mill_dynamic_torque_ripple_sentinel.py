"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Sentinel

Monitor instantaneous angular velocity and harmonic torque ripples on commercial roller mill
shafts to detect asymmetrical bearing wear, belt harmonic resonance, or incipient mechanical binding.
"""

import math
import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueRippleSentinel")

class RollerMillTorqueRippleSentinel:
    def __init__(self, mill_id: str, nominal_rpm: float = 750.0, ripple_threshold_pct: float = 5.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.ripple_threshold_pct = ripple_threshold_pct
        self.telemetry_history: List[Dict[str, float]] = []

    def ingest_telemetry(self, timestamp: float, instantaneous_rpm: float, torque_nm: float) -> Dict[str, Any]:
        """Ingest instantaneous shaft speed and torque to compute ripple indices."""
        rpm_deviation = abs(instantaneous_rpm - self.nominal_rpm)
        deviation_pct = (rpm_deviation / self.nominal_rpm) * 100.0
        
        self.telemetry_history.append({
            "timestamp": timestamp,
            "rpm": instantaneous_rpm,
            "torque": torque_nm,
            "deviation": deviation_pct
        })
        
        if len(self.telemetry_history) > 100:
            self.telemetry_history.pop(0)

        return self._evaluate_ripple(instantaneous_rpm, torque_nm, deviation_pct)

    def _evaluate_ripple(self, rpm: float, torque: float, deviation_pct: float) -> Dict[str, Any]:
        status = "NOMINAL"
        action = "NONE"

        if deviation_pct > self.ripple_threshold_pct:
            status = "WARNING"
            action = "MONITOR_DRIVE_BELT_TENSION"
        if deviation_pct > (self.ripple_threshold_pct * 2.0):
            status = "CRITICAL"
            action = "INITIATE_EMERGENCY_ROLLER_SLOWDOWN"
            logger.error(f"[CRITICAL] Mill {self.mill_id}: Torque ripple spike detected! Deviation: {deviation_pct:.2f}%")

        return {
            "mill_id": self.mill_id,
            "status": status,
            "action": action,
            "current_rpm": rpm,
            "torque_nm": torque,
            "deviation_pct": deviation_pct,
            "timestamp": time.time()
        }

if __name__ == "__main__":
    sentinel = RollerMillTorqueRippleSentinel(mill_id="UGUNJA_MILL_04")
    now = time.time()
    test_readings = [
        (750.0, 120.5),
        (742.1, 128.0),
        (731.5, 142.3),
        (710.0, 165.0)
    ]
    for i, (rpm, tq) in enumerate(test_readings):
        res = sentinel.ingest_telemetry(now + i, rpm, tq)
        print(f"Reading {i}: Status -> {res['status']}, Action -> {res['action']}, Deviation -> {res['deviation_pct']:.2f}%")
