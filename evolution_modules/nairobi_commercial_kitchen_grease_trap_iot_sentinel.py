"""Nairobi Commercial Kitchen Grease Trap IoT Telemetry & Fatberg Prevention Sentinel.

Provides real-time IoT monitoring, temperature stratification analysis, oil-layer depth
estimation, and automated compliance logging for commercial kitchens in Nairobi, Kenya.
"""

import time
import math
import random
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s')
logger = logging.getLogger("GreaseTrapSentinel")

@dataclass
class TrapMetrics:
    trap_id: str
    water_temp_c: float
    ambient_temp_c: float
    oil_layer_depth_mm: float
    sludge_depth_mm: float
    flow_rate_lpm: float
    ph_level: float
    timestamp: float = field(default_factory=time.time)

class GreaseTrapSentinel:
    """Monitors commercial kitchen grease traps to prevent fatbergs and ensure Nairobi County bylaws compliance."""
    
    MAX_OIL_DEPTH_MM = 50.0
    MAX_SLUDGE_DEPTH_MM = 75.0
    MIN_PH = 6.0
    MAX_PH = 9.0
    OPTIMAL_WATER_TEMP_C = 45.0

    def __init__(self, trap_id: str):
        self.trap_id = trap_id
        self.alert_history: List[str] = []

    def evaluate_telemetry(self, metrics: TrapMetrics) -> Dict[str, Any]:
        """Analyzes trap metrics against threshold parameters and outputs status and remediation."""
        status = "OPTIMAL"
        actions = []

        if metrics.oil_layer_depth_mm > self.MAX_OIL_DEPTH_MM:
            status = "WARNING"
            actions.append("Schedule immediate FOG vacuum truck extraction; oil layer exceeds tolerance.")

        if metrics.sludge_depth_mm > self.MAX_SLUDGE_DEPTH_MM:
            status = "CRITICAL"
            actions.append("Solid food sediment layer critically high; manual bailing and basket flush required.")

        if not (self.MIN_PH <= metrics.ph_level <= self.MAX_PH):
            status = "CRITICAL"
            actions.append(f"pH level {metrics.ph_level} out of compliance [6.0-9.0]. Check enzymatic dosing unit.")

        if metrics.water_temp_c > 65.0:
            actions.append("Inflow water temperature excessive; risks emulsifying grease past baffle walls.")

        risk_score = min(100.0, (
            (metrics.oil_layer_depth_mm / self.MAX_OIL_DEPTH_MM) * 40.0 +
            (metrics.sludge_depth_mm / self.MAX_SLUDGE_DEPTH_MM) * 40.0 +
            (0.0 if self.MIN_PH <= metrics.ph_level <= self.MAX_PH else 20.0)
        ))

        evaluation = {
            "trap_id": self.trap_id,
            "status": status,
            "risk_score": round(risk_score, 2),
            "actions_required": actions,
            "timestamp": metrics.timestamp
        }

        if status != "OPTIMAL":
            self.alert_history.append(str(evaluation))
            logger.warning(f"Grease Trap Alert [{self.trap_id}]: {status} - Risk: {risk_score}%")

        return evaluation

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Kitchen Grease Trap IoT Sentinel...")
    sentinel = GreaseTrapSentinel(trap_id="TRAP-NRB-WESTLANDS-04")
    
    sample_data = TrapMetrics(
        trap_id="TRAP-NRB-WESTLANDS-04",
        water_temp_c=48.2,
        ambient_temp_c=24.5,
        oil_layer_depth_mm=42.0,
        sludge_depth_mm=30.0,
        flow_rate_lpm=18.5,
        ph_level=7.2
    )
    
    result = sentinel.evaluate_telemetry(sample_data)
    print("Evaluation Result:", result)
    print("Grease Trap Sentinel Operational Successfully.")
