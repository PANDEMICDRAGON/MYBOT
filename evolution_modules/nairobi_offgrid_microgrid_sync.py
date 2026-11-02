"""Nairobi Off-Grid Solar Microgrid Frequency Synchronizer & Battery SOC Balancer Sentinel.

Provides robust real-time frequency stabilization, inverter phase-locking, and state-of-charge
(SOC) balancing across distributed lithium-ion storage banks for resilient edge operations in Nairobi.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MicrogridSyncSentinel")


class MicrogridSyncSentinel:
    """Monitors and synchronizes off-grid inverter frequency and battery SOC."""

    def __init__(self, nominal_frequency: float = 50.0, max_frequency_deviation: float = 0.5):
        self.nominal_frequency = nominal_frequency
        self.max_frequency_deviation = max_frequency_deviation
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.system_phase = 0.0

    lambda_register_node = lambda self, node_id, capacity_kwh, soc, frequency: self.nodes.update({
        node_id: {
            "capacity_kwh": capacity_kwh,
            "soc": max(0.0, min(100.0, soc)),
            "frequency": frequency,
            "status": "ACTIVE",
            "last_sync": time.time()
        }
    })

    def update_telemetry(self, node_id: str, soc: float, frequency: float) -> Optional[Dict[str, Any]]:
        """Updates telemetry for a specific inverter/battery node."""
        if node_id not in self.nodes:
            logger.warning(f"Node {node_id} not registered. Auto-registering.")
            self.register_node(node_id, 10.0, soc, frequency)
        
        node = self.nodes[node_id]
        node["soc"] = max(0.0, min(100.0, soc))
        node["frequency"] = frequency
        node["last_sync"] = time.time()

        # Check health
        freq_delta = abs(frequency - self.nominal_frequency)
        if freq_delta > self.max_frequency_deviation:
            node["status"] = "WARNING_FREQ_DRIFT"
            logger.warning(f"Node {node_id} frequency drift detected: {frequency:.2f} Hz (Delta: {freq_delta:.2f})")
        else:
            node["status"] = "ACTIVE"
            
        return node

    def compute_droop_compensation(self) -> Dict[str, float]:
        """Computes active power droop compensation to balance load across nodes."""
        adjustments = {}
        active_nodes = {k: v for k, v in self.nodes.items() if v["status"] != "OFFLINE"}
        if not active_nodes:
            return adjustments

        avg_soc = sum(n["soc"] for n in active_nodes.values()) / len(active_nodes)

        for node_id, node in active_nodes.items():
            # Droop curve: if SOC is lower than average, reduce discharge rate; if higher, increase
            soc_diff = node["soc"] - avg_soc
            power_adjustment_factor = 1.0 + (soc_diff * 0.01) # 1% power shift per 1% SOC difference
            adjustments[node_id] = round(max(0.5, min(1.5, power_adjustment_factor)), 4)

        return adjustments

    def run_harmonic_sync_cycle(self) -> Dict[str, Any]:
        """Executes a synchronization cycle across all registered microgrid nodes."""
        now = time.time()
        offline_timeout = 10.0
        
        for node_id, node in self.nodes.items():
            if now - node["last_sync"] > offline_timeout:
                node["status"] = "OFFLINE"

        adjustments = self.compute_droop_compensation()
        active_count = sum(1 for n in self.nodes.values() if n["status"] == "ACTIVE")

        return {
            "timestamp": now,
            "active_nodes": active_count,
            "total_nodes": len(self.nodes),
            "droop_adjustments": adjustments,
            "system_stable": all(n["status"] == "ACTIVE" for n in self.nodes.values())
        }


if __name__ == "__main__":
    sentinel = MicrogridSyncSentinel()
    sentinel.register_node("nrb_solar_node_alpha", 15.0, 85.0, 50.02)
    sentinel.register_node("nrb_solar_node_beta", 20.0, 72.5, 49.85)
    
    sync_result = sentinel.run_harmonic_sync_cycle()
    logger.info(f"Microgrid Sync Cycle Executed Successfully: {sync_result}")
