"""
Nairobi Commercial Hydroponic Nutrient & Electrical Conductivity (EC) Biosafety Sentinel
Designed for real-time monitoring and autonomous corrective dosing of urban commercial
hydroponic installations across Nairobi, Kenya.
"""

import time
import logging
import json
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HydroponicSentinel")


class HydroponicBiosafetySentinel:
    """
    Monitors nutrient solution parameters in commercial hydroponic systems,
    evaluates EC/TDS levels, pH, temperature, and triggers automated corrective
    dosing or operator alerts.
    """

    def __init__(self, system_id: str, crop_type: str):
        self.system_id = system_id
        self.crop_type = crop_type
        self.telemetry_history: List[Dict[str, Any]] = []
        self.alert_log: List[str] = []

    def ingest_telemetry(
        self,
        ec_msc_cm: float,
        ph_level: float,
        water_temp_c: float,
        dissolved_oxygen_mg_l: float,
        water_level_pct: float
    ) -> Dict[str, Any]:
        """
        Ingests sensor telemetry and runs safety bounds validation.
        "" - Target EC for leafy greens (e.g., Lettuce/Kale/Sukuma Wiki): 1.2 - 2.0 mS/cm
        - Target pH: 5.5 - 6.5
        - Target Temp: 18.0 - 24.0 C
        """
        timestamp = time.time()
        status = "OPTIMAL"
        actions_required: List[str] = []

        # EC Assessment
        if ec_msc_cm < 1.0:
            status = "WARNING"
            actions_required.append("INJECT_NUTRIENT_CONCENTRATE_A_B")
            self.alert_log.append(f"[{timestamp}] Low EC detected: {ec_msc_cm} mS/cm")
        elif ec_msc_cm > 2.5:
            status = "CRITICAL"
            actions_required.append("DILUTE_WITH_RO_WATER")
            self.alert_log.append(f"[{timestamp}] High EC detected (Risk of root burn): {ec_msc_cm} mS/cm")

        # pH Assessment
        if ph_level < 5.2:
            status = "WARNING" if status != "CRITICAL" else "CRITICAL"
            actions_required.append("DOSING_PH_UP")
            self.alert_log.append(f"[{timestamp}] Low pH detected: {ph_level}")
        elif ph_level > 7.0:
            status = "WARNING" if status != "CRITICAL" else "CRITICAL"
            actions_required.append("DOSING_PH_DOWN")
            self.alert_log.append(f"[{timestamp}] High pH detected: {ph_level}")

        # Temperature Assessment
        if water_temp_c > 26.0:
            status = "CRITICAL"
            actions_required.append("ACTIVATE_CHILLER_AND_AERATION")
            self.alert_log.append(f"[{timestamp}] High water temperature: {water_temp_c}C (Pythium risk)")

        # Water Level Assessment
        if water_level_pct < 20.0:
            status = "CRITICAL"
            actions_required.append("EMERGENCY_RESERVOIR_REFILL")
            self.alert_log.append(f"[{timestamp}] Low reservoir water level: {water_level_pct}%")

        record = {
            "timestamp": timestamp,
            "system_id": self.system_id,
            "crop_type": self.crop_type,
            "ec_msc_cm": ec_msc_cm,
            "ph_level": ph_level,
            "water_temp_c": water_temp_c,
            "dissolved_oxygen_mg_l": dissolved_oxygen_mg_l,
            "water_level_pct": water_level_pct,
            "status": status,
            "actions_required": actions_required
        }

        self.telemetry_history.append(record)
        return record

    def get_audit_summary(self) -> Dict[str, Any]:
        """Returns summary of sensor telemetry and cumulative alerts."""
        return {
            "system_id": self.system_id,
            "total_readings": len(self.telemetry_history),
            "active_alerts": len(self.alert_log),
            "last_status": self.telemetry_history[-1] if self.telemetry_history else None
        }


if __name__ == "__main__":
    sentinel = HydroponicBiosafetySentinel(system_id="NBO-HYDRA-01", crop_type="Sukuma-Wiki-Vertical")
    
    # Simulate optimal telemetry
    res1 = sentinel.ingest_telemetry(1.6, 6.0, 20.5, 7.2, 85.0)
    logger.info(f"Telemetry 1: {json.dumps(res1, indent=2)}")

    # Simulate nutrient depletion and acidic drop
    res2 = sentinel.ingest_telemetry(0.8, 4.9, 27.1, 4.5, 15.0)
    logger.info(f"Telemetry 2: {json.dumps(res2, indent=2)}")

    summary = sentinel.get_audit_summary()
    logger.info(f"Audit Summary: {json.dumps(summary, indent=2)}")
