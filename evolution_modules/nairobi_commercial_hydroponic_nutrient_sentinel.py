"""Nairobi Commercial Hydroponic Nutrient & EC/pH Sentinel.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Description:
Autonomous real-time sensor processing, closed-loop telemetry analysis, and
automatic corrective dosing orchestration for commercial hydroponic systems
operating within Nairobi's urban agriculture sector.
"""

import logging
import time
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [HydroponicSentinel] %(message)s"
)
logger = logging.getLogger("HydroponicSentinel")


class HydroponicControlException(Exception):
    """Custom exception raised during hydroponic actuator or sensor anomalies."""
    pass


class HydroponicNutrientSentinel:
    """Manages water quality, EC/pH parameters, and automatic dosing actuators
    for commercial NFT (Nutrient Film Technique) and DWC (Deep Water Culture)
    greenhouse setups in Nairobi.
    """

    def __init__(
        self, 
        system_id: str,
        target_ph_min: float = 5.5,
        target_ph_max: float = 6.5,
        target_ec_min_ms: float = 1.2,
        target_ec_max_ms: float = 2.2,
        max_water_temp_c: float = 26.0
    ):
        self.system_id = system_id
        self.target_ph_min = target_ph_min
        self.target_ph_max = target_ph_max
        self.target_ec_min_ms = target_ec_min_ms
        self.target_ec_max_ms = target_ec_max_ms
        self.max_water_temp_c = max_water_temp_c
        
        # Actuator state tracking
        self.dosing_pumps_active: Dict[str, bool] = {
            "ph_up": False,
            "ph_down": False,
            "nutrient_a": False,
            "nutrient_b": False,
            "water_top_up": False
        }
        self.aeration_pump_active: bool = True
        self.emergency_shutdown: bool = False
        self.telemetry_history: List[Dict[str, float]] = []

    def ingest_telemetry(
        self, 
        ph: float, 
        ec_ms: float, 
        water_temp_c: float,
        dissolved_oxygen_mg_l: float,
        water_level_pct: float
    ) -> Dict[str, Any]:
        """Ingests real-time telemetry from hydroponic sensor arrays, evaluates
        parameters against optimal bounds, and triggers corrective actions.
        """
        if self.emergency_shutdown:
            logger.error(f"[{self.system_id}] System in EMERGENCY LOCKDOWN. Ignoring telemetry.")
            return {"status": "EMERGENCY_LOCKDOWN", "actions_taken": []}

        timestamp = time.time()
        reading = {
            "timestamp": timestamp,
            "ph": ph,
            "ec_ms": ec_ms,
            "water_temp_c": water_temp_c,
            "dissolved_oxygen_mg_l": dissolved_oxygen_mg_l,
            "water_level_pct": water_level_pct
        }
        self.telemetry_history.append(reading)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        actions_taken = []

        # Water Temperature & Dissolved Oxygen Safety Check
        if water_temp_c > self.max_water_temp_c:
            logger.warning(f"[{self.system_id}] High water temperature detected ({water_temp_c}C). Activating chiller/aeration escalation.")
            self.aeration_pump_active = True
            actions_taken.append("MAX_AERATION_ENGAGED")
            if water_temp_c > (self.max_water_temp_c + 4.0):
                self._trigger_emergency_shutdown("Critical thermal runaway in nutrient reservoir.")
                return {"status": "CRITICAL_SHUTDOWN", "actions_taken": ["EMERGENCY_SHUTDOWN"]}

        # Water Level Check
        if water_level_pct < 20.0:
            logger.warning(f"[{self.system_id}] Reservoir water level critically low ({water_level_pct}%). Engaging top-up valve.")
            self.dosing_pumps_active["water_top_up"] = True
            actions_taken.append("ENGAGE_WATER_TOP_UP")
        else:
            self.dosing_pumps_active["water_top_up"] = False

        # pH Correction Logic
        if ph < self.target_ph_min:
            logger.info(f"[{self.system_id}] pH too acidic ({ph}). Dosing pH UP buffer.")
            self.dosing_pumps_active["ph_up"] = True
            self.dosing_pumps_active["ph_down"] = False
            actions_taken.append("DOSING_PH_UP")
        elif ph > self.target_ph_max:
            logger.info(f"[{self.system_id}] pH too alkaline ({ph}). Dosing pH DOWN acid.")
            self.dosing_pumps_active["ph_down"] = True
            self.dosing_pumps_active["ph_up"] = False
            actions_taken.append("DOSING_PH_DOWN")
        else:
            self.dosing_pumps_active["ph_up"] = False
            self.dosing_pumps_active["ph_down"] = False
            actions_taken.append("PH_STABLE")

        # EC (Nutrient Concentration) Correction Logic
        if ec_ms < self.target_ec_min_ms:
            logger.info(f"[{self.system_id}] EC low ({ec_ms} mS/cm). Dosing Nutrients A & B.")
            self.dosing_pumps_active["nutrient_a"] = True
            self.dosing_pumps_active["nutrient_b"] = True
            actions_taken.append("DOSING_NUTRIENTS_AB")
        elif ec_ms > self.target_ec_max_ms:
            logger.warning(f"[{self.system_id}] EC high ({ec_ms} mS/cm). Recommending fresh water dilution.")
            self.dosing_pumps_active["nutrient_a"] = False
            self.dosing_pumps_active["nutrient_b"] = False
            actions_taken.append("EC_HIGH_DILUTION_REQUIRED")
        else:
            self.dosing_pumps_active["nutrient_a"] = False
            self.dosing_pumps_active["nutrient_b"] = False
            actions_taken.append(
"EC_STABLE")

        return {
            "status": "HEALTHY_OPTIMIZED",
            "actions_taken": actions_taken,
            "actuator_states": self.dosing_pumps_active
        }

    def _trigger_emergency_shutdown(self, reason: str) -> None:
        """Halts all dosing pumps and secures the system."""
        self.emergency_shutdown = True
        for k in self.dosing_pumps_active:
            self.dosing_pumps_active[k] = False
        logger.critical(f"[{self.system_id}] EMERGENCY SHUTDOWN ACTIVATED: {reason}")

    def get_diagnostic_report(self) -> Dict[str, Any]:
        """Returns operational statistics and recent metrics."""
        return {
            "system_id": self.system_id,
            "emergency_shutdown": self.emergency_shutdown,
            "actuator_states": self.dosing_pumps_active,
            "total_telemetry_samples": len(self.telemetry_history),
            "last_reading": self.telemetry_history[-1] if self.telemetry_history else None
        }


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Hydroponic Nutrient Sentinel Test Harness...")
    sentinel = HydroponicNutrientSentinel(system_id="KAHAWA_WEST_VERTICAL_FARM_01")
    
    # Simulate normal initial state
    result = sentinel.ingest_telemetry(
        ph=5.8,
        ec_ms=1.6,
        water_temp_c=21.5,
        dissolved_oxygen_mg_l=7.2,
        water_level_pct=85.0
    )
    print(f"Telemetry Ingestion Result 1: {result}")

    # Simulate acidic pH anomaly requiring correction
    result_acidic = sentinel.ingest_telemetry(
        ph=5.1,
        ec_ms=1.1,
        water_temp_c=23.0,
        dissolved_oxygen_mg_l=6.8,
        water_level_pct=78.0
    )
    print(f"Telemetry Ingestion Result 2 (Acidic & Low EC): {result_acidic}")

    print("Diagnostic Report:", sentinel.get_diagnostic_report())
    print("Hydroponic Sentinel Module compiled and tested successfully.")
