"""
Nairobi Commercial Steam Boiler & Pressure Vessel Biosafety Sentinel
Autonomous Evolutionary Module #178
Designed for Cortana's Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import os
import time
import json
import logging
import threading
from typing import Dict, Any, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [SteamBoilerSentinel]: %(message)s'
)
logger = logging.getLogger("SteamBoilerSentinel")


class SteamBoilerSentinel:
    """
    Monitors industrial steam boilers and pressure vessels across Nairobi facilities,
    evaluating pressure thresholds, feedwater levels, and blowdown cycles to enforce
    strict biosafety and operational integrity.
    """

    def __init__(self, max_pressure_bar: float = 12.0, critical_water_level_pct: float = 20.0):
        self.max_pressure_bar = max_pressure_bar
        self.critical_water_level_pct = critical_water_level_pct
        self.vessels: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._active = False
        self._monitor_thread: Optional[threading.Thread] = None

    def register_vessel(self, vessel_id: str, location: str, rated_capacity_kg_hr: float) -> None:
        """Registers a new industrial steam boiler into the telemetry grid."""
        with self._lock:
            self.vessels[vessel_id] = {
                "location": location,
                "rated_capacity_kg_hr": rated_capacity_kg_hr,
                "pressure_bar": 0.0,
                "water_level_pct": 100.0,
                "stack_temp_c": 150.0,
                "blowdown_active": False,
                "status": "NORMAL",
                "last_updated": time.time()
            }
        logger.info(f"Registered steam vessel {vessel_id} at {location} (Capacity: {rated_capacity_kg_hr} kg/hr).")

    def ingest_telemetry(self, vessel_id: str, pressure_bar: float, water_level_pct: float, stack_temp_c: float) -> Dict[str, Any]:
        """Ingests live sensor data, evaluating safety compliance and anomaly risk."""
        with self._lock:
            if vessel_id not in self.vessels:
                raise ValueError(f"Vessel {vessel_id} not registered in sentinel mesh.")
            
            vessel = self.vessels[vessel_id]
            vessel["pressure_bar"] = pressure_bar
            vessel["water_level_pct"] = water_level_pct
            vessel["stack_temp_c"] = stack_temp_c
            vessel["last_updated"] = time.time()

            # Safety evaluation logic
            alerts = []
            if pressure_bar >= self.max_pressure_bar:
                vessel["status"] = "CRITICAL_OVERPRESSURE"
                alerts.append(f"CRITICAL OVERPRESSURE: {pressure_bar} bar exceeds limit {self.max_pressure_bar} bar!")
            elif water_level_pct <= self.critical_water_level_pct:
                vessel["status"] = "CRITICAL_LOW_WATER"
                alerts.append(f"CRITICAL LOW WATER: {water_level_pct}% below threshold {self.critical_water_level_pct}%!")
            elif stack_temp_c > 350.0:
                vessel["status"] = "WARNING_HIGH_STACK_TEMP"
                alerts.append(f"HIGH STACK TEMP: {stack_temp_c} C indicates thermal efficiency loss.")
            else:
                vessel["status"] = "NORMAL"

            return {
                "vessel_id": vessel_id,
                "status": vessel["status"],
                "alerts": alerts,
                "timestamp": vessel["last_updated"]
            }

    def trigger_emergency_blowdown(self, vessel_id: str) -> Dict[str, Any]:
        """Commands an emergency automated blowdown sequence to relieve vessel pressure."""
        with self._lock:
            if vessel_id not in self.vessels:
                raise ValueError(f"Vessel {vessel_id} not found.")
            vessel = self.vessels[vessel_id]
            vessel["blowdown_active"] = True
            vessel["pressure_bar"] = max(0.0, vessel["pressure_bar"] - 4.0)
            logger.warning(f"EMERGENCY BLOWDOWN ACTIVATED for vessel {vessel_id}. Pressure reduced.")
            return {
                "vessel_id": vessel_id,
                "action": "EMERGENCY_BLOWDOWN_EXECUTED",
                "current_pressure_bar": vessel["pressure_bar"],
                "timestamp": time.time()
            }

    def get_system_status(self) -> Dict[str, Any]:
        """Returns aggregate fleet status across all Nairobi installations."""
        with self._lock:
            return {
                "total_vessels": len(self.vessels),
                "vessels": dict(self.vessels),
                "sentinel_timestamp": time.time()
            }


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Steam Boiler Sentinel Test Harness...")
    sentinel = SteamBoilerSentinel(max_pressure_bar=10.0, critical_water_level_pct=25.0)
    
    sentinel.register_vessel("BOILER-IND-01", "Industrial Area Nairobi", 2500.0)
    sentinel.register_vessel("BOILER-TEX-02", "Ruaraka Textile Hub", 1800.0)
    
    telemetry_res = sentinel.ingest_telemetry("BOILER-IND-01", 8.5, 60.0, 210.0)
    print("Telemetry Ingest Normal:", json.dumps(telemetry_res, indent=2))
    
    # Simulate critical pressure spike
    spike_res = sentinel.ingest_telemetry("BOILER-IND-01", 10.8, 45.0, 310.0)
    print("Telemetry Ingest Overpressure:", json.dumps(spike_res, indent=2))
    
    blowdown_res = sentinel.trigger_emergency_blowdown("BOILER-IND-01")
    print("Emergency Blowdown:", json.dumps(blowdown_res, indent=2))
    
    fleet_status = sentinel.get_system_status()
    print("Fleet Status Summary:", json.dumps(fleet_status, indent=2))
    print("Steam Boiler Sentinel test harness executed successfully.")
