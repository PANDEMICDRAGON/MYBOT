"""
Distributed Multi-Node Swarm Heartbeat Arbiter.
Generated autonomously by Cortana Continuous Self-Evolution Core.
"""

import time
from typing import Dict, Any

class SwarmHeartbeatArbiter:
    """Tracks active nodes in the Cortana construct and computes swarm health index."""
    def __init__(self, heartbeat_timeout: float = 120.0):
        self.timeout = heartbeat_timeout
        self.nodes: Dict[str, float] = {}

    def record_heartbeat(self, node_id: str):
        self.nodes[node_id] = time.time()

    def get_swarm_health(self) -> Dict[str, Any]:
        now = time.time()
        active = [nid for nid, last in self.nodes.items() if now - last <= self.timeout]
        stale = [nid for nid, last in self.nodes.items() if now - last > self.timeout]
        health_pct = (len(active) / len(self.nodes) * 100.0) if self.nodes else 100.0
        return {
            "active_nodes": active,
            "stale_nodes": stale,
            "health_pct": round(health_pct, 1),
            "status": "ALL_SYSTEMS_NOMINAL" if not stale else "DEGRADED_NODES"
        }

if __name__ == "__main__":
    arbiter = SwarmHeartbeatArbiter(heartbeat_timeout=10.0)
    arbiter.record_heartbeat("workstation_daemon")
    arbiter.record_heartbeat("vercel_cloud_node")
    res = arbiter.get_swarm_health()
    assert len(res["active_nodes"]) == 2
    print(f"SwarmHeartbeatArbiter verified: {res}")
