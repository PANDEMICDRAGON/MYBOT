"""
Nairobi Commercial Grain Milling Roller Mill Emergency Quick Release Sentinel
Designed for automated monitoring and predictive fault detection of roller mill emergency
separation systems in Nairobi, Kenya industrial milling complexes.
"""

import time
import random
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [RollerQuickReleaseSentinel]: %(message)s')
logger = logging.getLogger(__name__)

class RollerMillEmergencyQuickReleaseSentinel:
    """
    Monitors rapid-release pneumatic cylinders, accumulator pressure, solenoid valve health,
    and mechanical trip linkage feedback for commercial grain roller mills.
    """
    def __init__(self, mill_id: str, nominal_pressure_bar: float = 6.0):
        self.mill_id = mill_id
        self.nominal_pressure_bar = nominal_pressure_bar
        self.telemetry_history: List[Dict[str, Any]] = []
        self.is_active = True
        logger.info(f"RollerMillEmergencyQuickReleaseSentinel initialized for mill {mill_id} at {nominal_pressure_bar} bar.")

    def inspect_actuation_telemetry(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inspects current pressure, solenoid continuity, and travel sensor feedback.
        Returns diagnostic status and anomaly alerts.
        """
        pressure = sensor_data.get("accumulator_pressure_bar", self.nominal_pressure_bar)
        solenoid_ohm = sensor_data.get("solenoid_resistance_ohm", 24.0)
        response_time_ms = sensor_data.get("last_release_response_ms", 12.5)
        linkage_wear_mm = sensor_data.get("linkage_play_mm", 0.2)

        alerts = []
        status = "OPTIMAL"

        # Pressure drop check
        if pressure < (self.nominal_pressure_bar * 0.85):
            status = "WARNING"
            alerts.append(f"Sub-optimal pneumatic accumulator pressure: {pressure} bar (Nominal: {self.nominal_pressure_bar})")
        if pressure < (self.nominal_pressure_bar * 0.70):
            status = "CRITICAL"
            alerts.append(f"DANGER: Quick-release pneumatic pressure critically low: {pressure} bar!")

        # Solenoid coil resistance check (approx 24 ohm nominal for industrial 24V DC valves)
        if not (20.0 <= solenoid_ohm <= 28.0):
            status = "WARNING"
            alerts.append(f"Solenoid coil resistance anomaly detected: {solenoid_ohm} ohms (Expected 20-28)")

        # Response time check (Must be under 20ms)
        if response_time_ms > 18.0:
            status = "WARNING"
            alerts.append(f"Slow emergency separation response time: {response_time_ms}ms (Threshold <18ms)")
        if response_time_ms > 25.0:
            status = "CRITICAL"
            alerts.append(f"CRITICAL: Emergency release actuation sluggish! {response_time_ms}ms")

        # Mechanical linkage play check
        if linkage_wear_mm > 0.8:
            status = "WARNING"
            alerts.append(f"Excessive mechanical linkage play: {linkage_wear_mm}mm. Check pivot pins.")

        record = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "status": status,
            "pressure_bar": pressure,
            "response_time_ms": response_time_ms,
            "alerts": alerts
        }

        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return record

    def run_self_test(self) -> Dict[str, Any]:
        """
        Simulates dry-run pulse test of the quick release solenoid and spring return.
        """
        logger.info(f"Executing automated self-test for mill {self.mill_id} quick release...")
        simulated_data = {
            "accumulator_pressure_bar": round(random.uniform(5.8, 6.2), 2),
            "solenoid_resistance_ohm": round(random.uniform(23.5, 24.5), 2),
            "last_release_response_ms": round(random.uniform(10.0, 15.0), 2),
            "linkage_play_mm": round(random.uniform(0.1, 0.4), 2)
        }
        return self.inspect_actuation_telemetry(simulated_data)

if __name__ == "__main__":
    sentinel = RollerMillEmergencyQuickReleaseSentinel(mill_id="NAI_MILL_04_UGALI_LINE")
    result = sentinel.run_self_test()
    print(f"Self-Test Result: {result}")
