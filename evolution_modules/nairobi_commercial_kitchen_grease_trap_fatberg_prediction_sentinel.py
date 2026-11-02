"""
Nairobi Commercial Kitchen Grease Trap Fatberg Prediction Sentinel
Autonomous Evolutionary Module for Cortana's Operational Infrastructure
Designed for Michael Obiero in Nairobi, Kenya
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("GreaseTrapFatbergSentinel")


class GreaseTrapFatbergSentinel:
    """
    Monitors commercial grease trap sensors (pH, temperature gradient, volumetric FOG layer thickness, 
    and drainage backpressure) to predict and prevent fatberg formation in Nairobi municipal drainage systems.
    """

    def __init__(self, trap_id: str, capacity_liters: float = 250.0):
        self.trap_id = trap_id
        self.capacity_liters = capacity_liters
        self.fog_layer_thickness_cm: float = 2.5
        self.temperature_inlet_c: float = 48.5
        self.temperature_outlet_c: float = 24.0
        self.ph_level: float = 6.2
        self.backpressure_kpa: float = 1.2
        self.enzyme_activity_score: float = 0.85
        logger.info(f"GreaseTrapFatbergSentinel initialized for trap {trap_id} ({capacity_liters}L capacity).")

    def ingest_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingests live sensor readings from the grease trap IoT array.
        """
        self.fog_layer_thickness_cm = telemetry.get("fog_thickness_cm", self.fog_layer_thickness_cm)
        self.temperature_inlet_c = telemetry.get("temp_inlet", self.temperature_inlet_c)
        self.temperature_outlet_c = telemetry.get(
            "temp_outlet", self.temperature_outlet_c
        )
        self.ph_level = telemetry.get("ph", self.ph_level)
        self.backpressure_kpa = telemetry.get("backpressure_kpa", self.backpressure_kpa)
        self.enzyme_activity_score = telemetry.get("enzyme_score", self.enzyme_activity_score)

        risk_index = self._calculate_fatberg_risk_index()
        action = self._determine_remediation_action(risk_index)

        return {
            "trap_id": self.trap_id,
            "risk_index": round(risk_index, 4),
            "status": action["status"],
            "recommended_protocol": action["protocol"],
            "timestamp": time.time()
        }

    def _calculate_fatberg_risk_index(self) -> float:
        """
        Calculates non-linear fatberg formation risk based on FOG accumulation thickness,
        temperature differentials, microbial enzyme decay, and backpressure surges.
        """
        thickness_factor = min(self.fog_layer_thickness_cm / 15.0, 1.0)
        temp_diff = abs(self.temperature_inlet_c - self.temperature_outlet_c)
        cooling_efficiency_penalty = max(0.0, (30.0 - temp_diff) / 30.0)
        pressure_factor = min(self.backpressure_kpa / 10.0, 1.0)
        enzyme_penalty = max(0.0, 1.0 - self.enzyme_activity_score)

        risk = (
            (thickness_factor * 0.40) +
            (cooling_efficiency_penalty * 0.25) +
            (pressure_factor * 0.20) +
            (enzyme_penalty * 0.15)
        )
        return float(max(0.0, min(risk, 1.0)))

    def _determine_remediation_action(self, risk_index: float) -> Dict[str, str]:
        """
        Determines autonomous flushing, enzymatic dosing, or emergency pump-out commands.
        """
        if risk_index >= 0.80:
            return {
                "status": "CRITICAL_FATBERG_IMMINENT",
                "protocol": "EMERGENCY_HOT_WATER_FLUSH_AND_VACUUM_DISPATCH"
            }
        elif risk_index >= 0.50:
            return {
                "status": "ELEVATED_RISK",
                "protocol": "BIOLOGICAL_ENZYME_BOOST_AND_CYCLE_FLUSH"
            }
        elif risk_index >= 0.25:
            return {
                "status": "MONITORING",
                "protocol": "STANDARD_MAINTENANCE_SCHEDULE"
            }
        else:
            return {
                "status": "OPTIMAL",
                "protocol": "NO_ACTION_REQUIRED"
            }


if __name__ == "__main__":
    print("Executing self-test for GreaseTrapFatbergSentinel...")
    sentinel = GreaseTrapFatbergSentinel(trap_id="TRAP-NRB-WESTLANDS-04")
    
    # Simulate high FOG accumulation telemetry
    sample_telemetry = {
        "fog_thickness_cm": 11.2,
        "temp_inlet": 52.0,
        "temp_outlet": 22.0,
        "ph": 5.8,
        "backpressure_kpa": 6.5,
        "enzyme_score": 0.42
    }
    
    result = sentinel.ingest_telemetry(sample_telemetry)
    print(f"Test telemetry ingestion result: {result}")
    assert result["risk_index"] > 0.5, "Risk calculation failed threshold check."
    print("GreaseTrapFatbergSentinel test passed successfully.")
