"""
Nairobi Commercial Grain Milling Discharge Rotary Valve Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RotaryValveSentinel")

class RotaryValveSentinel:
    """Monitors commercial grain milling rotary airlock discharge valves for RPM variance, air leakage, and bearing vibration."""
    
    def __init__(self, valve_id: str, rated_rpm: float = 35.0):
        self.valve_id = valve_id
        self.rated_rpm = rated_rpm
        self.metrics_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RotaryValveSentinel for {{valve_id}} at rated RPM {{rated_rpm}}")

    def analyze_telemetry(self, current_rpm: float, differential_pressure_pa: float, vibration_mm_s: float) -> Dict[str, Any]:
        """Evaluate rotary valve performance and detect airlock seal or drive anomalies."""
        rpm_deviation = abs(current_rpm - self.rated_rpm) / self.rated_rpm
        pressure_alert = differential_pressure_pa < 200.0 or differential_pressure_pa > 1500.0
        vibration_alert = vibration_mm_s > 4.5
        
        status = "OPTIMAL"
        actions: List[str] = []

        if rpm_deviation > 0.15:
            status = "WARNING"
            actions.append("Inspect drive chain, gearbox reducer, and motor inverter.")
        
        if pressure_alert:
            status = "CRITICAL"
            actions.append("Airlock seal failure detected! Check rotor vane clearance and pneumatic blowback.")

        if vibration_alert:
            status = "CRITICAL"
            actions.append("High bearing vibration detected. Schedule immediate bearing lubrication or replacement.")

        telemetry_record = {
            "timestamp": time.time(),
            "valve_id": self.valve_id,
            "current_rpm": current_rpm,
            "differential_pressure_pa": differential_pressure_pa,
            "vibration_mm_s": vibration_mm_s,
            "status": status,
            "actions": actions
        }

        self.metrics_history.append(telemetry_record)
        return telemetry_record

if __name__ == "__main__":
    sentinel = RotaryValveSentinel(valve_id="RV-CYC-04")
    result = sentinel.analyze_telemetry(current_rpm=34.2, differential_pressure_pa=850.0, vibration_mm_s=2.1)
    logger.info(f"Test Telemetry Evaluation: {{result}}")
    assert result["status"] == "OPTIMAL", "Expected optimal status"
    print("Rotary Valve Sentinel Self-Test Passed Successfully.")
