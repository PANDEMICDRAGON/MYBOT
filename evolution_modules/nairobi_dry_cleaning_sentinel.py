"""
Nairobi Commercial Dry Cleaning & Steam Boiler Safety Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("DryCleaningSentinel")


class DryCleaningBoilerSafetySentinel:
    """
    Monitors industrial steam boilers and solvent recovery chambers in Nairobi dry cleaning facilities.
    Tracks steam pressure (bar), exhaust temperature, solvent vapor (PCE/Hydrocarbon ppm), and water feed stability.
    """

    def __init__(self, facility_id: str, max_pressure_bar: float = 10.0, max_solvent_ppm: float = 25.0):
        self.facility_id = facility_id
        self.max_pressure_bar = max_pressure_bar
        self.max_solvent_ppm = max_solvent_ppm
        self.alert_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized DryCleaningBoilerSafetySentinel for {{facility_id}} (Max Press: {{max_pressure_bar}} bar)")

    def evaluate_sensor_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates real-time sensor streams from the boiler house and solvent recovery drum.
        """
        timestamp = time.time()
        pressure = float(telemetry.get("steam_pressure_bar", 0.0))
        temp_c = float(telemetry.get("exhaust_temp_c", 0.0))
        solvent_ppm = float(telemetry.get("solvent_vapor_ppm", 0.0))
        water_level_pct = float(telemetry.get("water_feed_level_pct", 100.0))

        status = "OPTIMAL"
        actions = []

        # Pressure Safety Check
        if pressure >= self.max_pressure_bar * 0.9:
            status = "CRITICAL_PRESSURE_WARNING"
            actions.append("TRIGGER_SOLENOID_STEAM_VENT")
            logger.warning(f"[{{self.facility_id}}] HIGH STEAM PRESSURE: {{pressure}} bar!")

        # Solvent Vapor Leak Check (OSHA / NEMA standards)
        if solvent_ppm > self.max_solvent_ppm:
            status = "HAZARDOUS_VAPOR_DETECTED"
            actions.append("ACTIVATE_EMERGENCY_EXHAUST_FANS")
            actions.append("LOCK_SOLVENT_LOADING_DOOR")
            logger.error(f"[{{self.facility_id}}] SOLVENT LEAK DETECTED: {{solvent_ppm}} ppm!")

        # Water Feed Safety (Prevent dry firing)
        if water_level_pct < 20.0:
            status = "BOILER_DRY_FIRE_RISK"
            actions.append("SHUTDOWN_BURNER_ELEMENTS")
            logger.critical(f"[{{self.facility_id}}] LOW WATER LEVEL: {{water_level_pct}}% - SHUTTING DOWN BURNER!")

        assessment = {
            "timestamp": timestamp,
            "facility_id": self.facility_id,
            "status": status,
            "metrics": {
                "pressure_bar": pressure,
                "exhaust_temp_c": temp_c,
                "solvent_ppm": solvent_ppm,
                "water_level_pct": water_level_pct
            },
            "recommended_actions": actions
        }

        if status != "OPTIMAL":
            self.alert_history.append(assessment)

        return assessment

    def audit_report(self) -> Dict[str, Any]:
        """Generates a compliance and safety summary for facility audit logs."""
        return {
            "facility_id": self.facility_id,
            "total_incidents": len(self.alert_history),
            "latest_incidents": self.alert_history[-5:]
        }


if __name__ == "__main__":
    print("[+] Executing DryCleaningBoilerSafetySentinel Test Harness...")
    sentinel = DryCleaningBoilerSafetySentinel(
        facility_id="WESTLANDS_CLEANERS_01",
        max_pressure_bar=12.0,
        max_solvent_ppm=20.0
    )

    # Test normal reading
    norm_telemetry = {
        "steam_pressure_bar": 6.5,
        "exhaust_temp_c": 145.0,
        "solvent_vapor_ppm": 4.2,
        "water_level_pct": 85.0
    }
    res1 = sentinel.evaluate_sensor_telemetry(norm_telemetry)
    print(f"Normal Run Status: {{res1['status']}}")

    # Test hazardous vapor reading
    hazard_telemetry = {
        "steam_pressure_bar": 11.5,
        "exhaust_temp_c": 180.0,
        "solvent_vapor_ppm": 34.8,
        "water_level_pct": 15.0
    }
    res2 = sentinel.evaluate_sensor_telemetry(hazard_telemetry)
    print(f"Hazardous Run Status: {{res2['status']}} | Actions: {{res2['recommended_actions']}}")
    print("[+] Test Harness Completed Successfully.")
