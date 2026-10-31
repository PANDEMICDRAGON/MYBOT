"""
Nairobi Commercial Grain Milling Discharge Rotary Valve Torque Sentinel
Monitors drive motor current draw and torque feedback on commercial rotary airlock valves
underneath cyclone and filter discharges to prevent mechanical binding or product bridging.
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("DischargeRotaryValveTorqueSentinel")

class RotaryValveTorqueSentinel:
    """
    Evaluates rotary airlock valve telemetry to detect jamming, over-torque events,
    and erratic discharge flow patterns in Nairobi commercial flour mills.
    """
    def __init__(self, valve_id: str, rated_current_amps: float = 4.5, max_torque_nm: float = 85.0):
        self.valve_id = valve_id
        self.rated_current_amps = rated_current_amps
        self.max_torque_nm = max_torque_nm
        self.telemetry_history: List[Dict[str, Any]] = []
        self.status = "NORMAL"
        self.consecutive_spikes = 0

    def ingest_telemetry(self, current_amps: float, speed_rpm: float, bearing_temp_c: float) -> Dict[str, Any]:
        """
        Ingests real-time electrical current, rotational speed, and bearing temperature.
        Calculates estimated operational torque and detects anomalies.
        """
        timestamp = time.time()
        # Estimated torque proportional to current draw relative to rated load
        estimated_torque = (current_amps / self.rated_current_amps) * (self.max_torque_nm * 0.6)
        
        anomaly_detected = False
        action_required = "NONE"

        if current_amps > (self.rated_current_amps * 1.35) or estimated_torque > (self.max_torque_nm * 0.85):
            self.consecutive_spikes += 1
            anomaly_detected = True
        else:
            self.consecutive_spikes = max(0, self.consecutive_spikes - 1)

        if self.consecutive_spikes >= 3:
            self.status = "CRITICAL_JAM_WARNING"
            action_required = "TRIGGER_REVERSE_PULSE_AND_ALARM"
        elif bearing_temp_c > 75.0:
            self.status = "BEARING_OVERHEAT"
            action_required = "SCHEDULE_LUBRICATION_INSPECTION"
        else:
            self.status = "NORMAL"
            action_required = "CONTINUE_MONITORING"

        record = {
            "timestamp": timestamp,
            "valve_id": self.valve_id,
            "current_amps": current_amps,
            "speed_rpm": speed_rpm,
            "estimated_torque_nm": round(estimated_torque, 2),
            "bearing_temp_c": bearing_temp_c,
            "status": self.status,
            "action_required": action_required
        }

        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        logger.info(f"Valve {self.valve_id} | Status: {self.status} | Torque: {estimated_torque:.1f}Nm | Action: {action_required}")
        return record

    def get_diagnostic_summary(self) -> Dict[str, Any]:
        """Returns summary of valve operational integrity."""
        if not self.telemetry_history:
            return {"status": "NO_DATA"}
        
        latest = self.telemetry_history[-1]
        return {
            "valve_id": self.valve_id,
            "current_status": self.status,
            "latest_telemetry": latest,
            "total_records": len(self.telemetry_history)
        }

if __name__ == "__main__":
    sentinel = RotaryValveTorqueSentinel(valve_id="RV-CYC-04")
    
    # Simulate normal operation
    sentinel.ingest_telemetry(current_amps=4.1, speed_rpm=25.0, bearing_temp_c=45.2)
    
    # Simulate minor load bump
    sentinel.ingest_telemetry(current_amps=5.2, speed_rpm=24.5, bearing_temp_c=48.0)
    
    # Simulate jam sequence
    sentinel.ingest_telemetry(current_amps=6.8, speed_rpm=18.0, bearing_temp_c=55.0)
    sentinel.ingest_telemetry(current_amps=7.2, speed_rpm=10.0, bearing_temp_c=58.0)
    sentinel.ingest_telemetry(current_amps=7.5, speed_rpm=2.0, bearing_temp_c=61.0)
    
    summary = sentinel.get_diagnostic_summary()
    print("DIAGNOSTIC SUMMARY:", summary)
