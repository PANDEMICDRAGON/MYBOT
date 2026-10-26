"""
Nairobi Commercial Greenhouse Aquaculture & Recirculating Aquaponic Biofilter Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import time
import logging
import json
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("AquacultureSentinel")

class AquacultureSentinel:
    """
    Monitors water quality parameters (Dissolved Oxygen, pH, Ammonia, Temperature)
    in recirculating aquaculture systems (RAS) integrated with greenhouses in Nairobi.
    """
    def __init__(self, tank_id: str, target_temp_c: float = 24.5, min_do_mg_l: float = 5.0):
        self.tank_id = tank_id
        self.target_temp_c = target_temp_c
        self.min_do_mg_l = min_do_mg_l
        self.metrics_history: List[Dict[str, Any]] = []
        self.actuator_state = {
            "aeration_pump": "ACTIVE",
            "biofilter_flow": "ACTIVE",
            "emergency_oxygen_valve": "CLOSED",
            "heater_chiller": "STANDBY"
        }

    def ingest_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingests sensor payload and evaluates biofilter health and fish stress thresholds.
        """
        timestamp = telemetry.get("timestamp", time.time())
        temp_c = float(telemetry.get("temperature_c", self.target_temp_c))
        do_mg_l = float(telemetry.get("dissolved_oxygen_mg_l", 6.0))
        ph = float(telemetry.get("ph_level", 7.2))
        ammonia_ppm = float(telemetry.get("ammonia_ppm", 0.05)) # Target < 0.05 ppm
        nitrite_ppm = float(telemetry.get("nitrite_ppm", 0.1))   # Target < 0.1 ppm

        alerts: List[str] = []

        # Dissolved Oxygen Check
        if do_mg_l < self.min_do_mg_l:
            alerts.append(f"CRITICAL: Low Dissolved Oxygen ({do_mg_l} mg/L). Activating backup oxygen valve.")
            self.actuator_state["emergency_oxygen_valve"] = "OPEN"
            self.actuator_state["aeration_pump"] = "MAX_BOOST"
        else:
            self.actuator_state["emergency_oxygen_valve"] = "CLOSED"

        # Ammonia Toxicity Check
        if ammonia_ppm > 0.1:
            alerts.append(f"WARNING: Elevated Ammonia ({ammonia_ppm} ppm). Biofilter nitrification strain detected.")
            self.actuator_state["biofilter_flow"] = "HIGH_FLUSH"

        # Temperature Regulation Check
        if abs(temp_c - self.target_temp_c) > 1.5:
            alerts.append(f"NOTICE: Temperature deviation ({temp_c}C vs Target {self.target_temp_c}C).")
            self.actuator_state["heater_chiller"] = "ADJUSTING"
        else:
            self.actuator_state["heater_chiller"] = "STANDBY"

        record = {
            "tank_id": self.tank_id,
            "timestamp": timestamp,
            "temperature_c": temp_c,
            "dissolved_oxygen_mg_l": do_mg_l,
            "ph": ph,
            "ammonia_ppm": ammonia_ppm,
            "nitrite_ppm": nitrite_ppm,
            "alerts": alerts,
            "actuators": dict(self.actuator_state)
        }

        self.metrics_history.append(record)
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)

        return record

    def get_status_summary(self) -> Dict[str, Any]:
        """Returns latest system health summary."""
        if not self.metrics_history:
            return {"status": "INITIALIZED", "tank_id": self.tank_id}
        latest = self.metrics_history[-1]
        return {
            "tank_id": self.tank_id,
            "last_update": latest["timestamp"],
            "system_health": "CRITICAL" if latest["alerts"] else "OPTIMAL",
            "active_alerts": latest["alerts"],
            "actuator_state": latest["actuators"]
        }

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Greenhouse Aquaculture Sentinel...")
    sentinel = AquacultureSentinel(tank_id="NAIROBI_TITAN_TILAPIA_01")

    # Test normal telemetry
    sample_telemetry = {
        "timestamp": time.time(),
        "temperature_c": 24.2,
        "dissolved_oxygen_mg_l": 6.8,
        "ph_level": 7.0,
        "ammonia_ppm": 0.02,
        "nitrite_ppm": 0.05
    }
    res = sentinel.ingest_telemetry(sample_telemetry)
    print("Normal Ingestion Result:", json.dumps(res, indent=2))

    # Test stress telemetry (Low DO and High Ammonia)
    stress_telemetry = {
        "timestamp": time.time(),
        "temperature_c": 27.5,
        "dissolved_oxygen_mg_l": 4.1,
        "ph_level": 8.2,
        "ammonia_ppm": 0.25,
        "nitrite_ppm": 0.4
    }
    res_stress = sentinel.ingest_telemetry(stress_telemetry)
    print("Stress Ingestion Result:", json.dumps(res_stress, indent=2))
    print("Sentinel Status Summary:", json.dumps(sentinel.get_status_summary(), indent=2))
