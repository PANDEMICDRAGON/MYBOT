"""
Nairobi Commercial Grease Trap & Effluent Sentinel
Autonomous Evolutionary Module #324
Designed for Cortana's Autonomous Evolutionary Architecture
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [GreaseTrapSentinel] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class GreaseTrapMetrics:
    trap_id: str
    temperature_celsius: float
    oil_grease_layer_cm: float
    ph_level: float
    flow_rate_lpm: float
    enzyme_dispenser_active: bool
    timestamp: float = field(default_factory=time.time)

class NairobiCommercialGreaseTrapSentinel:
    """
    Monitors commercial kitchen grease traps, analyzes FOG accumulation,
    manages biological enzyme dosing, and prevents municipal sewer compliance breaches.
    """
    
    MAX_FOG_THRESHOLD_CM = 15.0  # Max acceptable fat layer before emergency pump-out
    MIN_PH_THRESHOLD = 5.5
    MAX_PH_THRESHOLD = 9.0
    OPTIMAL_TEMP_C = 40.0        # Above this can melt FOG and bypass separation

    def __init__(self, trap_id: str):
        self.trap_id = trap_id
        self.history: List[GreaseTrapMetrics] = []
        logger.info(f"Initialized GreaseTrapSentinel for Trap: {self.trap_id}")

    def ingest_telemetry(self, temp: float, fog_cm: float, ph: float, flow_lpm: float, enzyme_active: bool) -> GreaseTrapMetrics:
        metrics = GreaseTrapMetrics(
            trap_id=self.trap_id,
            temperature_celsius=temp,
            oil_grease_layer_cm=fog_cm,
            ph_level=ph,
            flow_rate_lpm=flow_lpm,
            enzyme_dispenser_active=enzyme_active
        )
        self.history.append(metrics)
        return metrics

    def evaluate_compliance(self, metrics: GreaseTrapMetrics) -> Dict[str, Any]:
        alerts = []
        actions = []
        status = "OPTIMAL"

        if metrics.oil_grease_layer_cm >= self.MAX_FOG_THRESHOLD_CM:
            status = "CRITICAL"
            alerts.append(f"FOG layer critical ({metrics.oil_grease_layer_cm} cm). Immediate pump-out required.")
            actions.append("DISPATCH_EXHAUSTER_TRUCK")
        elif metrics.oil_grease_layer_cm >= (self.MAX_FOG_THRESHOLD_CM * 0.75):
            status = "WARNING"
            alerts.append(f"FOG layer high ({metrics.oil_grease_layer_cm} cm). Schedule maintenance.")
            actions.append("SCHEDULE_MAINTENANCE")

        if not metrics.enzyme_dispenser_active and status != "OPTIMAL":
            actions.append("TRIGGER_BIO_ENZYME_DOSING")

        if metrics.ph_level < self.MIN_PH_THRESHOLD or metrics.ph_level > self.MAX_PH_THRESHOLD:
            status = "WARNING"
            alerts.append(f"Effluent pH out of range ({metrics.ph_level}). Risk of pipe corrosion or bio-culture die-off.")
            actions.append("DISPATCH_NEUTRALIZER_DOSER")

        return {
            "trap_id": metrics.trap_id,
            "status": status,
            "alerts": alerts,
            "recommended_actions": actions,
            "timestamp": metrics.timestamp
        }

if __name__ == "__main__":
    print("--- Executing Nairobi Commercial Grease Trap Sentinel Test Harness ---")
    sentinel = NairobiCommercialGreaseTrapSentinel(trap_id="TRAP-WESTLANDS-04")
    sample = sentinel.ingest_telemetry(
        temp=38.5,
        fog_cm=12.2,
        ph=6.8,
        flow_lpm=45.0,
        enzyme_active=False
    )
    report = sentinel.evaluate_compliance(sample)
    print(json.dumps(report, indent=2))
    print("--- Test Harness Completed Successfully ---")
