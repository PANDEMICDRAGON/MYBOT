"""Nairobi Municipal Composting & Biofilter Odor Mitigation Sentinel

Monitors temperature, moisture, ammonia (NH3), hydrogen sulfide (H2S), and airflow
across Nairobi peri-urban organic composting windrows and woodchip biofilters.
Ensures compliance with environmental odor thresholds and microbial degradation efficiency.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("CompostBiofilterSentinel")

@dataclass
class BiofilterSensorReading:
    node_id: str
    temperature_celsius: float
    moisture_percentage: float
    ammonia_ppm: float
    hydrogen_sulfide_ppm: float
    airflow_cfm: float
    timestamp: float = field(default_factory=time.time)

class CompostingBiofilterEngine:
    def __init__(self, target_moisture: float = 55.0, max_nh3_ppm: float = 25.0, max_h2s_ppm: float = 10.0):
        self.target_moisture = target_moisture
        self.max_nh3_ppm = max_nh3_ppm
        self.max_h2s_ppm = max_h2s_ppm
        self.history: List[BiofilterSensorReading] = []

    def ingest_reading(self, reading: BiofilterSensorReading) -> Dict[str, Any]:
        """Ingests a sensor payload and evaluates biofilter health and odor risk."""
        self.history.append(reading)
        alerts = []
        status = "OPTIMAL"

        # Temperature checks (Thermophilic phase target: 55C - 65C)
        if reading.temperature_celsius < 45.0:
            status = "SUBOPTIMAL"
            alerts.append(f"Low thermophilic temp ({reading.temperature_celsius}°C). Pathogen kill incomplete.")
        elif reading.temperature_celsius > 75.0:
            status = "CRITICAL_WARNING"
            alerts.append(f"Exothermic overheating ({reading.temperature_celsius}°C). Risk of spontaneous combustion.")

        # Moisture checks
        if reading.moisture_percentage < 40.0:
            status = "SUBOPTIMAL"
            alerts.append(f"Compost too dry ({reading.moisture_percentage}%). Microbial activity stalling.")
        elif reading.moisture_percentage > 70.0:
            status = "CRITICAL_WARNING"
            alerts.append(f"Waterlogged compost ({reading.moisture_percentage}%). Anaerobic pockets forming.")

        # Gas breakthrough checks (Odor & toxicity metrics)
        if reading.ammonia_ppm > self.max_nh3_ppm:
            status = "ODOR_BREACH"
            alerts.append(f"High Ammonia breakthrough ({reading.ammonia_ppm} ppm > limit {self.max_nh3_ppm} ppm).")

        if reading.hydrogen_sulfide_ppm > self.max_h2s_ppm:
            status = "ODOR_BREACH"
            alerts.append(f"High Hydrogen Sulfide breakthrough ({reading.hydrogen_sulfide_ppm} ppm > limit {self.max_h2s_ppm} ppm).")

        # Airflow / media pressure check
        if reading.airflow_cfm < 50.0:
            status = "SUBOPTIMAL"
            alerts.append(f"Biofilter airflow insufficient ({reading.airflow_cfm} CFM). Channeling or clogging suspected.")

        logger.info(f"Evaluated node {reading.node_id}: Status -> {status}, Alerts -> {len(alerts)}")
        return {
            "node_id": reading.node_id,
            "status": status,
            "alerts": alerts,
            "timestamp": reading.timestamp
        }

    def generate_remediation_plan(self, evaluation: Dict[str, Any]) -> str:
        """Generates automated operational instructions for Nairobi facility operators."""
        status = evaluation["status"]
        if status == "OPTIMAL":
            return "All systems nominal. Maintain current leachate irrigation and blower schedule."
        elif status == "ODOR_BREACH":
            return "ACTION REQUIRED: Increase biofilter moisture spray, inject activated carbon dosing, and check blower speed."
        elif status == "CRITICAL_WARNING":
            return "EMERGENCY ACTION: Turn windrow immediately to dissipate heat/anaerobic pockets and adjust pressure valves."
        else:
            return "ADVISORY: Adjust moisture nozzles and verify organic mix carbon-to-nitrogen (C:N) ratio."

if __name__ == "__main__":
    print("--- Executing Nairobi Municipal Composting & Biofilter Sentinel Test Harness ---")
    engine = CompostingBiofilterEngine()
    sample_reading = BiofilterSensorReading(
        node_id="KASARANI_COMPOST_UNIT_04",
        temperature_celsius=68.5,
        moisture_percentage=58.0,
        ammonia_ppm=12.0,
        hydrogen_sulfide_ppm=4.5,
        airflow_cfm=120.0
    )
    eval_result = engine.ingest_reading(sample_reading)
    print(f"Evaluation Result: {eval_result}")
    remediation = engine.generate_remediation_plan(eval_result)
    print(f"Remediation Plan: {remediation}")
    print("--- Sentinel Test Complete ---")
