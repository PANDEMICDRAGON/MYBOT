"""
Nairobi Urban Kitchen Garden & Rainwater Harvesting Micro-Irrigation Automated Sentinel
Designed for Michael Obiero's Nairobi residence to manage urban agriculture efficiently.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("KitchenGardenSentinel")


class KitchenGardenSentinel:
    """
    Monitors soil moisture, ambient humidity, and rooftop rainwater tank levels
    to automate micro-drip irrigation for urban kitchen gardens in Nairobi.
    """

    def __init__(self, tank_capacity_liters: float = 1000.0, target_moisture_pct: float = 65.0):
        self.tank_capacity_liters = tank_capacity_liters
        self.target_moisture_pct = target_moisture_pct
        self.zones: Dict[str, Dict[str, Any]] = {}
        self.water_level_liters = tank_capacity_liters * 0.8
        logger.info("KitchenGardenSentinel initialized with %.1fL water tank capacity.", tank_capacity_liters)

    def register_zone(self, zone_id: str, crop_type: str, current_moisture: float) -> None:
        """Register a kitchen garden zone (e.g., Sukuma Wiki, Coriander, Spinach)."""
        self.zones[zone_id] = {
            "crop_type": crop_type,
            "current_moisture": current_moisture,
            "status": "IDLE",
            "last_watered_timestamp": 0.0
        }
        logger.info("Registered zone %s (%s) at %.1f%% moisture.", zone_id, crop_type, current_moisture)

    def update_sensor_reading(self, zone_id: str, moisture_pct: float) -> None:
        """Update moisture telemetry from IoT sensor in the specified zone."""
        if zone_id in self.zones:
            self.zones[zone_id]["current_moisture"] = moisture_pct
            logger.debug("Zone %s telemetry updated: Moisture = %.1f%%", zone_id, moisture_pct)

    def record_rainfall(self, liters_harvested: float) -> None:
        """Record harvested rainwater entering the storage tank."""
        self.water_level_liters = min(self.tank_capacity_liters, self.water_level_liters + liters_harvested)
        logger.info(
            "Rainwater harvested: +%.1fL. Current Tank Level: %.1fL / %.1fL",
            liters_harvested,
            self.water_level_liters,
            self.tank_capacity_liters
        )

    def evaluate_irrigation_cycle(self) -> Dict[str, Any]:
        """
        Evaluates all zones and triggers drip irrigation if soil moisture is below
        target threshold and sufficient water is available in the storage tank.
        """
        actions: List[Dict[str, Any]] = []
        total_water_needed = 0.0

        for zone_id, data in self.zones.items():
            if data["current_moisture"] < self.target_moisture_pct:
                deficit = self.target_moisture_pct - data["current_moisture"]
                water_required = deficit * 1.5  # 1.5L per percent deficit factor
                total_water_needed += water_required
                actions.append({
                    "zone_id": zone_id,
                    "crop": data["crop_type"],
                    "action": "IRRIGATE",
                    "water_allocated_liters": water_required
                })

        if total_water_needed <= 0:
            return {"status": "OPTIMAL", "actions": [], "tank_level": self.water_level_liters}

        if self.water_level_liters >= total_water_needed:
            self.water_level_liters -= total_water_needed
            for action in actions:
                z_id = action["zone_id"]
                self.zones[z_id]["status"] = "WATERED"
                self.zones[z_id]["last_watered_timestamp"] = time.time()
            logger.info("Irrigation cycle completed successfully. Total water dispensed: %.1fL", total_water_needed)
            return {
                "status": "EXECUTED",
                "actions": actions,
                "tank_level": self.water_level_liters
            }
        else:
            logger.warning(
                "Insufficient tank water (%.1fL available, %.1fL required). Conservation mode active.",
                self.water_level_liters,
                total_water_needed
            )
            return {
                "status": "CONSERVATION_MODE",
                "reason": "Insufficient water storage",
                "tank_level": self.water_level_liters,
                "water_deficit": total_water_needed - self.water_level_liters
            }


if __name__ == "__main__":
    print("[TEST HARNESS] Starting KitchenGardenSentinel verification...")
    sentinel = KitchenGardenSentinel(tank_capacity_liters=500.0, target_moisture_pct=60.0)
    
    sentinel.register_zone("zone_balcony_1", "Sukuma Wiki (Collard Greens)", 45.0)
    sentinel.register_zone(
        "zone_balcony_2",
        "Coriander (Dhania)",
        58.0
    )
    
    sentinel.record_rainfall(120.0)
    result = sentinel.evaluate_irrigation_cycle()
    print("Irrigation Evaluation Result:", json.dumps(result, indent=2))
    print("[TEST HARNESS] KitchenGardenSentinel verification completed successfully.")
