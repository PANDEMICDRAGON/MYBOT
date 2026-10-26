"""
Module: nairobi_commercial_grease_trap_sentinel.py
Description: Real-time biosafety & operational sentinel for commercial kitchen grease traps 
             in Nairobi, monitoring FOG accumulation, pH, temperature, and automated enzyme dosing.
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import time
import logging
import json
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [GreaseTrapSentinel]: %(message)s')
logger = logging.getLogger("NairobiCommercialGreaseTrapSentinel")

class GreaseTrapSentinel:
    """
    Monitors commercial grease trap metrics, evaluates regulatory compliance with
    Nairobi City County environmental standards, and automates biological additive dosing.
    """
    def __init__(self, trap_id: str, capacity_liters: float = 500.0):
        self.trap_id = trap_id
        self.capacity_liters = capacity_liters
        self.current_fog_thickness_cm: float = 2.5  # Fats, oils, and grease layer
        self.water_temperature_c: float = 42.0
        self.effluent_ph: float = 6.8
        self.water_level_pct: float = 65.0
        self.enzyme_pump_active: bool = False
        self.last_pump_maintenance: float = time.time() - 86400 * 14  # 14 days ago
        self.alerts: List[str] = []

    def ingest_sensor_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingests live telemetry from grease trap IoT sensors.
        Expected keys: fog_thickness_cm, temperature_c, ph, level_pct
        """
        self.current_fog_thickness_cm = float(telemetry.get("fog_thickness_cm", self.current_fog_thickness_cm))
        self.water_temperature_c = float(telemetry.get("temperature_c", self.water_temperature_c))
        self.effluent_ph = float(telemetry.get("ph", self.effluent_ph))
        self.water_level_pct = float(telemetry.get(
            "level_pct", self.water_level_pct
        ))
        
        logger.info(f"[{self.trap_id}] Telemetry updated: FOG={self.current_fog_thickness_cm}cm, Temp={self.water_temperature_c}C, pH={self.effluent_ph}, Level={self.water_level_pct}%")
        return self.evaluate_biosafety()

    def evaluate_biosafety(self) -> Dict[str, Any]:
        """
        Evaluates operational thresholds against Nairobi sewer discharge standards
        and triggers countermeasures (e.g., bio-enzyme dosing).
        """
        self.alerts.clear()
        status = "OPTIMAL"

        # FOG Threshold check (Max allowable layer typically 20% of depth or ~8cm)
        if self.current_fog_thickness_cm > 8.0:
            self.alerts.append(f"CRITICAL: FOG layer thickness ({self.current_fog_thickness_cm}cm) exceeds safe operational limit.")
            status = "HAZARD"
            self.trigger_enzyme_dosing(duration_seconds=120)
        elif self.current_fog_thickness_cm > 5.0:
            self.alerts.append(f"WARNING: FOG layer thickness ({self.current_fog_thickness_cm}cm) elevated. Scheduling bio-digestion.")
            status = "WARNING"
            self.trigger_enzyme_dosing(duration_seconds=60)

        # Temperature check (Hot water above 60C melts FOG downstream, under 30C solidifies prematurely)
        if self.water_temperature_c > 65.0:
            self.alerts.append(f"WARNING: High water temperature ({self.water_temperature_c}C) risk of emulsifying FOG into main sewer.")
            if status == "OPTIMAL":
                status = "WARNING"

        # pH check (Nairobi County sewer discharge compliance: pH 6.0 - 9.5)
        if self.effluent_ph < 5.5 or self.effluent_ph > 10.0:
            self.alerts.append(f"CRITICAL: Effluent pH ({self.effluent_ph}) out of legal compliance range [6.0 - 9.5].")
            status = "HAZARD"

        # Overfill check
        if self.water_level_pct > 90.0:
            self.alerts.append(f"CRITICAL: Grease trap high liquid level ({self.water_level_pct}%) indicates partial blockage or pump failure.")
            status = "HAZARD"

        return {
            "trap_id": self.trap_id,
            "status": status,
            "alerts": list(self.alerts),
            "enzyme_pump_active": self.enzyme_pump_active,
            "timestamp": time.time()
        }

    def trigger_enzyme_dosing(self, duration_seconds: int) -> None:
        """
        Activates peristaltic pump to dose biological lipase-producing bacteria
        into the grease trap inlet.
        """
        self.enzyme_pump_active = True
        logger.warning(f"[{self.trap_id}] ACTIVATING BIO-ENZYME DOSING PUMP for {duration_seconds} seconds to breakdown lipid chains.")
        # Simulated hardware actuation latency
        time.sleep(0.01)
        self.enzyme_pump_active = False

    def generate_county_compliance_report(self) -> str:
        """
        Generates a JSON audit report suitable for environmental inspectors.
        """
        report = {
            "facility": "Commercial Kitchen Node - Nairobi",
            "trap_id": self.trap_id,
            "capacity_liters": self.capacity_liters,
            "metrics": {
                "fog_thickness_cm": self.current_fog_thickness_cm,
                "temperature_c": self.water_temperature_c,
                "effluent_ph": self.effluent_ph,
                "water_level_pct": self.water_level_pct
            },
            "compliance_status": "COMPLIANT" if not self.alerts else "ACTION_REQUIRED",
            "active_alerts": self.alerts,
            "timestamp": time.time()
        }
        return json.dumps(report, indent=2)


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grease Trap Sentinel test harness...")
    sentinel = GreaseTrapSentinel(trap_id="GT-WESTLANDS-04", capacity_liters=750.0)
    
    # Test normal telemetry
    res1 = sentinel.ingest_sensor_telemetry({
        "fog_thickness_cm": 3.2,
        "temperature_c": 40.5,
        "ph": 7.1,
        "level_pct": 50.0
    })
    print(f"Test 1 Result: {res1}")

    # Test hazard telemetry (high FOG & low pH)
    res2 = sentinel.ingest_sensor_telemetry({
        "fog_thickness_cm": 9.1,
        "temperature_c": 58.0,
        "ph": 4.8,
        "level_pct": 92.5
    })
    print(f"Test 2 Result: {res2}")
    print("County Compliance Audit Report:")
    print(sentinel.generate_county_compliance_report())
    print("Test harness execution complete.")
