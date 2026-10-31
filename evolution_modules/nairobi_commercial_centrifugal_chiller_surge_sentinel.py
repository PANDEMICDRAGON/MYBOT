"""Nairobi Commercial Centrifugal Chiller Surge & Refrigerant Compression Sentinel

Protects large-scale centrifugal chillers in Nairobi commercial installations against
aerodynamic surge, refrigerant pressure spikes, lubrication anomalies, and electrical stress.
"""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CentrifugalChillerSurgeSentinel")


class CentrifugalChillerSurgeSentinel:
    """Monitors centrifugal chiller telemetry and prevents refrigerant surge and thermal overload."""

    def __init__(self, chiller_id: str, refrigerant_type: str = "R-134a") -> None:
        self.chiller_id = chiller_id
        self.refrigerant_type = refrigerant_type
        self.is_running = False
        self.surge_incident_count = 0
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"[+] CentrifugalChillerSurgeSentinel initialized for {self.chiller_id} ({self.refrigerant_type}).")

    def evaluate_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes operating pressures, temperatures, and compressor metrics."""
        suction_pressure_kpa = telemetry.get("suction_pressure_kpa", 350.0)
        discharge_pressure_kpa = telemetry.get("discharge_pressure_kpa", 1200.0)
        oil_pressure_diff_kpa = telemetry.get("oil_pressure_diff_kpa", 150.0)
        guide_vane_position_pct = telemetry.get("guide_vane_position_pct", 50.0)
        motor_temp_c = telemetry.get("motor_temp_c", 65.0)
        vibration_mm_s = telemetry.get("vibration_mm_s", 1.2)

        # Pressure ratio calculation for surge proximity
        # High pressure ratio combined with low guide vane position indicates surge risk
        pressure_ratio = discharge_pressure_kpa / max(suction_pressure_kpa, 1.0)
        
        surge_risk = False
        action_taken = "NORMAL"

        # Surge condition heuristic: high pressure ratio and low flow/vane opening
        if pressure_ratio > 3.8 and guide_vane_position_pct < 25.0:
            surge_risk = True
            self.surge_incident_count += 1
            action_taken = "MODULATE_GUIDE_VANES_OPEN"
        elif vibration_mm_s > 4.5:
            surge_risk = True
            action_taken = "EMERGENCY_CAPACITY_REDUCTION"
        elif oil_pressure_diff_kpa < 90.0:
            surge_risk = True
            action_taken = "SHUTDOWN_LOW_OIL_PRESSURE"
        elif motor_temp_c > 95.0:
            surge_risk = True
            action_taken = "SHUTDOWN_MOTOR_OVERHEAT"

        evaluation = {
            "chiller_id": self.chiller_id,
            "timestamp": time.time(),
            "pressure_ratio": round(pressure_ratio, 2),
            "surge_risk": surge_risk,
            "action_taken": action_taken,
            "surge_incident_count": self.surge_incident_count
        }

        self.telemetry_history.append(evaluation);
        if len(self.telemetry_history) > 100:
            self.telemetry_history.pop(0)

        return evaluation

    def get_status_summary(self) -> Dict[str, Any]:
        """Returns historical operational metrics and health status."""
        return {
            "chiller_id": self.chiller_id,
            "is_running": self.is_running,
            "total_surge_incidents": self.surge_incident_count,
            "last_telemetry": self.telemetry_history[-1] if self.telemetry_history else None
        }


if __name__ == "__main__":
    sentinel = CentrifugalChillerSurgeSentinel(chiller_id="NBI-CC-01", refrigerant_type="R-134a")
    sentinel.is_running = True
    
    # Test normal condition
    normal_telemetry = {
        "suction_pressure_kpa": 400.0,
        "discharge_pressure_kpa": 1100.0,
        "oil_pressure_diff_kpa": 160.0,
        "guide_vane_position_pct": 65.0,
        "motor_temp_c": 60.0,
        "vibration_mm_s": 1.0
    }
    print("Normal Evaluation:", sentinel.evaluate_telemetry(normal_telemetry))

    # Test surge-risk condition (high pressure ratio + low vane position)
    surge_telemetry = {
        "suction_pressure_kpa": 280.0,
        "discharge_pressure_kpa": 1350.0,
        "oil_pressure_diff_kpa": 150.0,
        "guide_vane_position_pct": 18.0,
        "motor_temp_c": 70.0,
        "vibration_mm_s": 2.1
    }
    print("Surge Risk Evaluation:", sentinel.evaluate_telemetry(surge_telemetry))
    print("Summary Status:", sentinel.get_status_summary())
