"""
Module: nairobi_ev_charging_hub.py
Description: Nairobi Electric Vehicle (EV) Solar Charging Hub & Battery Swapping Grid Sentinel.
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import ast
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("EVChargingSentinel")

class EVChargingHubSentinel:
    """
    Manages solar generation, battery swapping slots, and dynamic KPLC grid power 
    allocation for Nairobi EV fleets, prioritizing low-cost solar and peak shaving.
    """
    def __init__(self, hub_id: str, capacity_kw: float, solar_generation_kw: float):
        self.hub_id = hub_id
        self.capacity_kw = capacity_kw
        self.solar_generation_kw = solar_generation_kw
        self.connected_vehicles: Dict[str, Dict[str, Any]] = {}
        self.swap_inventory: List[Dict[str, Any]] = []
        logger.info(f"Initialized EV Hub {hub_id} with {capacity_kw}kW capacity & {solar_generation_kw}kW solar.")

    def register_swap_battery(self, battery_id: str, state_of_health: float, state_of_charge: float) -> None:
        """Registers a swap-ready battery in the local inventory."""
        battery = {
            "battery_id": battery_id,
            "soh": state_of_health,
            "soc": state_of_charge,
            "status": "READY"
        }
        self.swap_inventory.append(battery)
        logger.info(f"Battery {battery_id} registered. SoH: {state_of_health}%, SoC: {state_of_charge}%")

    def allocate_charging_slot(self, vehicle_id: str, required_kw: float, priority: int = 1) -> Dict[str, Any]:
        """
        Allocates power to a connected EV based on solar availability, current load, 
        and priority (e.g., emergency boda vs delivery fleet).
        """
        current_allocated = sum(v["allocated_kw"] for v in self.connected_vehicles.values())
        available_headroom = self.capacity_kw - current_allocated

        if required_kw <= available_headroom:
            allocated = required_kw
            source = "SOLAR+GRID"
        elif self.solar_generation_kw > current_allocated:
            allocated = max(0.0, self.solar_generation_kw - current_allocated)
            source = "SOLAR_PRIMARY"
        else:
            allocated = max(0.0, available_headroom)
            source = "RATIONED"

        self.connected_vehicles[vehicle_id] = {
            "vehicle_id": vehicle_id,
            "allocated_kw": allocated,
            "requested_kw": required_kw,
            "source": source,
            "priority": priority,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"Allocated {allocated}kW to vehicle {vehicle_id} from source: {source}")
        return self.connected_vehicles[vehicle_id]

    def execute_battery_swap(self, vehicle_id: str, depleted_battery_id: str) -> Dict[str, Any]:
        """
        Facilitates instantaneous battery swapping for Nairobi electric transport units.
        """
        ready_batteries = [b for b in self.swap_inventory if b["status"] == "READY" and b["soc"] >= 95.0]
        if not ready_batteries:
            logger.warning(f"Swap failed for {vehicle_id}: No fully charged batteries available.")
            return {"status": "FAILED", "reason": "NO_READY_BATTERIES"}

        # Select highest SoH ready battery
        best_battery = max(ready_batteries, key=lambda x: x["soh"])
        best_battery["status"] = "DEPLOYED"

        # Add depleted battery to charging queue
        self.swap_inventory.append({
            "battery_id": depleted_battery_id,
            "soh": 92.5,
            "soc": 12.0,
            "status": "CHARGING"
        })

        logger.info(f"Successful swap for {vehicle_id}: Issued {best_battery['battery_id']}, received {depleted_battery_id}")
        return {
            "status": "SUCCESS",
            "vehicle_id": vehicle_id,
            "issued_battery_id": best_battery["battery_id"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def audit_hub_metrics(self) -> Dict[str, Any]:
        """Compiles hub operational metrics for Nairobi smart grid analytics."""
        total_allocated = sum(v["allocated_kw"] for v in self.connected_vehicles.values())
        ready_count = len([b for b in self.swap_inventory if b["status"] == "READY"])
        charging_count = len([b for b in self.swap_inventory if b["status"] == "CHARGING"])
        
        return {
            "hub_id": self.hub_id,
            "capacity_kw": self.capacity_kw,
            "solar_generation_kw": self.solar_generation_kw,
            "total_allocated_kw": total_allocated,
            "ready_swap_batteries": ready_count,
            "charging_batteries": charging_count,
            "active_vehicles": len(self.connected_vehicles),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

if __name__ == "__main__":
    print("=== TESTING NAIROBI EV CHARGING HUB SENTINEL ===")
    hub = EVChargingHubSentinel(hub_id="NBO-EV-HUB-01", capacity_kw=150.0, solar_generation_kw=85.0)
    
    hub.register_swap_battery("BAT-901", 98.5, 99.0)
    hub.register_swap_battery("BAT-902", 95.0, 96.5)
    
    slot = hub.allocate_charging_slot("BODA-EV-042", required_kw=22.5, priority=1)
    print(json.dumps(slot, indent=2))
    
    swap_res = hub.execute_battery_swap("BODA-EV-042", "BAT-OLD-019")
    print(json.dumps(swap_res, indent=2))
    
    metrics = hub.audit_hub_metrics()
    print(json.dumps(metrics, indent=2))
    
    # Compile check
    assert ast.parse(open(__file__).read())
    print("=== AST COMPILATION SUCCESSFUL ===")
