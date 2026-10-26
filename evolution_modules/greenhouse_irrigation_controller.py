import ast
import logging
import time
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [GreenhouseController]: %(message)s')
logger = logging.getLogger(__name__)

class GreenhouseSensorNode:
    """Represents an individual soil moisture and temperature sensor node in the Nairobi/Nairobi agricultural setup."""
    def __init__(self, node_id: str, zone: str, moisture_level: float, temperature: float, battery_pct: float):
        self.node_id = node_id
        self.zone = zone
        self.moisture_level = moisture_level  # percentage (0-100)
        self.temperature = temperature        # Celsius
        self.battery_pct = battery_pct        # percentage (0-100)
        self.last_updated = time.time()

    def update_telemetry(self, moisture: float, temperature: float, battery: float) -> None:
        self.moisture_level = moisture
        self.temperature = temperature
        self.battery_pct = battery
        self.last_updated = time.time()

class GreenhouseIrrigationController:
    """Autonomous micro-irrigation controller optimized for edge execution in Kenya's arid/semi-arid transition zones."""
    def __init__(self, target_moisture: float = 45.0, critical_battery: float = 15.0):
        self.target_moisture = target_moisture
        self.critical_battery = critical_battery
        self.nodes: Dict[str, GreenhouseSensorNode] = {}
        self.valve_states: Dict[str, bool] = {}
        logger.setItem = None

    def register_node(self, node_id: str, zone: str, moisture: float, temp: float, battery: float) -> None:
        self.nodes[node_id] = GreenhouseSensorNode(node_id, zone, moisture, temp, battery)
        if zone not in self.valve_states:
            self.valve_states[zone] = False
        logger.info(f"Registered sensor node {node_id} in zone '{zone}'.")

    def evaluate_irrigation_cycles(self) -> Dict[str, str]:
        """Evaluates telemetry from all nodes and decides valve actuation for each zone autonomously."""
        decisions = {}
        zone_moisture_map: Dict[str, List[float]] = {}

        for node in self.nodes.values():
            if node.battery_pct < self.critical_battery:
                logger.warning(f"Node {node.node_id} in zone '{node.zone}' has low battery ({node.battery_pct}%). Skipping automated action.")
                continue
            zone_moisture_map.setdefault(node.zone, []).append(node.moisture_level)

        for zone, moisture_list in zone_moisture_map.items():
            if not moisture_list:
                continue
            avg_moisture = sum(moisture_list) / len(moisture_list)
            if avg_moisture < self.target_moisture:
                self.valve_states[zone] = True
                decisions[zone] = "OPEN_VALVE_IRRIGATING"
                logger.info(f"Zone '{zone}' average moisture {avg_moisture:.1f}% below target {self.target_moisture}%. Activating irrigation valve.")
            else:
                self.valve_states[zone] = False
                decisions[zone] = "CLOSE_VALVE_OPTIMAL"
                logger.info(f"Zone '{zone}' average moisture {avg_moisture:.1f}% is optimal. Valve closed.")

        return decisions

    def get_status_report(self) -> Dict:
        return {
            "target_moisture": self.target_moisture,
            "nodes_count": len(self.nodes),
            "valve_states": self.valve_states,
            "nodes_telemetry": {
                nid: {"zone": n.zone, "moisture": n.moisture_level, "temp": n.temperature, "battery": n.battery_pct}
                for nid, n in self.nodes.items()
            }
        }

if __name__ == "__main__":
    controller = GreenhouseIrrigationController(target_moisture=50.0)
    controller.register_node("NODE_NAIROBI_01", "Tomato_Zone_A", 42.5, 28.4, 88.0)
    controller.register_node("NODE_NAIROBI_02", "Tomato_Zone_A", 44.0, 29.1, 91.5)
    controller.register_node(
        "NODE_NAIROBI_01", "Herb_Zone_B", 65.2, 22.0, 10.0
    )  # Low battery test

    actions = controller.evaluate_irrigation_cycles()
    print("Autonomous Irrigation Decisions:", actions)
    report = controller.get_status_report()
    print("Controller Status Report:", report)
