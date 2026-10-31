import time
import json
import random
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SGR_Cycloid")

class TransportMode(Enum):
    RAIL = "rail"
    BODA = "boda"
    MATATU = "matatu"
    TRUCK = "truck"

@dataclass
class FreightUnit:
    id: str
    weight_kg: float
    destination: str
    priority: int  # 1 (low) to 5 (high)
    current_mode: TransportMode = TransportMode.RAIL
    status: str = "at_terminal"
    timestamp: float = field(default_factory=time.time)

@dataclass
class MicroLogisticsNode:
    id: str
    capacity_kg: float
    speed_kmh: float
    cost_per_km: float
    reliability: float  # 0.0 to 1.0

    def calculate_cost(self, distance_km: float) -> float:
        return self.cost_per_km * distance_km

class SGRRailCycloidOptimizer:
    """
    Optimizes the handoff of freight from SGR rail terminals to local micro-logistics nodes.
    Uses a cycloid-based pathing algorithm to minimize total cost and time while respecting
    weight and reliability constraints.
    """

    def __init__(self, terminal_id: str):
        self.terminal_id = terminal_id
        self.nodes: Dict[str, MicroLogisticsNode] = {}
        self.pending_freight: List[FreightUnit] = []
        self.dispatch_log: List[Dict] = []
        self._seed = int(time.time())

    def register_node(self, node: MicroLogisticsNode) -> None:
        """Register a micro-logistics node (boda, matatu, truck)."""
        self.nodes[node.id] = node
        logger.info(f"Registered node {node.id} (mode: {node.capacity_kg}kg)")

    def add_freight(self, freight: FreightUnit) -> None:
        """Add a freight unit to the pending queue."""
        self.pending_freight.append(freight)
        logger.info(f"Added freight {freight.id} to queue")

    def _cycloid_score(self, node: MicroLogisticsNode, freight: FreightUnit, distance_km: float) -> float:
        """
        Calculate a cycloid score for a node-freight pair.
        Lower score is better. Factors in cost, time, reliability, and weight fit.
        """
        if freight.weight_kg > node.capacity_kg:
            return float('inf')

        cost = node.calculate_cost(distance_km)
        time_estimate = distance_km / node.speed_kmh
        reliability_penalty = (1.0 - node.reliability) * 100
        weight_utilization = freight.weight_kg / node.capacity_kg
        # Cycloid curve: penalizes low utilization and high cost
        score = cost + (time_estimate * 10) + reliability_penalty + (1.0 - weight_utilization) * 5
        return score

    def optimize_dispatch(self, distance_km: float = 5.0) -> List[Dict]:
        """
        Optimize the dispatch of pending freight to available nodes.
        Returns a list of dispatch instructions.
        """
        if not self.pending_freight:
            return []

        # Sort freight by priority (high to low)
        sorted_freight = sorted(self.pending_freight, key=lambda f: f.priority, reverse=True)
        dispatches = []
        available_nodes = list(self.nodes.values())

        for freight in sorted_freight:
            best_node = None
            best_score = float('inf')
            for node in available_nodes:
                score = self._cycloid_score(node, freight, distance_km)
                if score < best_score:
                    best_score = score
                    best_node = node

            if best_node:
                freight.current_mode = TransportMode.BODA if best_node.capacity_kg < 50 else TransportMode.MATATU
                freight.status = "dispatched"
                dispatch = {
                    "freight_id": freight.id,
                    "node_id": best_node.id,
                    "cost": best_node.calculate_cost(distance_km),
                    "score": best_score,
                    "timestamp": time.time()
                }
                dispatches.append(dispatch)
                self.dispatch_log.append(dispatch)
                logger.info(f"Dispatched freight {freight.id} to node {best_node.id} (score: {best_score:.2f})")
            else:
                freight.status = "unassigned"
                logger.warning(f"No suitable node for freight {freight.id}")

        self.pending_freight.clear()
        return dispatches

    def get_status(self) -> Dict:
        """Return the current status of the optimizer."""
        return {
            "terminal_id": self.terminal_id,
            "pending_freight": len(self.pending_freight),
            "registered_nodes": len(self.nodes),
            "total_dispatches": len(self.dispatch_log)
        }

if __name__ == "__main__":
    # Test Harness
    optimizer = SGRRailCycloidOptimizer("Nairobi_Rail_Terminal")

    # Register nodes
    optimizer.register_node(MicroLogisticsNode("boda_001", capacity_kg=50, speed_kmh=40, cost_per_km=2.0, reliability=0.95))
    optimizer.register_node(MicroLogisticsNode("matatu_001", capacity_kg=500, speed_kmh=30, cost_per_km=5.0, reliability=0.90))
    optimizer.register_node(MicroLogisticsNode("truck_001", capacity_kg=5000, speed_kmh=60, cost_per_km=10.0, reliability=0.98))

    # Add freight
    optimizer.add_freight(FreightUnit("F001", weight_kg=30, destination="Westlands", priority=5))
    optimizer.add_freight(FreightUnit("F002", weight_kg=300, destination="Kilimani", priority=3))
    optimizer.add_freight(FreightUnit("F003", weight_kg=2000, destination="Industrial Area", priority=1))

    # Optimize
    dispatches = optimizer.optimize_dispatch(distance_km=10.0)
    print(json.dumps(dispatches, indent=2))
    print(optimizer.get_status())
