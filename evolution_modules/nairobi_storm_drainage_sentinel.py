import time
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DrainageStatus(Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    BLOCKED = "blocked"

@dataclass
class DrainageNode:
    node_id: str
    location: str
    capacity_lps: float  # Liters per second
    current_flow_lps: float = 0.0
    debris_level_pct: float = 0.0
    status: DrainageStatus = DrainageStatus.NORMAL
    last_updated: float = field(default_factory=time.time)

    def update(self, flow: float, debris: float) -> None:
        """Update node status based on new sensor readings."""
        self.current_flow_lps = flow
        self.debris_level_pct = debris
        self.last_updated = time.time()
        
        # Determine status
        if self.debris_level_pct > 80 or self.current_flow_lps > self.capacity_lps * 1.2:
            self.status = DrainageStatus.BLOCKED
        elif self.debris_level_pct > 60 or self.current_flow_lps > self.capacity_lps * 0.9:
            self.status = DrainageStatus.CRITICAL
        elif self.debris_level_pct > 40 or self.current_flow_lps > self.capacity_lps * 0.7:
            self.status = DrainageStatus.WARNING
        else:
            self.status = DrainageStatus.NORMAL

@dataclass
class Alert:
    node_id: str
    status: DrainageStatus
    timestamp: float
    message: str
    action_required: bool

class NairobiStormDrainageSentinel:
    """
    Monitors storm drainage nodes across Nairobi to detect and predict
    flooding risks due to blockages or excessive flow.
    """
    
    def __init__(self, nodes: List[DrainageNode]):
        self.nodes = {node.node_id: node for node in nodes}
        self.alerts: List[Alert] = []
        self.maintenance_queue: List[str] = []
        
    def simulate_sensor_readings(self) -> None:
        """Simulate new sensor data for all nodes."""
        for node in self.nodes.values():
            # Simulate random fluctuations
            flow_variation = random.uniform(-0.1, 0.2) * node.current_flow_lps
            debris_variation = random.uniform(-0.05, 0.1) * node.debris_level_pct
            
            new_flow = max(0, node.current_flow_lps + flow_variation + random.uniform(0, 5))
            new_debris = min(100, max(0, node.debris_level_pct + debris_variation + random.uniform(0, 2)))
            
            node.update(new_flow, new_debris)
            
            # Generate alert if status changes to critical or blocked
            if node.status in [DrainageStatus.CRITICAL, DrainageStatus.BLOCKED]:
                if node.node_id not in self.maintenance_queue:
                    self.maintenance_queue.append(node.node_id)
                    alert = Alert(
                        node_id=node.node_id,
                        status=node.status,
                        timestamp=time.time(),
                        message=f"Drainage node {node.node_id} at {node.location} is {node.status.value}",
                        action_required=True
                    )
                    self.alerts.append(alert)
                    logger.warning(alert.message)

    def get_critical_nodes(self) -> List[DrainageNode]:
        """Return list of nodes in critical or blocked state."""
        return [node for node in self.nodes.values() 
                if node.status in [DrainageStatus.CRITICAL, DrainageStatus.BLOCKED]]

    def get_maintenance_schedule(self) -> List[str]:
        """Return list of node IDs requiring maintenance."""
        return self.maintenance_queue.copy()

    def clear_maintenance(self, node_id: str) -> bool:
        """Mark a node as maintained and reset its status."""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.debris_level_pct = 0.0
            node.current_flow_lps = node.capacity_lps * 0.5
            node.status = DrainageStatus.NORMAL
            if node_id in self.maintenance_queue:
                self.maintenance_queue.remove(node_id)
            return True
        return False

    def generate_report(self) -> Dict:
        """Generate a summary report of drainage system health."""
        total_nodes = len(self.nodes)
        critical_count = len(self.get_critical_nodes())
        warning_count = sum(1 for node in self.nodes.values() if node.status == DrainageStatus.WARNING)
        
        return {
            "total_nodes": total_nodes,
            "critical_nodes": critical_count,
            "warning_nodes": warning_count,
            "maintenance_queue": self.maintenance_queue,
            "system_health": "CRITICAL" if critical_count > 0 else "WARNING" if warning_count > 0 else "NORMAL"
        }

if __name__ == "__main__":
    # Create sample drainage nodes
    nodes = [
        DrainageNode("D001", "Westlands Junction", 50.0, 20.0, 10.0),
        DrainageNode("D002", "Nairobi CBD", 80.0, 60.0, 45.0),
        DrainageNode("D003", "Thika Road", 60.0, 30.0, 20.0),
        DrainageNode("D004", "Kilimani", 40.0, 15.0, 5.0)
    ]
    
    sentinel = NairobiStormDrainageSentinel(nodes)
    
    # Run simulation for 5 cycles
    for i in range(5):
        print(f"\n--- Simulation Cycle {i+1} ---")
        sentinel.simulate_sensor_readings()
        report = sentinel.generate_report()
        print(f"System Health: {report['system_health']}")
        print(f"Critical Nodes: {report['critical_nodes']}")
        print(f"Maintenance Queue: {report['maintenance_queue']}")
        
        # Simulate maintenance for critical nodes
        for node_id in sentinel.get_maintenance_schedule():
            if random.random() > 0.5:  # 50% chance of maintenance being completed
                sentinel.clear_maintenance(node_id)
                print(f"Maintenance completed for {node_id}")
    
    print("\nFinal Report:")
    final_report = sentinel.generate_report()
    for key, value in final_report.items():
        print(f"{key}: {value}")