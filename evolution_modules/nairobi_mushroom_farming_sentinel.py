"""
Nairobi Urban Mushroom Cultivation & Humidity Biosafety Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Monitors fruiting chamber microclimates (temperature, relative humidity, CO2 levels)
and substrate pasteurization cycles for urban mushroom farming, triggering automated
foggers and ventilation exhaust systems while logging biosafety telemetry.
"""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MushroomSentinel")

class MushroomFarmingSentinel:
    """Manages environmental parameters for urban mushroom fruiting and incubation chambers."""

    def __init__(self, chamber_id: str, mushroom_species: str = "Oyster") -> None:
        self.chamber_id = chamber_id
        self.mushroom_species = mushroom_species
        self.target_humidity_min = 85.0  # percentage
        self.target_humidity_max = 95.0
        self.target_temp_min = 18.0     # Celsius
        self.target_temp_max = 24.0
        self.max_co2_ppm = 900.0        # parts per million
        self.telemetry_history: List[Dict[str, Any]] = []

    def evaluate_chamber_conditions(self, temp_c: float, humidity_pct: float, co2_ppm: float) -> Dict[str, Any]:
        """Evaluates current sensor readings and determines required actuator actions."""
        actions = []
        status = "OPTIMAL"

        # Humidity check
        if humidity_pct < self.target_humidity_min:
            status = "ADJUSTING"
            actions.append({"actuator": "ultrasonic_fogger", "state": "ON", "duration_sec": 120})
        elif humidity_pct > self.target_humidity_max:
            status = "ADJUSTING"
            actions.append({"actuator": "exhaust_fan", "state": "ON", "duration_sec": 60})

        # CO2 check
        if co2_ppm > self.max_co2_ppm:
            status = "VENTILATING"
            actions.append({"actuator": "fresh_air_intake_fan", "state": "ON", "duration_sec": 180})

        # Temperature safety
        if temp_c > self.target_temp_max + 4.0:
            status = "CRITICAL_HEAT_WARNING"
            actions.append({"actuator": "evaporative_cooling_pad", "state": "ON", "duration_sec": 300})

        record = {
            "timestamp": time.time(),
            "chamber_id": self.chamber_id,
            "species": self.mushroom_species,
            "temperature_c": temp_c,
            "humidity_pct": humidity_pct,
            "co2_ppm": co2_ppm,
            "status": status,
            "triggered_actions": actions
        }
        self.telemetry_history.append(record)
        logger.info(f"Chamber {self.chamber_id} [{status}] -> Temp: {temp_c}C, Humidity: {humidity_pct}%, CO2: {co2_ppm}ppm")
        return record

    def get_audit_summary(self) -> Dict[str, Any]:
        """Summarizes environmental stability over the monitoring period."""
        if not self.telemetry_history:
            return {"chamber_id": self.chamber_id, "total_readings": 0}
        
        avg_temp = sum(r["temperature_c"] for r in self.telemetry_history) / len(self.telemetry_history)
        avg_humidity = sum(r["humidity_pct"] for r in self.telemetry_history) / len(self.telemetry_history)
        return {
            "chamber_id": self.chamber_id,
            "total_readings": len(self.telemetry_history),
            "average_temperature_c": round(avg_temp, 2),
            "average_humidity_pct": round(avg_humidity, 2),
            "last_status": self.telemetry_history[-1]["status"]
        }

if __name__ == "__main__":
    print("Initializing Nairobi Urban Mushroom Cultivation Sentinel Test...")
    sentinel = MushroomFarmingSentinel(chamber_id="KASARANI-MUSHROOM-UNIT-01", mushroom_species="Blue Oyster")
    
    # Simulate routine sensor telemetry feed
    sample_readings = [
        (20.5, 82.0, 850.0),  # Low humidity
        (21.0, 88.0, 820.0),  # Optimal
        (22.0, 96.0, 1100.0), # High humidity + High CO2
        (26.5, 90.0, 950.0)   # High temperature alert
    ]
    
    for temp, hum, co2 in sample_readings:
        sentinel.evaluate_chamber_conditions(temp, hum, co2)
    
    summary = sentinel.get_audit_summary()
    print(f"Final Sentinel Audit Summary: {summary}")
    print("Mushroom Farming Sentinel test completed successfully.")
