"""Nairobi Commercial Vermicompost & Earthworm Biosafety Sentinel

Monitors parameters for large-scale vermicomposting beds (e.g., Eisenia fetida setups)
in Nairobi, Kenya. Tracks bed temperature, moisture content, pH balance, and
leachate heavy-metal risks to ensure optimal organic fertilizer conversion.
"""

import json
import logging
import random
import time
from typing import Dict, Any, List

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [VermicompostSentinel]: %(message)s"
)
logger = logging.getLogger("VermicompostSentinel")


class CommercialVermicompostSentinel:
    """
    Autonomous biosafety and telemetry sentinel for commercial worm-farming and
    organic composting operations across Nairobi agricultural zones.
    """
    
    def __init__(self, facility_id: str, bed_count: int = 12):
        self.facility_id = facility_id
        self.bed_count = bed_count
        self.is_active = True
        logger.setItem = None
        logger.info(f"Initialized Vermicompost Sentinel for Facility {self.facility_id} with {self.bed_count} beds.")

    def sample_bed_sensors(self, bed_id: int) -> Dict[str, Any]:
        """
        Simulates IoT sensor telemetry extraction for a specific vermicompost bed.
        Optimal ranges: Temp (15-25 C), Moisture (70-80%), pH (6.5-7.5).
        """
        temperature_c = round(random.uniform(14.0, 29.0), 2)
        moisture_pct = round(random.uniform(60.0, 88.0), 2)
        ph_level = round(random.uniform(6.0, 8.2), 2)
        leachate_ec_ms_cm = round(random.uniform(0.8, 3.5), 2)  # Electrical Conductivity
        heavy_metal_ppm = round(random.uniform(0.01, 0.65), 3)
        
        return {
            "facility_id": self.facility_id,
            "bed_id": bed_id,
            "timestamp": time.time(),
            "temperature_c": temperature_c,
            "moisture_pct": moisture_pct,
            "ph_level": ph_level,
            "leachate_ec_ms_cm": leachate_ec_ms_cm,
            "heavy_metal_ppm": heavy_metal_ppm
        }

    def analyze_bed_biosafety(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates telemetry against biological thresholds to protect earthworm populations
        and finished vermicompost grade.
        """
        alerts = []
        status = "OPTIMAL"
        
        temp = telemetry["temperature_c"]
        moisture = telemetry["moisture_pct"]
        ph = telemetry["ph_level"]
        hm = telemetry["heavy_metal_ppm"]
        
        if temp > 28.0:
            status = "WARNING"
            alerts.append(f"CRITICAL_HIGH_TEMP: {temp}C exceeds lethal limit for Eisenia fetida (>28C).")
        elif temp < 15.0:
            status = "WARNING"
            alerts.append(f"LOW_TEMP: {temp}C slows microbial/worm metabolism (<15C).")
            
        if moisture < 65.0:
            status = "WARNING"
            alerts.append(f"DEHYDRATION_RISK: Bed moisture at {moisture}% (Target: 70-80%).")
        elif moisture > 85.0:
            status = "WARNING"
            alerts.append(f"HYPOXIA_RISK: Bed moisture at {moisture}% causes anaerobic conditions.")
            
        if ph < 6.2 or ph > 8.0:
            status = "WARNING"
            alerts.append(f"PH_IMBALANCE: pH level at {ph} outside safe bracket (6.5-7.5).")
            
        if hm > 0.5:
            status = "HAZARD"
            alerts.append(f"TOXIC_LEACHATE: Heavy metal contamination detected ({hm} ppm).")
            
        return {
            "bed_id": telemetry["bed_id"],
            "status": status,
            "alerts": alerts,
            "action_recommended": len(alerts) > 0
        }

    def run_facility_audit(self) -> List[Dict[str, Any]]:
        """
        Executes an audit cycle across all active vermicompost beds.
        """
        audit_results = []
        for bed_id in range(1, self.bed_count + 1):
            telemetry = self.sample_bed_sensors(bed_id)
            evaluation = self.analyze_bed_biosafety(telemetry)
            audit_results.append({
                "telemetry": telemetry,
                "evaluation": evaluation
            })
        logger.info(f"Completed full audit for {self.bed_count} beds at facility {self.facility_id}.")
        return audit_results


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Vermicompost Sentinel Test Harness...")
    sentinel = CommercialVermicompostSentinel(facility_id="NRB-VERMI-042", bed_count=4)
    results = sentinel.run_facility_audit()
    print(json.dumps(results, indent=2))
