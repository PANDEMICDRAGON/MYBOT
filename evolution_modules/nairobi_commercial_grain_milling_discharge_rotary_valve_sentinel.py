"""
Nairobi Commercial Grain Milling Discharge Rotary Valve & Airlock Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import logging
import random
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (RotaryValveSentinel): %(message)s')

class DischargeRotaryValveSentinel:
    """
    Monitors commercial grain milling rotary discharge valves and airlocks to ensure
    proper back-pressure maintenance, preventing product blowback and mechanical jamming.
    """
    def __init__(self, valve_id: str, rated_rpm: float = 35.0):
        self.valve_id = valve_id
        self.rated_rpm = rated_rpm
        self.is_running = False
        self.audit_log: List[Dict[str, Any]] = []

    def start_monitoring(self) -> None:
        self.is_running = True
        logging.info(f"Discharge Rotary Valve Sentinel active on unit {self.valve_id}.")

    def sample_telemetry(self, current_rpm: float, motor_current_amps: float, differential_pressure_kpa: float) -> Dict[str, Any]:
        if not self.is_running:
            raise RuntimeError("Sentinel is not running.")

        rpm_deviation = abs(current_rpm - self.rated_rpm) / self.rated_rpm
        jam_detected = motor_current_amps > 12.5
        pressure_loss = differential_pressure_kpa < 1.2

        status = "OPTIMAL"
        if jam_detected:
            status = "CRITICAL_JAM_RISK"
        elif rpm_deviation > 0.15 or pressure_loss:
            status = "WARNING_SEAL_WEAR"

        telemetry = {
            "valve_id": self.valve_id,
            "timestamp": time.time(),
            "current_rpm": current_rpm,
            "motor_current_amps": motor_current_amps,
            "differential_pressure_kpa": differential_pressure_kpa,
            "status": status
        }
        self.audit_log.append(telemetry)
        return telemetry

    def mitigate_anomaly(self, status: str) -> str:
        if status == "CRITICAL_JAM_RISK":
            logging.warning(f"[{self.valve_id}] Executing emergency reverse cycle to clear feed jam!")
            return "REVERSE_PULSE_EXECUTED"
        elif status == "WARNING_SEAL_WEAR":
            logging.info(f"[{self.valve_id}] Adjusting variable speed drive to compensate for seal blow-by.")
            return "VSD_COMPENSATED"
        return "NO_ACTION_REQUIRED"

if __name__ == "__main__":
    sentinel = DischargeRotaryValveSentinel(valve_id="RV-SILO-04")
    sentinel.start_monitoring()
    
    # Simulate telemetry sampling
    for _ in range(3):
        rpm = random.uniform(30.0, 38.0)
        amps = random.uniform(4.0, 14.0)
        dp = random.uniform(1.0, 3.5)
        telemetry = sentinel.sample_telemetry(rpm, amps, dp)
        action = sentinel.mitigate_anomaly(telemetry["status"])
        logging.info(f"Telemetry: {telemetry} | Action: {action}")
        time.sleep(0.1)
