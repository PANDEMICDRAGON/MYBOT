"""
Module: nairobi_commercial_grain_milling_roller_mill_roll_thermal_expansion_sentinel_v29.py
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
Description: Monitors roller mill roll temperatures, calculates differential thermal expansion coefficients,
             predicts nip gap variations, and triggers automated cooling adjustments to prevent uneven flour granulation.
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ThermalExpansionSentinel")

class RollerThermalSentinel:
    """
    Real-time thermal expansion and gap variance sentinel for commercial roller mills.
    """
    def __init__(self, mill_id: str, nominal_diameter_mm: float = 250.0, thermal_expansion_coefficient: float = 0.000011):
        self.mill_id = mill_id
        self.nominal_diameter_mm = nominal_diameter_mm
        self.alpha = thermal_expansion_coefficient  # Cast iron / alloy steel thermal expansion
        self.baseline_temp_c = 25.0
        self.history: List[Dict[str, Any]] = []

    def calculate_expansion(self, current_temp_c: float) -> float:
        """
        Calculates radial expansion (delta r) based on temperature delta from baseline.
        """
        delta_t = current_temp_c - self.baseline_temp_c
        radius = self.nominal_diameter_mm / 2.0
        delta_r = radius * self.alpha * delta_t
        return delta_r

    def evaluate_roll_status(self, fast_roll_temp_c: float, slow_roll_temp_c: float) -> Dict[str, Any]:
        """
        Evaluates thermal state of both fast and slow rolls, projecting nip gap error.
        """
        fast_expansion = self.calculate_expansion(fast_roll_temp_c)
        slow_expansion = self.calculate_expansion(slow_roll_temp_c)
        
        # Differential expansion between fast and slow rolls alters effective nip gap
        nip_variance_microns = (fast_expansion - slow_expansion) * 1000.0
        
        status = "OPTIMAL"
        cooling_action = "NONE"

        if abs(nip_variance_microns) > 45.0 or max(fast_roll_temp_c, slow_roll_temp_c) > 75.0:
            status = "CRITICAL_THERMAL_DRIFT"
            cooling_action = "MAX_CHILLER_WATER_FLOW"
        elif abs(nip_variance_microns) > 25.0 or max(fast_roll_temp_c, slow_roll_temp_c) > 60.0:
            status = "WARNING_ELEVATED_TEMP"
            cooling_action = "MODERATE_CHILLER_WATER_FLOW"

        telemetry = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "fast_roll_temp_c": fast_roll_temp_c,
            "slow_roll_temp_c": slow_roll_temp_c,
            "fast_expansion_mm": round(fast_expansion, 4),
            "slow_expansion_mm": round(slow_expansion, 4),
            "nip_variance_microns": round(nip_variance_microns, 2),
            "status": status,
            "cooling_action": cooling_action
        }
        
        self.history.append(telemetry)
        if len(self.history) > 1000:
            self.history.pop(0)
            
        return telemetry

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Thermal Expansion Sentinel v29...")
    sentinel = RollerThermalSentinel(mill_id="NAIROBI_MILL_LINE_04")
    
    # Test simulation run under heavy load heating up rolls
    test_readings = [
        (28.5, 27.8),
        (45.0, 42.1),
        (62.4, 58.0),
        (78.1, 71.5)
    ]

    for fast_t, slow_t in test_readings:
        result = sentinel.evaluate_roll_status(fast_t, slow_t)
        print(f"Telemetry Evaluated: {result}")

    print("Sentinel verification complete. System armed.")
