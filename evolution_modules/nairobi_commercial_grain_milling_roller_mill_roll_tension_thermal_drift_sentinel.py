"""
Nairobi Commercial Grain Milling Roller Mill Roll Tension Thermal Drift Sentinel
Autonomous Evolutionary Architecture Module #13
Designed for Michael Obiero in Nairobi, Kenya
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillThermalDriftSentinel")

class RollerMillThermalDriftSentinel:
    """
    Monitors thermal expansion of commercial grain milling rolls and dynamically
    compensates roll gap tensioning parameters to maintain precise flour extraction granularity.
    """
    def __init__(self, mill_id: str, thermal_expansion_coefficient: float = 0.000011):
        self.mill_id = mill_id
        self.alpha = thermal_expansion_coefficient
        self.baseline_temp_c: float = 25.0
        self.current_temp_c: float = 25.0
        self.roll_diameter_mm: float = 250.0
        self.nominal_gap_microns: float = 150.0
        self.current_tension_bar: float = 45.0
        self.drift_history: List[Dict[str, Any]] = []

    def update_telemetry(self, temp_c: float, current_gap_microns: float, tension_bar: float) -> Dict[str, Any]:
        self.current_temp_c = temp_c
        self.nominal_gap_microns = current_gap_microns
        self.current_tension_bar = tension_bar
        
        delta_t = self.current_temp_c - self.baseline_temp_c
        # Thermal expansion formula: delta_d = d * alpha * delta_t
        expansion_microns = self.roll_diameter_mm * 1000.0 * self.alpha * delta_t
        
        # Compensation required
        compensated_adjustment = -expansion_microns
        
        status = "OPTIMAL"
        if abs(expansion_microns) > 15.0:
            status = "THERMAL_DRIFT_WARNING"
        if abs(expansion_microns) > 30.0:
            status = "CRITICAL_THERMAL_EXPANSION"

        record = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "temp_c": self.current_temp_c,
            "delta_t": delta_t,
            "expansion_microns": round(expansion_microns, 3),
            "recommended_gap_adjustment_microns": round(compensated_adjustment, 3),
            "status": status
        }
        
        self.drift_history.append(record)
        if len(self.drift_history) > 100:
            self.drift_history.pop(0)
            
        return record

    def get_audit_summary(self) -> Dict[str, Any]:
        if not self.drift_history:
            return {"status": "NO_DATA"}
        latest = self.drift_history[-1]
        return {
            "mill_id": self.mill_id,
            "latest_record": latest,
            "total_samples": len(self.drift_history),
            "sentinel_status": "ACTIVE"
        }

if __name__ == "__main__":
    sentinel = RollerMillThermalDriftSentinel(mill_id="NAIROBI_MILL_EASTLANDS_04")
    # Simulate thermal rise during heavy maize milling operation
    for t in [25.0, 32.5, 40.0, 48.2, 55.0]:
        res = sentinel.update_telemetry(temp_c=t, current_gap_microns=150.0, tension_bar=48.5)
        logger.info(f"Telemetry processed: {res}")
    print(sentinel.get_audit_summary())
