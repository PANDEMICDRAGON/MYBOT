"""Nairobi Commercial Medical & Laboratory Autoclave Sterilization Biosafety Sentinel."""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [AutoclaveSentinel]: %(message)s')
logger = logging.getLogger("AutoclaveSentinel")

class AutoclaveCycleState:
    IDLE = "IDLE"
    HEATING = "HEATING"
    STERILIZING = "STERILIZING"
    EXHAUSTING = "EXHAUSTING"
    COMPLETE = "COMPLETE"
    ABORTED_FAIL = "ABORTED_FAIL"

class NairobiCommercialAutoclaveSentinel:
    """
    Monitors temperature, chamber pressure, and hold times for commercial autoclaves in Nairobi labs.
    Computes Fo lethal rate values (assuming z=10°C, Tref=121.1°C) to certify biological destruction.
    """
    def __init__(self, autoclave_id: str, target_temp_c: float = 121.1, target_pressure_kpa: float = 105.0, required_hold_secs: int = 900):
        self.autoclave_id = autoclave_id
        self.target_temp_c = target_temp_c
        self.target_pressure_kpa = target_pressure_kpa
        self.required_hold_secs = required_hold_secs
        
        self.state = AutoclaveCycleState.IDLE
        self.current_temp = 25.0
        self.current_pressure = 0.0
        self.hold_timer_secs = 0
        self.accumulated_fo = 0.0
        self.cycle_logs: List[Dict[str, Any]] = []
        self.lockdown_active = False

    def start_cycle(self) -> None:
        if self.lockdown_active:
            logger.error(f"[{self.autoclave_id}] CRITICAL: Cannot start cycle. Autoclave under safety lockdown.")
            return
        self.state = AutoclaveCycleState.HEATING
        self.accumulated_fo = 0.0
        self.hold_timer_secs = 0
        self.cycle_logs.clear()
        logger.info(f"[{self.autoclave_id}] Cycle initiated. Heating chamber to {self.target_temp_c}°C...")

    def feed_sensor_telemetry(self, temp_c: float, pressure_kpa: float) -> Dict[str, Any]:
        """Ingests live telemetry from chamber sensors and advances state machine."""
        self.current_temp = temp_c
        self.current_pressure = pressure_kpa
        timestamp = time.time()

        telemetry_entry = {
            "timestamp": timestamp,
            "temp_c": temp_c,
            "pressure_kpa": pressure_kpa,
            "state": self.state,
            "fo": self.accumulated_fo
        }
        self.cycle_logs.append(telemetry_entry)

        if self.state == AutoclaveCycleState.HEATING:
            # Check if operating pressure & temp reached
            if temp_c >= self.target_temp_c and pressure_kpa >= self.target_pressure_kpa:
                self.state = AutoclaveCycleState.STERILIZING
                logger.info(f"[{self.autoclave_id}] Sterilization parameters reached. Holding phase active.")

        elif self.state == AutoclaveCycleState.STERILIZING:
            # Calculate Fo value contribution: Fo = delta_t * 10^((T - 121.1) / 10)
            delta_t = 1.0 # assuming 1 second tick
            z_val = 10.0
            t_ref = 121.1
            fo_increment = delta_t * (10.0 ** ((temp_c - t_ref) / z_val))
            self.accumulated_fo += fo_increment
            self.hold_timer_secs += 1

            # Check for sudden pressure drop or temperature dip (Sterility Breach)
            if temp_c < (self.target_temp_c - 2.0) or pressure_kpa < (self.target_pressure_kpa - 5.0):
                logger.warning(f"[{self.autoclave_id}] STERILITY BREACH DETECTED: Temp/Pressure drop during hold!")
                self.state = AutoclaveCycleState.ABORTED_FAIL
                self.lockdown_active = True
                return telemetry_entry

            if self.hold_timer_secs >= self.required_hold_secs:
                self.state = AutoclaveCycleState.EXHAUSTING
                logger.info(f"[{self.autoclave_id}] Hold complete. Fo achieved: {self.accumulated_fo:.2f}. Venting chamber...")

        elif self.state == AutoclaveCycleState.EXHAUSTING:
            if pressure_kpa <= 5.0 and temp_c < 80.0:
                self.state = AutoclaveCycleState.COMPLETE
                logger.info(f"[{self.autoclave_id}] Cycle SUCCESSFUL. Safe to unload sterilized materials.")

        return telemetry_entry

    def reset_lockdown(self, operator_key: str) -> bool:
        if operator_key == "MICHAEL_OBIERO_ADMIN_KEY":
            self.lockdown_active = False
            self.state = AutoclaveCycleState.IDLE
            logger.warning(f"[{self.autoclave_id}] Lockdown manually cleared by operator Michael Obiero.")
            return True
        logger.error(f"[{self.autoclave_id}] Unauthorized lockdown reset attempt.")
        return False

    def get_audit_summary(self) -> Dict[str, Any]:
        return {
            "autoclave_id": self.autoclave_id,
            "state": self.state,
            "accumulated_fo": round(self.accumulated_fo, 2),
            "lockdown_active": self.lockdown_active,
            "total_telemetry_points": len(self.cycle_logs)
        }

if __name__ == "__main__":
    print("--- Executing Nairobi Commercial Autoclave Sentinel Simulation ---")
    sentinel = NairobiCommercialAutoclaveSentinel("AUTO-LAB-01", target_temp_c=121.1, target_pressure_kpa=105.0, required_hold_secs=5)
    
    sentinel.start_cycle()
    
    # Simulate heating phase
    sentinel.feed_sensor_telemetry(110.0, 80.0)
    sentinel.feed_sensor_telemetry(121.5, 108.0)
    
    # Simulate holding phase (5 ticks)
    for _ in range(5):
        sentinel.feed_sensor_telemetry(121.6, 108.5)
        
    # Simulate exhausting / cooling phase
    sentinel.feed_sensor_telemetry(95.0, 40.0)
    sentinel.feed_sensor_telemetry(75.0, 2.0)
    
    summary = sentinel.get_audit_summary()
    print(f"Final Audit Summary: {summary}")
    assert summary["state"] == AutoclaveCycleState.COMPLETE
    print("--- Autoclave Sentinel Simulation Passed Successfully ---")
