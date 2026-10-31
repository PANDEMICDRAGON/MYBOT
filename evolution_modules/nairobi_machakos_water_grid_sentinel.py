import time
import random
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class PressureStatus(Enum):
    NORMAL = "normal"
    LOW = "low"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class WaterNode:
    node_id: str
    name: str
    pressure: float  # in PSI
    flow_rate: float  # in L/min
    last_updated: float


class NairobiMachakosWaterGridSentinel:
    """
    Monitors the water grid pressure and flow rates for the Nairobi-Machakos corridor.
    Predicts potential failures based on historical trends and current anomalies.
    """

    def __init__(self, nodes: List[WaterNode]):
        self.nodes = {node.node_id: node for node in nodes}
        self.alerts: List[Dict] = []
        self.history: Dict[str, List[float]] = {node_id: [] for node_id in self.nodes}

    def update_node(self, node_id: str, pressure: float, flow_rate: float) -> None:
        """Update the status of a specific water node."""
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found in grid")
        
        node = self.nodes[node_id]
        node.pressure = pressure
        node.flow_rate = flow_rate
        node.last_updated = time.time()
        
        # Keep last 100 readings for trend analysis
        self.history[node_id].append(pressure)
        if len(self.history[node_id]) > 100:
            self.history[node_id].pop(0)

    def check_pressure_status(self, node_id: str) -> PressureStatus:
        """Determine the current pressure status of a node."""
        node = self.nodes[node_id]
        if node.pressure < 20:
            return PressureStatus.CRITICAL
        elif node.pressure < 40:
            return PressureStatus.LOW
        elif node.pressure > 100:
            return PressureStatus.HIGH
        else:
            return PressureStatus.NORMAL

    def predict_failure_probability(self, node_id: str) -> float:
        """
        Predict the probability of a pipe burst or major failure
        based on pressure variance and trend.
        """
        if len(self.history[node_id]) < 10:
            return 0.0

        recent = self.history[node_id][-10:]
        mean = sum(recent) / len(recent)
        variance = sum((x - mean) ** 2 for x in recent) / len(recent)
        std_dev = variance ** 0.5

        # High variance and low mean pressure indicate potential issues
        risk_score = (std_dev / mean) if mean > 0 else 0
        if mean < 40:
            risk_score *= 1.5

        return min(risk_score, 1.0)

    def generate_alerts(self) -> List[Dict]:
        """Generate alerts for nodes with critical or high risk status."""
        self.alerts = []
        for node_id, node in self.nodes.items():
            status = self.check_pressure_status(node_id)
            risk = self.predict_failure_probability(node_id)

            if status == PressureStatus.CRITICAL or risk > 0.7:
                self.alerts.append({
                    "node_id": node_id,
                    "node_name": node.name,
                    "status": status.value,
                    "risk_probability": risk,
                    "pressure": node.pressure,
                    "flow_rate": node.flow_rate,
                    "timestamp": node.last_updated
                })
        return self.alerts

    def get_grid_summary(self) -> Dict:
        """Provide a summary of the entire water grid status."""
        total_nodes = len(self.nodes)
        critical_nodes = sum(1 for node_id in self.nodes if self.check_pressure_status(node_id) == PressureStatus.CRITICAL)
        high_risk_nodes = sum(1 for node_id in self.nodes if self.predict_failure_probability(node_id) > 0.7)
        
        return {
            "total_nodes": total_nodes,
            "critical_nodes": critical_nodes,
            "high_risk_nodes": high_risk_nodes,
            "alerts": self.generate_alerts()
        }


def main():
    """Test harness for the Nairobi-Machakos Water Grid Sentinel."""
    # Initialize with sample nodes
    nodes = [
        WaterNode("N001", "Machakos Treatment Plant", 60.0, 500.0, time.time()),
        WaterNode("N002", "Nairobi North Pumping Station", 55.0, 450.0, time.time()),
        WaterNode("N003", "Kilimani Distribution Hub", 50.0, 300.0, time.time()),
        WaterNode("N004", "Westlands Reservoir", 45.0, 250.0, time.time())
    ]

    sentinel = NairobiMachakosWaterGridSentinel(nodes)

    # Simulate some data updates
    for _ in range(20):
        for node_id in sentinel.nodes:
            # Simulate normal fluctuations
            base_pressure = 50.0
            pressure = base_pressure + random.uniform(-5, 5)
            flow_rate = 300.0 + random.uniform(-20, 20)
            sentinel.update_node(node_id, pressure, flow_rate)

    # Simulate a critical failure in one node
    sentinel.update_node("N003", 15.0, 50.0)

    # Generate alerts
    alerts = sentinel.generate_alerts()
    print("Active Alerts:")
    for alert in alerts:
        print(f"  - {alert['node_name']}: {alert['status']} (Risk: {alert['risk_probability']:.2f})")

    # Get grid summary
    summary = sentinel.get_grid_summary()
    print(f"\nGrid Summary: {summary['total_nodes']} nodes, {summary['critical_nodes']} critical, {summary['high_risk_nodes']} high risk")


if __name__ == "__main__":
    main()