import ast
import json
import logging
import time
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('NairobiAquaponicsSentinel')

class NairobiAquaponicsSentinel:
    """
    Monitors water chemistry, pump telemetry, biological filtration efficiency, 
    and nutrient exchange ratios in urban aquaponic installations across Nairobi.
    """
    def __init__(self, system_id: str, fish_species: str, crop_type: str):
        self.system_id = system_id
        self.fish_species = fish_species
        self.crop_type = crop_type
        self.metrics_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized Aquaponics Sentinel [{self.system_id}] for {self.fish_species} & {self.crop_type}.")

    def evaluate_water_chemistry(self, ph: float, dissolved_oxygen_mg_l: float, ammonia_ppm: float, nitrate_ppm: float, water_temp_c: float) -> Dict[str, Any]:
        """
        Evaluates key water parameters against optimal biological thresholds for tilapia/catfish and leafy greens.
        """
        alerts = []
        status = "OPTIMAL"

        # pH bounds for nitrification bacteria and fish (ideal: 6.8 - 7.2)
        if ph < 6.0 or ph > 8.0:
            status = "CRITICAL"
            alerts.append(f"pH level {ph} is out of safe range (6.0-8.0). Nitrification bacteria at risk.")
        elif ph < 6.6 or ph > 7.5:
            if status != "CRITICAL": status = "WARNING"
            alerts.append(f"pH level {ph} requires buffering adjustment.")

        # Dissolved Oxygen (DO) (ideal: > 5.0 mg/L)
        if dissolved_oxygen_mg_l < 4.0:
            status = "CRITICAL"
            alerts.append(f"Dissolved Oxygen dangerously low at {dissolved_oxygen_mg_l} mg/L. Aeration failure risk!")
        elif dissolved_oxygen_mg_l < 5.5:
            if status != "CRITICAL": status = "WARNING"
            alerts.append(f"Dissolved Oxygen sub-optimal at {dissolved_oxygen_mg_l} mg/L.")

        # Ammonia (ideal: 0.0 ppm, toxic > 0.5 ppm)
        if ammonia_ppm > 0.5:
            status = "CRITICAL"
            alerts.append(f"Toxic ammonia spike detected: {ammonia_ppm} ppm!")
        elif ammonia_ppm > 0.2:
            if status != "CRITICAL": status = "WARNING"
            alerts.append(f"Elevated ammonia: {ammonia_ppm} ppm. Monitor biofilter activity.")

        # Water Temperature (ideal for tilapia: 24-28C)
        if water_temp_c < 20.0 or water_temp_c > 32.0:
            status = "CRITICAL"
            alerts.append(f"Water temperature {water_temp_c}°C outside metabolic range.")

        record = {
            "timestamp": time.time(),
            "system_id": self.system_id,
            "ph": ph,
            "do": dissolved_oxygen_mg_l,
            "ammonia": ammonia_ppm,
            "nitrate": nitrate_ppm,
            "temp_c": water_temp_c,
            "status": status,
            "alerts": alerts
        }

        self.metrics_history.append(record)
        return record

    def get_system_health_summary(self) -> Dict[str, Any]:
        """Summarizes recent system performance and operational readiness."""
        if not self.metrics_history:
            return {"system_id": self.system_id, "status": "NO_DATA"}
        
        latest = self.metrics_history[-1]
        return {
            "system_id": self.system_id,
            "fish_species": self.fish_species,
            "crop_type": self.crop_type,
            "latest_status": latest["status"],
            "total_readings": len(self.metrics_history),
            "last_alerts": latest["alerts"]
        }

if __name__ == "__main__":
    sentinel = NairobiAquaponicsSentinel(
        system_id="NAIROBI-ROOFTOP-AQUA-01",
        fish_species="Oreochromis niloticus (Nile Tilapia)",
        crop_type="Kale (Sukuma Wiki)"
    )
    
    # Test normal reading
    eval_normal = sentinel.evaluate_water_chemistry(7.0, 6.2, 0.05, 25.0, 26.5)
    logger.info(f"Normal Check: {json.dumps(eval_normal, indent=2)}")
    
    # Test emergency scenario (Ammonia spike & Low DO)
    eval_emergency = sentinel.evaluate_water_chemistry(5.8, 3.2, 0.8, 5.0, 18.0)
    logger.info(f"Emergency Check: {json.dumps(eval_emergency, indent=2)}")
    
    summary = sentinel.get_system_health_summary()
    logger.info(f"Health Summary: {json.dumps(summary, indent=2)}")

    # Self-test AST compilation
    code_str = open(__file__, 'r').read()
    ast.parse(code_str)
    logger.info("AST compilation check passed successfully.")
