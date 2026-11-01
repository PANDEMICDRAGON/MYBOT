"""
Nairobi Edge Datacenter Immersion Cooling & Dielectric Breakdown Sentinel
Provides continuous monitoring, anomaly detection, and automated load balancing for high-density 
liquid immersion cooling infrastructure hosting Cortana edge nodes in Nairobi.
"""

import time
import math
import random
import json
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("NairobiImmersionCoolingSentinel")

@dataclass
class CoolantTelemetry:
    node_id: str
    timestamp: float
    dielectric_breakdown_kv: float  # kV (Normal: 40.0 - 60.0)
    fluid_temperature_c: float     # °C (Normal: 35.0 - 55.0)
    viscosity_cst: float            # cSt (Normal: 8.0 - 15.0)
    moisture_ppm: float             # ppm (Normal: < 25.0)
    particulate_count_pml: int      # particles per mL > 4µm (Normal: < 500)
    flow_rate_lpm: float            # Liters per minute (Normal: 12.0 - 25.0)

@dataclass
class HealthStatus:
    node_id: str
    health_score: float             # 0.0 to 100.0
    status_label: str               # "OPTIMAL", "WARNING", "CRITICAL"
    dielectric_margin: float        # Remaining kV safety margin
    thermal_impedance_index: float
    recommended_action: str

class ImmersionCoolingSentinel:
    """
    Monitors single-phase & two-phase dielectric fluid immersion tanks hosting 
    high-density compute racks in Nairobi edge datacenters. Prevents catastrophic thermal runaway 
    and electrical arcing in high-voltage silicon packages.
    """
    
    # Operational thresholds
    MIN_DIELECTRIC_KV: float = 30.0  # Below 30kV poses high risk of arcing
    MAX_TEMP_C: float = 65.0         # Upper safe operating fluid temperature
    MAX_MOISTURE_PPM: float = 50.0   # Moisture decreases dielectric strength drastically
    MAX_PARTICULATE: int = 1200      # Suspended metallic/dust particles
    MIN_FLOW_RATE_LPM: float = 8.0   # Minimum circulation rate

    def __init__(self, node_ids: List[str]):
        self.node_ids = node_ids
        self.history: Dict[str, List[CoolantTelemetry]] = {nid: [] for nid in node_ids}
        self.max_history_depth: int = 100
        logger.info(f"Initialized Immersion Cooling Sentinel for nodes: {node_ids}")

    def ingest_telemetry(self, telemetry: CoolantTelemetry) -> None:
        """Ingests raw sensor readings into rolling window buffer."""
        if telemetry.node_id not in self.history:
            self.history[telemetry.node_id] = []
        
        self.history[telemetry.node_id].append(telemetry)
        if len(self.history[telemetry.node_id]) > self.max_history_depth:
            self.history[telemetry.node_id].pop(0)

    def evaluate_node_health(self, node_id: str) -> HealthStatus:
        """Evaluates health score and determines corrective actions based on physics-informed rules."""
        if node_id not in self.history or not self.history[node_id]:
            return HealthStatus(
                node_id=node_id,
                health_score=0.0,
                status_label="UNKNOWN",
                dielectric_margin=0.0,
                thermal_impedance_index=1.0,
                recommended_action="INSUFFICIENT_TELEMETRY"
            )

        latest = self.history[node_id][-1]

        # Calculate dielectric risk penalty
        dielectric_margin = latest.dielectric_breakdown_kv - self.MIN_DIELECTRIC_KV
        dielectric_penalty = 0.0
        if dielectric_margin < 0:
            dielectric_penalty = 50.0
        elif dielectric_margin < 10.0:
            dielectric_penalty = (10.0 - dielectric_margin) * 4.0

        # Thermal penalty
        temp_penalty = 0.0
        if latest.fluid_temperature_c > self.MAX_TEMP_C:
            temp_penalty = min(40.0, (latest.fluid_temperature_c - self.MAX_TEMP_C) * 3.0)

        # Moisture penalty
        moisture_penalty = 0.0
        if latest.moisture_ppm > self.MAX_MOISTURE_PPM:
            moisture_penalty = min(30.0, (latest.moisture_ppm - self.MAX_MOISTURE_PPM) * 1.5)

        # Calculate overall score
        raw_score = 100.0 - (dielectric_penalty + temp_penalty + moisture_penalty)
        health_score = max(0.0, min(100.0, raw_score))

        # Determine status label & action
        if health_score >= 80.0:
            status_label = "OPTIMAL"
            action = "MAINTAIN_NORMAL_OPERATIONS"
        elif health_score >= 50.0:
            status_label = "WARNING"
            if latest.moisture_ppm > self.MAX_MOISTURE_PPM:
                action = "ENABLE_DESICCANT_FLUID_RECIRCULATION"
            elif latest.fluid_temperature_c > self.MAX_TEMP_C:
                action = "INCREASE_AUXILIARY_PUMP_SPEED"
            else:
                action = "SCHEDULE_FLUID_FILTRATION"
        else:
            status_label = "CRITICAL"
            if latest.dielectric_breakdown_kv < self.MIN_DIELECTRIC_KV:
                action = "EMERGENCY_SHED_HIGH_VOLTAGE_LOAD_IMMEDIATE"
            else:
                action = "ACTIVATE_SECONDARY_HEAT_EXCHANGER_AND_THROTTLE"

        # Thermal impedance index proxy
        thermal_impedance = (latest.fluid_temperature_c / 40.0) * (latest.viscosity_cst / 10.0)

        return HealthStatus(
            node_id=node_id,
            health_score=round(health_score, 2),
            status_label=status_label,
            dielectric_margin=round(dielectric_margin, 2),
            thermal_impedance_index=round(thermal_impedance, 2),
            recommended_action=action
        )

    def analyze_all_nodes(self) -> Dict[str, Dict]:
        """Runs batch health evaluation for all monitored immersion tanks."""
        report = {}
        for nid in self.node_ids:
            health = self.evaluate_node_health(nid)
            report[nid] = asdict(health)
        return report

# Test Harness
if __name__ == "__main__":
    nodes = ["nairobi-dc1-tank-01", "nairobi-dc1-tank-02"]
    sentinel = ImmersionCoolingSentinel(nodes)

    # Simulate optimal telemetry
    t1 = CoolantTelemetry(
        node_id="nairobi-dc1-tank-01",
        timestamp=time.time(),
        dielectric_breakdown_kv=48.5,
        fluid_temperature_c=42.0,
        viscosity_cst=11.2,
        moisture_ppm=12.4,
        particulate_count_pml=210,
        flow_rate_lpm=18.5
    )

    # Simulate degraded dielectric telemetry
    t2 = CoolantTelemetry(
        node_id="nairobi-dc1-tank-02",
        timestamp=time.time(),
        dielectric_breakdown_kv=28.1,  # Critical drop
        fluid_temperature_c=68.2,       # Overheating
        viscosity_cst=16.8,
        moisture_ppm=58.9,               # Moisture contamination
        particulate_count_pml=1450,
        flow_rate_lpm=7.2
    )

    sentinel.ingest_telemetry(t1)
    sentinel.ingest_telemetry(t2)

    results = sentinel.analyze_all_nodes()
    print(json.dumps(results, indent=2))
