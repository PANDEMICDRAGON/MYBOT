"""Nairobi Commercial Grain Milling Pneumatic Lift & Fan Sentinel.

Monitors pneumatic conveying fan load, static pressure differentials, rotary
airlock speeds, and duct velocity to prevent chokes and maintain seamless
mill floor material transfer.
"""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PneumaticLiftSentinel")


class PneumaticLiftSentinel:
    """Monitors and protects commercial grain mill pneumatic conveying circuits."""

    def __init__(self, circuit_id: str, design_airflow_cfm: float, max_static_pressure_pa: float):
        self.circuit_id = circuit_id
        self.design_airflow_cfm = design_airflow_cfm
        self.max_static_pressure_pa = max_static_pressure_pa
        self.history: List[Dict[str, Any]] = []
        self.alarm_state = False

    def evaluate_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate real-time pneumatic lift metrics and trigger countermeasures if needed."""
        timestamp = time.time()
        airflow = telemetry.get("airflow_cfm", self.design_airflow_cfm)
        static_pressure = telemetry.get("static_pressure_pa", 0.0)
        airlock_rpm = telemetry.get("airlock_rpm", 35.0)
        fan_vibration_mm_s = telemetry.get("fan_vibration_mm_s", 1.2)
        motor_current_amps = telemetry.get("motor_current_amps", 45.0)

        warnings = []
        actions = []

        # Check for pressure choke (pressure rising too high due to blockage)
        if static_pressure > (self.max_static_pressure_pa * 0.85):
            warnings.warn(f"High static pressure detected: {static_pressure} Pa")
            actions.append("REDUCE_FEED_GATE_RATE")
            self.alarm_state = True

        # Check for airflow drop (line blockage or fan slip)
        if airflow < (self.design_airflow_cfm * 0.75):
            warnings.append(f"Airflow drop critical: {airflow} CFM")
            actions.append(
                "TRIGGER_PNEUMATIC_PURGE_CYCLE"
            )
            self.alarm_state = True

        # Check for excessive vibration (fan imbalance or bearing wear)
        if fan_vibration_mm_s > 4.5:
            warnings.append(
                f"Excessive fan vibration: {fan_vibration_mm_s} mm/s"
            )
            actions.append(
                "ALERT_MAINTENANCE_SCHEDULE_BALANCING"
            )
            self.alarm_state = True

        if not warnings:
            self.alarm_state = False
            actions.append("OPTIMAL_CONVEYING")

        record = {
            "timestamp": timestamp,
            "circuit_id": self.circuit_id,
            "airflow_cfm": airflow,
            "static_pressure_pa": static_pressure,
            "airlock_rpm": airlock_rpm,
            "fan_vibration_mm_s": fan_vibration_mm_s,
            "warnings": warnings,
            "actions_taken": actions,
            "alarm_state": self.alarm_state,
        }

        self.history.append(record)
        if len(self.history) > 1000:
            self.history.pop(0)

        return record


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Pneumatic Lift Sentinel...")
    sentinel = PneumaticLiftSentinel(
        circuit_id="PN-LIFT-04", design_airflow_cfm=4500.0, max_static_pressure_pa=2800.0
    )

    # Test normal operation
    status = sentinel.evaluate_telemetry(
        {
            "airflow_cfm": 4450.0,
            "static_pressure_pa": 1800.0,
            "airlock_rpm": 35.0,
            "fan_vibration_mm_s": 1.1,
            "motor_current_amps": 44.2,
        }
    )
    print(f"Normal Status: {status}")

    # Test blockage / over-pressure condition
    alarm_status = sentinel.evaluate_telemetry(
        {
            "airflow_cfm": 3100.0,
            "static_pressure_pa": 2600.0,
            "airlock_rpm": 20.0,
            "fan_vibration_mm_s": 4.8,
            "motor_current_amps": 62.0,
        }
    )
    print(f"Alarm Status: {alarm_status}")
    print("Pneumatic Lift Sentinel Verification Complete.")
