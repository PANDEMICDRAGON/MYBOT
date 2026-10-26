"""
Nairobi Commercial Bee Venom Extraction & Apiary Biosafety Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

 Monitors and controls commercial apitoxin (bee venom) collection cycles via safe
 electrical stimulation grids, monitors hive environmental telemetry, detects
 stress harmonics through acoustic and vibration sensors, and protects colonies.
"""

import time
import logging
import json
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BeeVenomSentinel")

class BeeVenomSentinel:
    """Manages commercial apitoxin extraction cycles and hive biosafety."""

    def __init__(self, hive_id: str, max_voltage_mv: int = 3500, max_temp_c: float = 38.0):
        self.hive_id = hive_id
        self.max_voltage_mv = max_voltage_mv
        self.max_temp_c = max_temp_c
        self.active_extraction = False
        self.total_venom_harvested_mg = 0.0
        self.emergency_lockout = False

    def evaluate_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates hive telemetry and returns safety actions."""
        temp = telemetry.get("temperature_c", 34.0)
        humidity = telemetry.get("humidity_pct", 60.0)
        vibration_hz = telemetry.get("vibration_hz", 150.0)
        co2_ppm = telemetry.get("co2_ppm", 450)

        actions = {"status": "NORMAL", "voltage_applied_mv": 0, "warning": None}

        if self.emergency_lockout:
            return {"status": "LOCKED_OUT", "voltage_applied_mv": 0, "warning": "Emergency lockout active due to prior anomaly."}

        # Check biosafety thresholds
        if temp > self.max_temp_c or co2_ppm > 1200:
            self.emergency_lockout = True
            self.active_extraction = False
            actions["status"] = "EMERGENCY_SHUTDOWN"
            actions["warning"] = "Critical hive stress detected: Temperature or CO2 exceeded safe thresholds."
            logger.warning(f"[{self.hive_id}] EMERGENCY SHUTDOWN TRIGGERED: Temp={temp}C, CO2={co2_ppm}ppm")
            return actions

        if vibration_hz > 450.0:
            actions["status"] = "PAUSED"
            actions["warning"] = "High agitation frequency detected. Halting extraction to protect queen and brood."
            return actions

        if self.active_extraction:
            actions["voltage_applied_mv"] = self.max_voltage_mv
            actions["status"] = "HARVESTING"
            # Simulate venom deposition on glass plate (mg)
            self.total_venom_harvested_mg += 0.05

        actions["total_harvest_mg"] = round(self.total_venom_harvested_mg, 2)
        return actions

    def start_extraction_cycle(self, duration_seconds: int = 60) -> bool:
        """Initiates a controlled venom collection cycle."""
        if self.emergency_lockout:
            logger.error(f"[{self.hive_id}] Cannot start extraction: System in emergency lockout.")
            return False
        self.active_extraction = True
        logger.info(f"[{self.hive_id}] Starting venom extraction cycle for {duration_seconds}s at {self.max_voltage_mv}mV.")
        return True

    def stop_extraction_cycle(self):
        """Stops the venom collection cycle."""
        self.active_extraction = False
        logger.info(f"[{self.hive_id}] Venom extraction cycle stopped.")

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Bee Venom Extraction Sentinel...")
    sentinel = BeeVenomSentinel(hive_id="HIVE_KAREN_04")
    
    # Test normal telemetry
    telemetry_normal = {"temperature_c": 34.5, "humidity_pct": 55.0, "vibration_hz": 120.0, "co2_ppm": 500}
    sentinel.start_extraction_cycle(30)
    res = sentinel.evaluate_telemetry(telemetry_normal)
    print("Normal Telemetry Evaluation:", json.dumps(res, indent=2))
    
    # Test stress telemetry
    telemetry_stress = {"temperature_c": 39.2, "humidity_pct": 75.0, "vibration_hz": 500.0, "co2_ppm": 1400}
    res_stress = sentinel.evaluate_telemetry(telemetry_stress)
    print("Stress Telemetry Evaluation:", json.dumps(res_stress, indent=2))
    print("Sentinel verification complete.")
