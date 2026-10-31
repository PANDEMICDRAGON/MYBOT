import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GridStatus(Enum):
    NORMAL = "NORMAL"
    LOW_PRESSURE = "LOW_PRESSURE"
    HIGH_PRESSURE = "HIGH_PRESSURE"
    FLOW_ANOMALY = "FLOW_ANOMALY"
    OFFLINE = "OFFLINE"


@dataclass
class SensorReading:
    timestamp: float
    pressure_kpa: float
    flow_m3_per_hour: float
    temperature_c: float
    battery_level: float
    signal_strength: int


@dataclass
class GridNode:
    node_id: str
    location: str
    status: GridStatus = GridStatus.NORMAL
    last_reading: Optional[SensorReading] = None
    readings_history: List[SensorReading] = field(default_factory=list)

    def update_reading(self, reading: SensorReading) -> None:
        self.last_reading = reading
        self.readings_history.append(reading)
        if len(self.readings_history) > 100:  # Keep last 100 readings
            self.readings_history.pop(0)
        self._update_status()

    def _update_status(self) -> None:
        if not self.last_reading:
            self.status = GridStatus.OFFLINE
            return

        pressure = self.last_reading.pressure_kpa
        flow = self.last_reading.flow_m3_per_hour

        if pressure < 200:  # Low pressure threshold
            self.status = GridStatus.LOW_PRESSURE
        elif pressure > 800:  # High pressure threshold
            self.status = GridStatus.HIGH_PRESSURE
        elif flow < 50 or flow > 500:  # Flow anomaly thresholds
            self.status = GridStatus.FLOW_ANOMALY
        else:
            self.status = GridStatus.NORMAL


class WaterGridSentinel:
    def __init__(self, grid_name: str = "Nairobi-Machakos Water Grid"):
        self.grid_name = grid_name
        self.nodes: Dict[str, GridNode] = {}
        self.alert_thresholds = {
            "low_pressure_kpa": 200,
            "high_pressure_kpa": 800,
            "min_flow_m3_per_hour": 50,
            "max_flow_m3_per_hour": 500,
        }

    def add_node(self, node_id: str, location: str) -> None:
        if node_id in self.nodes:
            raise ValueError(f"Node {node_id} already exists")
        self.nodes[node_id] = GridNode(node_id=node_id, location=location)
        logger.info(f"Added node {node_id} at {location}")

    def update_node_reading(self, node_id: str, reading: SensorReading) -> None:
        if node_id not in self.nodes:
            raise KeyError(f"Node {node_id} not found")
        self.nodes[node_id].update_reading(reading)

    def get_grid_status(self) -> Dict[str, GridStatus]:
        return {node_id: node.status for node_id, node in self.nodes.items()}

    def get_alerts(self) -> List[Dict[str, str]]:
        alerts = []
        for node_id, node in self.nodes.items():
            if node.status != GridStatus.NORMAL:
                alerts.append({
                    "node_id": node_id,
                    "location": node.location,
                    "status": node.status.value,
                    "last_reading": str(node.last_reading) if node.last_reading else "None"
                })
        return alerts

    def simulate_reading(self, node_id: str, pressure_kpa: float, flow_m3_per_hour: float) -> None:
        reading = SensorReading(
            timestamp=time.time(),
            pressure_kpa=pressure_kpa,
            flow_m3_per_hour=flow_m3_per_hour,
            temperature_c=25.0,
            battery_level=100.0,
            signal_strength=90
        )
        self.update_node_reading(node_id, reading)


if __name__ == "__main__":
    # Test harness
    sentinel = WaterGridSentinel()
    sentinel.add_node("node_1", "Nairobi Central")
    sentinel.add_node("node_2", "Machakos Town")

    # Simulate normal readings
    sentinel.simulate_reading("node_1", 400.0, 200.0)
    sentinel.simulate_reading("node_2", 450.0, 250.0)

    print("Grid Status:", sentinel.get_grid_status())
    print("Alerts:", sentinel.get_alerts())

    # Simulate low pressure
    sentinel.simulate_reading("node_1", 150.0, 200.0)

    print("Grid Status after low pressure:", sentinel.get_grid_status())
    print("Alerts after low pressure:", sentinel.get_alerts())
