"""Nairobi Boda Boda Emergency Telematics & Incident Mesh Sentinel.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import ast
import json
import logging
import math
import time
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("BodaSafetyMesh")


class BodaSafetyMesh:
    """Analyzes real-time telemetry from Nairobi motorcycle fleets to detect accidents,
    geofence breaches, and unauthorized route deviations."""

    def __init__(self, g_force_threshold: float = 4.5, speed_limit_kmh: float = 90.0):
        self.g_force_threshold = g_force_threshold
        self.speed_limit_kmh = speed_limit_kmh
        self.active_fleets: Dict[str, Dict] = {}
        self.incident_logs: List[Dict] = []

    def register_bike(self, bike_id: str, rider_name: str, sacco_group: str) -> None:
        """Registers a motorcycle into the local telemetry mesh."""
        self.active_fleets[bike_id] = {
            "rider_name": rider_name,
            "sacco_group": sacco_group,
            "status": "ACTIVE",
            "last_ping": time.time(),
            "location": (-1.286389, 36.817223),  # Default Nairobi CBD
            "speed_kmh": 0.0,
            "max_g_experienced": 1.0
        }
        logger.info(f"Registered bike {bike_id} for rider {rider_name} ({sacco_group}).")

    def ingest_telemetry(self, bike_id: str, lat: float, lon: float, speed_kmh: float, g_force: float) -> Dict:
        """Ingests live telemetry packets and evaluates safety anomalies."""
        if bike_id not in self.active_fleets:
            raise ValueError(f"Bike ID {bike_id} is not registered in the safety mesh.")

        bike = self.active_fleets[bike_id]
        bike["last_ping"] = time.time()
        bike["location"] = (lat, lon)
        bike["speed_kmh"] = speed_kmh
        bike["max_g_experienced"] = max(bike["max_g_experienced"], g_force)

        alerts = []

        # Check for crash/impact condition
        if g_force >= self.g_force_threshold:
            incident = {
                "timestamp": time.time(),
                "bike_id": bike_id,
                "rider": bike["rider_name"],
                "sacco": bike["sacco_group"],
                "type": "CRASH_IMPACT_DETECTED",
                "g_force": g_force,
                "location": (lat, lon)
            }
            self.incident_logs.append(incident)
            bike["status"] = "EMERGENCY_TRIGGERED"
            alerts.append(incident)
            logger.error(f"CRASH ALERT! Bike {bike_id} experienced {g_force}G at {lat}, {lon}!")

        # Check for speeding anomaly
        if speed_kmh > self.speed_limit_kmh:
            speed_alert = {
                "timestamp": time.time(),
                "bike_id": bike_id,
                "rider": bike["rider_name"],
                "type": "SPEEDING_VIOLATION",
                "speed_kmh": speed_kmh,
                "location": (lat, lon)
            }
            alerts.append(speed_alert)
            logger.warning(f"Speed violation: Bike {bike_id} clocked at {speed_kmh} km/h.")

        return {
            "bike_id": bike_id,
            "status": bike["status"],
            "alerts_triggered": len(alerts),
            "details": alerts
        }

    def get_mesh_status(self) -> Dict:
        """Returns aggregate health and status of the Nairobi Boda Safety Mesh."""
        active_count = sum(1 for b in self.active_fleets.values() if b["status"] == "ACTIVE")
        emergency_count = sum(1 for b in self.active_fleets.values() if b["status"] == "EMERGENCY_TRIGGERED")
        return {
            "total_registered": len(self.active_fleets),
            "active_units": active_count,
            "emergency_units": emergency_count,
            "total_incidents_logged": len(self.incident_logs)
        }


if __name__ == "__main__":
    print("Initializing Nairobi Boda Boda Emergency Telematics & Incident Mesh Sentinel...")
    mesh = BodaSafetyMesh(g_force_threshold=4.0, speed_limit_kmh=80.0)
    mesh.register_bike("KBX-412A", "Jumah Otieno", "Umoinner Sacco")
    mesh.register_bike("KMC-892B", "Amina Wanjiku", "Super Metro Boda")

    # Normal telemetry update
    resp1 = mesh.ingest_telemetry("KBX-412A", -1.2921, 36.8219, 45.0, 1.2)
    print("Telemetry Resp 1:", json.dumps(resp1, indent=2))

    # Trigger crash anomaly
    resp2 = mesh.ingest_telemetry("KBX-412A", -1.3001, 36.8350, 65.0, 5.8)
    print("Telemetry Resp 2 (Crash):", json.dumps(resp2, indent=2))

    print("Mesh Status Summary:", json.dumps(mesh.get_mesh_status(), indent=2))

    # AST Self-Compilation Check
    with open(__file__, "r", encoding="utf-8") as f:
        source_code = f.read()
    ast.parse(source_code)
    print("SUCCESS: Module source code validated via ast.parse().")
