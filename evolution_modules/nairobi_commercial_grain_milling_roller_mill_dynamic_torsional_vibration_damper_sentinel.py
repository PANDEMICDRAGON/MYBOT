"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsional Vibration Damper Sentinel
Autonomous Evolutionary Architecture - Cycle #754

Monitors torsional vibration frequencies, calculates harmonic distortion vectors, and modulates
active electromagnetic damper torque to stabilize roller mill drive trains.
"""

import os
import sys
import time
import math
import logging
import json
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("TorsionalVibrationDamperSentinel")

class TorsionalVibrationDamperSentinel:
    """
    Active vibration damping and torsional stress stabilization engine for industrial roller mills.
    """
    def __init__(self, mill_id: str, nominal_rpm: float = 1450.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.active_damping_active = True
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized TorsionalVibrationDamperSentinel for mill {mill_id} at {nominal_rpm} RPM.")

    def analyze_vibration(self, shaft_rpm: float, torsional_deflection_deg: float, current_load_amps: float) -> Dict[str, Any]:
        """
        Analyzes live telemetry from shaft encoders and torque sensors to compute required counter-torque.
        """
        rpm_deviation = abs(shaft_rpm - self.nominal_rpm)
        # Torsional stress index based on deflection and current draw
        torsional_stress_mpa = (torsional_deflection_deg * 12.5) + (current_load_amps * 0.45)
        
        # Dynamic damping coefficient calculation
        damping_torque_nm = 0.0
        status = "OPTIMAL"

        if torsional_stress_mpa > 85.0:
            status = "WARNING_HIGH_TORSION"
            damping_torque_nm = torsional_stress_mpa * 3.2
        elif torsional_stress_mpa > 120.0:
            status = "CRITICAL_RESONANCE"
            damping_torque_nm = torsional_stress_mpa * 5.0
            self._trigger_emergency_dampening_pulse()

        assessment = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "shaft_rpm": shaft_rpm,
            "rpm_deviation": rpm_deviation,
            "torsional_stress_mpa": round(torsional_stress_mpa, 2),
            "damping_torque_nm": round(damping_torque_nm, 2),
            "status": status
        }
        
        self.telemetry_history.append(assessment)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return assessment

    def _trigger_emergency_dampening_pulse(self) -> None:
        """
        Emits an emergency counter-electromotive pulse to break harmonic lock.
        """
        logger.warning(f"[{self.mill_id}] CRITICAL RESONANCE DETECTED! Deploying counter-electromotive damping pulse.")

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "total_samples": len(self.telemetry_history),
            "system_status": "ACTIVE" if self.active_damping_active else "STANDBY"
        }

if __name__ == "__main__":
    logger.info("Executing self-test harness for TorsionalVibrationDamperSentinel...")
    sentinel = TorsionalVibrationDamperSentinel(mill_id="NAIROBI_MILL_ALPHA_04", nominal_rpm=1500.0)
    
    # Simulate normal operation
    res1 = sentinel.analyze_vibration(shaft_rpm=1498.5, torsional_deflection_deg=1.2, current_load_amps=42.0)
    print(json.dumps(res1, indent=2))
    
    # Simulate high torsional stress condition
    res2 = sentinel.analyze_vibration(shaft_rpm=1440.0, torsional_deflection_deg=9.8, current_load_amps=88.5)
    print(json.dumps(res2, indent=2))
    
    print(json.dumps(sentinel.get_diagnostics(), indent=2))
    logger.info("Test harness completed successfully.")
