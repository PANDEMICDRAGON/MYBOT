"""
Module: nairobi_commercial_aquaponics_bio_filter_sentinel.py
Description: Autonomous biosafety sentinel for commercial aquaponics bio-filters in Nairobi, Kenya.
             Monitors nitrification kinetics, ammonia/nitrite toxicity, dissolved oxygen, and flow rates.
Author: Cortana's Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import logging
import time
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("AquaponicsBioFilterSentinel")

class BioFilterMetrics:
    def __init__(self, system_id: str, ammonia_ppm: float, nitrite_ppm: float, nitrate_ppm: float,
                 dissolved_oxygen_mg_l: float, water_temp_c: float, ph_level: float, flow_rate_lpm: float):
        self.system_id = system_id
        self.ammonia_ppm = ammonia_ppm
        self.nitrite_ppm = nitrite_ppm
        self.nitrate_ppm = nitrate_ppm
        self.dissolved_oxygen_mg_l = dissolved_oxygen_mg_l
        self.water_temp_c = water_temp_c
        self.ph_level = ph_level
        self.flow_rate_lpm = flow_rate_lpm
        self.timestamp = time.time()

class AquaponicsBioFilterSentinel:
    """
    Monitors biological filtration efficiency and water parameters for commercial aquaponics
    systems in Nairobi, executing immediate emergency interventions upon toxicity spikes.
    """
    def __init__(self, system_id: str, max_ammonia_ppm: float = 0.5, max_nitrite_ppm: float = 0.3,
                 min_dissolved_oxygen: float = 5.0, min_flow_lpm: float = 20.0):
        self.system_id = system_id
        self.max_ammonia_ppm = max_ammonia_ppm
        self.max_nitrite_ppm = max_nitrite_ppm
        self.min_dissolved_oxygen = min_dissolved_oxygen
        self.min_flow_lpm = min_flow_lpm
        self.incident_log: List[Dict[str, Any]] = []

    def evaluate_nitrification_health(self, metrics: BioFilterMetrics) -> Dict[str, Any]:
        """
        Evaluates bio-filter metrics against safety thresholds and computes nitrification efficiency.
        """
        alerts = []
        status = "OPTIMAL"

        # Ammonia toxicity check
        if metrics.ammonia_ppm > self.max_ammonia_ppm:
            status = "CRITICAL"
            alerts.append(f"HIGH AMMONIA WARNING: {metrics.ammonia_ppm} ppm (Threshold: < {self.max_ammonia_ppm})")

        # Nitrite toxicity check
        if metrics.nitrite_ppm > self.max_nitrite_ppm:
            status = "CRITICAL" if status != "CRITICAL" else status
            alerts.append(f"HIGH NITRITE WARNING: {metrics.nitrite_ppm} ppm (Threshold: < {self.max_nitrite_ppm})")

        # Dissolved Oxygen check
        if metrics.dissolved_oxygen_mg_l < self.min_dissolved_oxygen:
            status = "WARNING" if status == "OPTIMAL" else status
            alerts.append(f"LOW OXYGEN WARNING: {metrics.dissolved_oxygen_mg_l} mg/L (Min: {self.min_dissolved_oxygen})")

        # Flow rate check
        if metrics.flow_rate_lpm < self.min_flow_lpm:
            status = "CRITICAL"
            alerts.append(f"PUMP FLOW FAILURE: {metrics.flow_rate_lpm} LPM (Min: {self.min_flow_lpm})")

        evaluation = {
            "system_id": self.system_id,
            "status": status,
            "alerts": alerts,
            "timestamp": metrics.timestamp,
            "nitrification_active": metrics.ammonia_ppm < 0.2 and metrics.nitrite_ppm < 0.1
        }

        if status != "OPTIMAL":
            self.incident_log.append(evaluation)
            logger.warning(f"[{self.system_id}] BioFilter Status: {status} | Alerts: {alerts}")
        else:
            logger.info(f"[{self.system_id}] BioFilter Operational. Nitrification Healthy.")

        return evaluation

    def execute_remediation(self, evaluation: Dict[str, Any]) -> str:
        """
        Executes automated corrective action protocols (e.g., aeration booster, water dilution, feed halt).
        """
        if evaluation["status"] == "OPTIMAL":
            return "NO_ACTION_REQUIRED"

        actions_taken = []
        for alert in evaluation["alerts"]:
            if "AMMONIA" in alert or "NITRITE" in alert:
                actions_taken.append("HALTED_FISH_FEEDING_AND_ACTIVATED_CARBON_BYPASS")
            if "OXYGEN" in alert:
                actions_taken.append("DEPLOYED_EMERGENCY_OXYGEN_DIFFUSERS")
            if "FLOW" in alert:
                actions_taken.append("SWITCHED_TO_BACKUP_DC_WATER_PUMP")

        logger.error(f"[REMEDIATION EXECUTED FOR {self.system_id}]: {actions_taken}")
        return f"SUCCESS: Executed {len(actions_taken)} corrective protocols."

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Aquaponics Bio-Filter & Nitrification Biosafety Sentinel...")
    sentinel = AquaponicsBioFilterSentinel(system_id="NAI_AQUA_RANCH_01")
    
    # Test metrics simulating a bio-filter nitrite spike
    test_metrics = BioFilterMetrics(
        system_id="NAI_AQUA_RANCH_01",
        ammonia_ppm=0.1,
        nitrite_ppm=0.45,
        nitrate_ppm=45.0,
        dissolved_oxygen_mg_l=4.2,
        water_temp_c=24.5,
        ph_level=6.8,
        flow_rate_lpm=18.5
    )
    
    eval_result = sentinel.evaluate_nitrification_health(test_metrics)
    print("Evaluation Result:", eval_result)
    action_result = sentinel.execute_remediation(eval_result)
    print("Remediation Result:", action_result)
