import time
import math
import json
import logging
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NairobiAgriDroneMesh")

class DroneNode:
    """Represents an autonomous agricultural drone node in the Nairobi perimeter mesh."""
    def __init__(self, node_id: str, lat: float, lon: float, battery_pct: float):
        self.node_id = node_id
        self.lat = lat
        self.lon = lon
        self.battery_pct = battery_pct
        self.status = "STANDBY"
        self.last_heartbeat = time.time()

    def update_telemetry(self, lat: float, lon: float, battery_pct: float) -> None:
        self.lat = lat
        self.lon = lon
        self.battery_pct = battery_pct
        self.last_heartbeat = time.time()

class NairobiAgriDroneMeshCoordinator:
    """Coordinates multi-drone telemetry, collision avoidance, and tactical crop monitoring swarms."""
    def __init__(self, center_lat: float = -1.2921, center_lon: float = 36.8219, geofence_radius_km: float = 25.0):
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.geofence_radius_km = geofence_radius_km
        self.nodes: Dict[str, DroneNode] = {}

    def register_node(self, node_id: str, lat: float, lon: float, battery_pct: float) -> bool:
        if not self._is_within_geofence(lat, lon):
            logger.warning(f"Node {node_id} registration rejected: outside Nairobi geofence boundary.")
            return False
        self.nodes[node_id] = DroneNode(node_id, lat, lon, battery_pct)
        logger.info(f"Node {node_id} successfully registered into swarm mesh.")
        return True

    def _is_within_geofence(self, lat: float, lon: float) -> bool:
        # Haversine distance approximation
        dlat = math.radians(lat - self.center_lat)
        dlon = math.radians(lon - self.center_lon)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(self.center_lat)) * math.cos(math.radians(lat)) * math.sin(dlon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance_km = 6371.0 * c
        return distance_km <= self.geofence_radius_km

    def evaluate_swarm_health(self) -> Dict[str, any]:
        active_nodes = len(self.nodes)
        low_battery_count = sum(1 for n in self.nodes.values() if n.battery_pct < 20.0)
        return {
            "active_nodes": active_nodes,
            "low_battery_alerts": low_battery_count,
            "mesh_status": "OPTIMAL" if low_battery_count == 0 else "DEGRADED_BATTERY_WARNING"
        }

if __name__ == "__main__":
    coordinator = NairobiAgriDroneMeshCoordinator()
    # Test registration within Nairobi limits (e.g., Karen farm)
    success = coordinator.register_node("DRONE_ALPHA_01", -1.3192, 36.7073, 88.5)
    print(f"Registration Test: {success}")
    health = coordinator.evaluate_swarm_health()
    print(f"Swarm Health Metrics: {json.dumps(health, indent=2)}")
