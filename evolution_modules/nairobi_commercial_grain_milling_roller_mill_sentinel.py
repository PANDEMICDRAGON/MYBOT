"""Nairobi Commercial Grain Milling Roller Mill Biosafety Sentinel. Real-time telemetry monitoring for roller mill gap calibration, thermal bearing health, differential nip speeds, dust explosion mitigation, and automated emergency safety trips."""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("RollerMillSentinel")

class RollerMillSentinel:
    """Monitors industrial roller mills in Nairobi grain milling facilities."""

    def __init__(self, mill_id: str, roll_diameter_mm: float = 250.0):
        self.mill_id = mill_id
        self.roll_diameter_mm = roll_diameter_mm
        self.status = "STANDBY"
        self.emergency_tripped = False
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"RollerMillSentinel initialized for mill {self.mill_id} with {self.roll_diameter_mm}mm rolls.")

    def ingest_telemetry(self,
                         left_roll_rpm: float,
                         right_roll_rpm: float,
                         gap_micron: float,
                         bearing_temp_c: float,
                         vibration_mm_s: float,
                         dust_conc_gm3: float,
                         grain_moisture_pct: float) -> Dict[str, Any]:
        """Ingests live sensor data, evaluates mechanical stress, thermal limits, and explosion risks."""
        if self.emergency_tripped:
            logger.error(f"[{self.mill_id}] CRITICAL: Ingestion blocked. Mill is in EMERGENCY TRIPPED state.")
            return {"status": "TRIPPED", "action": "SHUTDOWN"}

        # Calculate differential speed ratio (fast roll vs slow roll)
        fast_rpm = max(left_roll_rpm, right_roll_rpm)
        slow_rpm = min(left_roll_rpm, right_roll_rpm)
        speed_ratio = fast_rpm / (slow_rpm if slow_rpm > 0 else 1.0)

        alerts = []
        action = "CONTINUE"

        # Thermal threshold check (Bearings > 75C risk failure)
        if bearing_temp_c > 75.0:
            alerts.append(f"HIGH_BEARING_TEMP: {bearing_temp_c}C")
            action = "WARNING"

        # Vibration check (> 4.5 mm/s indicates severe misalignment or worn flutes)
        if vibration_mm_s > 4.5:
            alerts.append(f"EXCESSIVE_VIBRATION: {vibration_mm_s} mm/s")
            action = "SLOW_DOWN"

        # Dust explosion hazard check (Starch dust lower explosive limit ~ 50 g/m3)
        if dust_conc_gm3 > 40.0:
            alerts.append(f"DANGER_DUST_CONCENTRATION: {dust_conc_gm3} g/m3")
            action = "TRIGGER_SUPPRESSION"

        # Emergency Trip Condition
        if bearing_temp_c > 90.0 or vibration_mm_s > 8.0 or dust_conc_gm3 > 60.0:
            self.emergency_tripped = True
            self.status = "TRIPPED"
            action = "EMERGENCY_SHUTDOWN"
            logger.critical(f"[{self.mill_id}] EMERGENCY TRIP ACTIVATED! Alerts: {alerts}")

        record = {
            "timestamp": time.time(),
            "left_rpm": left_roll_rpm,
            "right_rpm": right_roll_rpm,
            "speed_ratio": round(speed_ratio, 2),
            "gap_micron": gap_micron,
            "bearing_temp_c": bearing_temp_c,
            "vibration_mm_s": vibration_mm_s,
            "dust_conc_gm3": dust_conc_gm3,
            "grain_moisture_pct": grain_moisture_pct,
            "alerts": alerts,
            "action": action
        }

        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return record

    def reset_trip(self, operator_key: str) -> bool:
        """Resets emergency trip after physical inspection and operator clearance."""
        if operator_key == "MICHAEL_OBIERO_SECURE_AUTH":
            self.emergency_tripped = False
            self.status = "STANDBY"
            logger.info(f"[{self.mill_id}] Trip reset successfully by operator.")
            return True
        logger.warning(f"[{self.mill_id}] Unauthorized trip reset attempt.")
        return False

    def get_diagnostics(self) -> Dict[str, Any]:
        """Returns system health and performance analytics."""
        return {
            "mill_id": self.mill_id,
            "status": self.status,
            "emergency_tripped": self.emergency_tripped,
            "total_telemetry_records": len(self.telemetry_history)
        }


if __name__ == "__main__":
    print("--- Executing RollerMillSentinel Diagnostic Harness ---")
    sentinel = RollerMillSentinel(mill_id="NAI_MILL_IND_04")
    
    # Test normal ingestion
    res1 = sentinel.ingest_telemetry(
        left_roll_rpm=600.0,
        right_roll_rpm=150.0,
        gap_micron=200.0,
        bearing_temp_c=58.2,
        vibration_mm_s=1.2,
        dust_conc_gm3=12.5,
        grain_moisture_pct=13.2
    )
    print(f"Telemetry 1: {res1}")
    
    # Test hazardous ingestion triggering emergency shutdown
    res2 = sentinel.ingest_telemetry(
        left_roll_rpm=850.0,
        right_roll_rpm=200.0,
        gap_micron=100.0,
        bearing_temp_c=94.5,
        vibration_mm_s=9.1,
        dust_conc_gm3=68.0,
        grain_moisture_pct=10.1
    )
    print(f"Telemetry 2: {res2}")
    
    # Reset test
    reset_status = sentinel.reset_trip("MICHAEL_OBIERO_SECURE_AUTH")
    print(f"Reset Status: {reset_status}")
    print(f"Diagnostics: {sentinel.get_diagnostics()}")
