import time
import json
import logging
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [StreetlightSentinel] %(message)s')
logger = logging.getLogger('StreetlightSentinel')

@dataclass
class StreetlightNode:
    node_id: str
    zone: str
    latitude: float
    longitude: float
    led_brightness_pct: int = 80
    grid_active: bool = True
    battery_voltage_v: float = 24.0
    vibration_anomaly_detected: bool = False
    ambient_lux: float = 12.0
    last_ping_timestamp: float = field(default_factory=time.time)

class NairobiStreetlightMeshSentinel:
    """
    Manages Nairobi municipal IoT streetlighting clusters, providing adaptive dimming,
    anti-vandalism alerts, and automated grid-to-solar failovers.
    """
    def __init__(self, target_zones: Optional[List[str]] = None):
        self.target_zones = target_zones or ["CBD", "Westlands", "Parklands", "Kilimani", "Eastleigh"]
        self.nodes: Dict[str, StreetlightNode] = {}
        self._initialize_virtual_grid()

    def _initialize_virtual_grid(self) -> None:
        logger.info("Initializing Nairobi municipal IoT streetlight mesh nodes...")
        for zone in self.target_zones:
            for i in range(1, 4):
                node_id = f"NBO-LGT-{zone.upper()}-{i:03d}"
                # Approximate Nairobi coordinates baseline (-1.2921, 36.8219)
                lat = -1.2921 + random.uniform(-0.05, 0.05)
                lon = 36.8219 + random.uniform(-0.05, 0.05)
                self.nodes[node_id] = StreetlightNode(
                    node_id=node_id,
                    zone=zone,
                    latitude=lat,
                    longitude=lon
                )
        logger.info(f"Successfully deployed {len(self.nodes)} streetlight nodes across {len(self.target_zones)} zones.")

    def poll_and_optimize_zone(self, zone: str, pedestrian_density: float, grid_online: bool) -> List[Dict[str, Any]]:
        """
        Optimizes lighting brightness based on real-time pedestrian density and grid status.
         pedestrian_density: scale 0.0 (empty) to 1.0 (heavy crowd)
         grid_online: boolean state of KPLC feeder line
        """
        actions_taken = []
        for node_id, node in self.nodes.items():
            if node.zone.lower() != zone.lower():
                continue
            
            node.grid_active = grid_online
            node.last_ping_timestamp = time.time()

            # Adaptive dimming curve: base 30% + up to 70% based on pedestrian density
            if grid_online:
                target_brightness = int(30 + (pedestrian_density * 70))
                target_brightness = max(10, min(100, target_brightness))
                node.led_brightness_pct = target_brightness
            else:
                # Emergency conservation mode on solar/battery backup
                node.led_brightness_pct = 20
                node.battery_voltage_v = max(11.0, node.battery_voltage_v - 0.1)

            # Simulate random tamper/vibration event (vandalism attempt on cables/batteries)
            if random.random() < 0.02:
                node.vibration_anomaly_detected = True
                logger.warning(f"VANDALISM ALERT: Tamper vibration detected at node {node_id} in {zone}!")
            else:
                node.vibration_anomaly_detected = False

            actions_taken.append({
                "node_id": node_id,
                "brightness_pct": node.led_brightness_pct,
                "grid_active": node.grid_active,
                "battery_v": round(node.battery_voltage_v, 2),
                "tamper_alert": node.vibration_anomaly_detected
            })

        return actions_taken

    def generate_mesh_audit_report(self) -> Dict[str, Any]:
        total_nodes = len(self.nodes)
        active_grid_count = sum(1 for n in self.nodes.values() if n.grid_active)
        tamper_count = sum(1 for n in self.nodes.values() if n.vibration_anomaly_detected)
        avg_brightness = sum(n.led_brightness_pct for n in self.nodes.values()) / total_nodes if total_nodes > 0 else 0

        return {
            "timestamp": time.time(),
            "total_nodes": total_nodes,
            "grid_uptime_pct": round((active_grid_count / total_nodes) * 100, 2) if total_nodes > 0 else 0,
            "active_tamper_alarms": tamper_count,
            "average_brightness_pct": round(avg_brightness, 2),
            "status": "SECURE_AND_OPTIMIZED"
        }

if __name__ == "__main__":
    logger.info("Executing standalone validation harness for NairobiStreetlightMeshSentinel...")
    sentinel = NairobiStreetlightMeshSentinel()
    
    # Simulate evening rush hour in CBD with grid online
    cbd_actions = sentinel.poll_and_optimize_zone("CBD", pedestrian_density=0.85, grid_online=True)
    logger.info(f"CBD Optimization Actions Sample: {cbd_actions[:2]}")

    # Simulate midnight in Westlands with grid outage
    westlands_actions = sentinel.poll_and_optimize_zone("Westlands", pedestrian_density=0.05, grid_online=False)
    logger.info(f"Westlands Outage Actions Sample: {westlands_actions[:2]}")

    report = sentinel.generate_mesh_audit_report()
    logger.info(f"Municipal Streetlight Mesh Audit Report: {json.dumps(report, indent=2)}")
