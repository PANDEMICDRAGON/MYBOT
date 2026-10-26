"""
Nairobi Commercial Aquaponics Closed-Loop & Nutrient Biosafety Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Monitors and optimizes integrated fish and plant production loops, ensuring water
quality parameters stay within optimal biological thresholds.
"""

import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [AquaponicsSentinel]: %(message)s')


class AquaponicsBiosafetySentinel:
    """
    Manages sensor telemetry from aquaculture tanks and hydroponic grow beds,
    triggering automated biofilter adjustments and aeration overrides.
    """

    def __init__(self, system_id: str, target_fish_species: str = "Nile Tilapia") -> None:
        self.system_id = system_id
        self.species = target_fish_species
        self.telemetry_history: List[Dict[str, Any]] = []
        self.alert_count = 0

    def ingest_sensor_data(self, data: Dict[str, float]) -> Dict[str, Any]:
        """
        Ingests metrics: water_temp_c, dissolved_o2_mg_l, ph_level,
        total_ammonia_mg_l, nitrite_mg_l, nitrate_mg_l, water_flow_l_min.
        """
        timestamp = time.time()
        record = {"timestamp": timestamp, **data}
        self.telemetry_history.append(record)

        diagnostics = self._analyze_biological_balance(data)
        return {
            "system_id": self.system_id,
            "timestamp": timestamp,
            "status": diagnostics["status"],
            "actions_taken": diagnostics["actions"],
            "warnings": diagnostics["warnings"]
        }

    def _analyze_biological_balance(self, data: Dict[str, float]) -> Dict[str, Any]:
        actions = []
        warnings = []
        status = "OPTIMAL"

        temp = data.get("water_temp_c", 24.0)
        do2 = data.get("dissolved_o2_mg_l", 6.5)
        ph = data.get("ph_level", 7.0)
        ammonia = data.get("total_ammonia_mg_l", 0.05)
        nitrite = data.get("nitrite_mg_l", 0.02)
        nitrate = data.get("nitrate_mg_l", 40.0)
        flow = data.get("water_flow_l_min", 50.0)

        # Temperature checks for Tilapia
        if temp < 20.0:
            status = "WARNING"
            warnings.warn(f"Water temperature low ({temp}°C). Metabolic rate dropping.")
            actions.append("ACTIVATE_TANK_HEATER_ELEMENT")
        elif temp > 28.0:
            status = "CRITICAL"
            warnings.append(f"Water temperature critical ({temp}°C). Oxygen solubility risk.")
            actions.append("ACTIVATE_EMERGENCY_CHILLER_AND_AERATOR")

        # Dissolved Oxygen checks
        if do2 < 5.0:
            status = "CRITICAL"
            warnings.append(f"Dissolved Oxygen dangerously low ({do2} mg/L).")
            actions.append("MAX_POWER_OXYGEN_CONCENTRATOR")

        # pH Checks (Ideal 6.8 - 7.2 for nitrifying bacteria and fish)
        if ph < 6.5:
            status = "WARNING"
            warnings.append(f"pH acidic ({ph}). Nitrification slowing down.")
            actions.append("DOSING_CALCIUM_CARBONATE_BUFFER")
        elif ph > 7.5:
            status = "WARNING"
            warnings.append(f"pH alkaline ({ph}). Ammonia toxicity risk increased.")
            actions.append("DOSING_ORGANIC_PH_DOWN")

        # Ammonia & Nitrite Toxicity check
        if ammonia > 0.5 or nitrite > 0.5:
            status = "CRITICAL"
            warnings.append("Biofilter failure detected! High Ammonia/Nitrite levels.")
            actions.append("DIVERT_FLOW_TO_EMERGENCY_BIO_REACTOR")
            actions.append(
                "REDUCE_FISH_FEEDING_RATE_50_PERCENT"
            )

        if flow < 30.0:
            status = "CRITICAL"
            warnings.append(f"Low water circulation ({flow} L/min).")
            actions.append("FAILOVER_TO_BACKUP_DC_WATER_PUMP")

        if status == "CRITICAL":
            self.alert_count += 1

        return {
            "status": status,
            "actions": actions,
            "warnings": warnings
        }

    def get_system_summary(self) -> Dict[str, Any]:
        return {
            "system_id": self.system_id,
            "species": self.species,
            "total_telemetry_records": len(self.telemetry_history),
            "total_critical_alerts": self.alert_count
        }


if __name__ == "__main__":
    logging.info("Initializing Nairobi Commercial Aquaponics Sentinel Test Harness...")
    sentinel = AquaponicsBiosafetySentinel(system_id="AQUA-NRB-01", target_fish_species="Nile Tilapia")

    test_telemetry = {
        "water_temp_c": 26.5,
        "dissolved_o2_mg_l": 6.2,
        "ph_level": 6.9,
        "total_ammonia_mg_l": 0.02,
        "nitrite_mg_l": 0.01,
        "nitrate_mg_l": 35.0,
        "water_flow_l_min": 55.0
    }

    result = sentinel.ingest_sensor_data(test_telemetry)
    logging.info(f"Telemetry Ingest Result: {result}")

    stress_telemetry = {
        "water_temp_c": 29.2,
        "dissolved_o2_mg_l": 4.1,
        "ph_level": 6.1,
        "total_ammonia_mg_l": 0.8,
        "nitrite_mg_l": 0.6,
        "nitrate_mg_l": 90.0,
        "water_flow_l_min": 22.0
    }

    stress_result = sentinel.ingest_sensor_data(stress_telemetry)
    logging.info(f"Stress Telemetry Result: {stress_result}")
    logging.info(f"System Summary: {sentinel.get_system_summary()}")
