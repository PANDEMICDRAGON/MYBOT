"""
Nairobi Urban Organic Waste Biodigester & Biogas Energy Grid Sentinel
Designed and implemented autonomously by Cortana for Michael Obiero in Nairobi, Kenya.
"""

import json
import hashlib
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class BiodigesterNode:
    node_id: str
    location: str
    capacity_m3: float
    substrate_type: str  # e.g., 'market_waste', 'kitchen_refuse', 'livestock_manure'
    internal_temp_c: float
    ph_level: float
    pressure_kpa: float
    gas_yield_m3_day: float
    status: str = "ACTIVE"


class NairobiBiogasSentinel:
    """
    Monitors anaerobic digestion units across Nairobi, forecasting gas yields,
    ensuring structural and chemical safety (temperature and pH balance),
    and logging tokenized energy distribution to local households.
    """

    def __init__(self, operator: str = "Michael Obiero") -> None:
        self.operator = operator
        self.nodes: Dict[str, BiodigesterNode] = {}
        self.ledger: List[Dict[str, Any]] = []

    def register_node(self, node: BiodigesterNode) -> None:
        """Register a new biodigester node in the Nairobi network."""
        self.nodes[node.node_id] = node
        self._record_event("NODE_REGISTERED", {"node_id": node.node_id, "location": node.location})

    def ingest_telemetry(self, node_id: str, temp_c: float, ph: float, pressure_kpa: float, yield_m3: float) -> Dict[str, Any]:
        """Ingest live telemetry from a biodigester and check safety parameters."""
        if node_id not in self.nodes:
            raise ValueError(f"Biodigester node {node_id} not found in Nairobi registry.")

        node = self.nodes[node_id]
        node.internal_temp_c = temp_c
        node.ph_level = ph
        node.pressure_kpa = pressure_kpa
        node.gas_yield_m3_day = yield_m3

        alerts = []
        # Mesophilic temperature optimum: 35C - 40C
        if not (32.0 <= temp_c <= 42.0):
            alerts.append(f"WARNING: Temperature anomaly ({temp_c}C) at {node_id}. Optimal: 35-40C")
        
        # Optimal pH: 6.8 - 8.0
        if not (6.5 <= ph <= 8.2):
            alerts.append(f"CRITICAL: pH imbalance ({ph}) at {node_id}. Risk of methanogen inhibition.")

        # Overpressure safety threshold: > 150 kPa
        if pressure_kpa > 150.0:
            alerts.append(f"EMERGENCY: High pressure ({pressure_kpa} kPa) at {node_id}. Venting recommended.")

        status_update = {
            "node_id": node_id,
            "timestamp": time.time(),
            "temp_c": temp_c,
            "ph": ph,
            "pressure_kpa": pressure_kpa,
            "yield_m3": yield_m3,
            "alerts": alerts
        }
        self._record_event("TELEMETRY_INGEST", status_update)
        return status_update

    def audit_energy_distribution(self, node_id: str, recipient_household: str, volume_m3: float) -> Dict[str, Any]:
        """Record distributed clean cooking gas to local Nairobi households."""
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} does not exist.")
        
        node = self.nodes[node_id]
        if node.gas_yield_m3_day < volume_m3:
            raise ValueError("Insufficient gas yield reserves for requested distribution.")

        node.gas_yield_m3_day -= volume_m3
        tx = {
            "node_id": node_id,
            "recipient": recipient_household,
            "volume_m3": volume_m3,
            "timestamp": time.time(),
            "operator_guard": self.operator
        }
        self._record_event("GAS_DISTRIBUTION", tx)
        return tx

    def _record_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        payload_str = json.dumps(payload, sort_keys=True)
        prev_hash = self.ledger[-1]["hash"] if self.ledger else "0" * 64
        block_data = f"{event_type}:{payload_str}:{prev_hash}:{time.time()}"
        block_hash = hashlib.sha256(block_data.encode("utf-8")).hexdigest()
        
        self.ledger.append({
            "event_type": event_type,
            "payload": payload,
            "prev_hash": prev_hash,
            "hash": block_hash,
            "timestamp": time.time()
        })


if __name__ == "__main__":
    print("Initializing Nairobi Urban Organic Waste Biodigester Sentinel for Michael Obiero...")
    sentinel = NairobiBiogasSentinel(operator="Michael Obiero")
    
    node_alpha = BiodigesterNode(
        node_id="BIO-NBO-01",
        location="Kawangware Market",
        capacity_m3=50.0,
        substrate_type="market_produce_waste",
        internal_temp_c=37.5,
        ph_level=7.2,
        pressure_kpa=85.0,
        gas_yield_m3_day=42.0
    )
    
    sentinel.register_node(node_alpha)
    telemetry = sentinel.ingest_telemetry("BIO-NBO-01", temp_c=38.1, ph=7.1, pressure_kpa=92.0, yield_m3=41.5)
    print("Telemetry Ingestion Result:", json.dumps(telemetry, indent=2))
    
    distribution = sentinel.audit_energy_distribution("BIO-NBO-01", "Household_Kawangware_99", 3.5)
    print(
        "Energy Distribution Recorded Successfully. Ledger Blocks:",
        len(sentinel.ledger)
    )
