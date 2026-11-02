"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Thermo Elastic Deviation Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerGapThermoElasticSentinel")

class RollerGapThermoElasticSentinel:
    """
    Monitors roller mill bearing and shell temperatures, calculating real-time thermo-elastic
    expansion of cast-iron/alloy rolls and issuing micro-actuator gap adjustments.
    """
    def __init__(self, mill_id: str, nominal_gap_microns: float = 250.0, thermal_expansion_coeff: float = 11.0e-6):
        self.mill_id = mill_id
        self.nominal_gap_microns = nominal_gap_microns
        self.thermal_expansion_coeff = thermal_expansion_coeff  # per deg C for alloy steel/cast iron
        self.roll_diameter_mm = 250.0
        self.ambient_reference_temp_c = 25.0
        self.current_gap_microns = nominal_gap_microns
        self.adjustment_history: List[Dict[str, Any]] = []

    def compute_gap_compensation(self, drive_bearing_temp_c: float, non_drive_bearing_temp_c: float, shell_temp_c: float) -> Dict[str, Any]:
        """
        Computes thermal expansion deviation and required micrometer correction.
        """
        avg_temp = (drive_bearing_temp_c + non_drive_bearing_temp_c + (shell_temp_c * 2.0)) / 4.0
        temp_delta = avg_temp - self.ambient_reference_temp_c
        
        # Thermal expansion formula: delta_d = diameter * alpha * temp_delta
        # Expressed in microns (1 mm = 1000 microns)
        expansion_microns = self.roll_diameter_mm * 1000.0 * self.thermal_expansion_coeff * temp_delta
        
        # Compensatory movement is negative expansion to maintain constant gap
        required_correction_microns = -expansion_microns
        self.current_gap_microns = self.nominal_gap_microns + required_correction_microns

        status = "OPTIMAL"
        if abs(expansion_microns) > 50.0:
            status = "HIGH_THERMAL_DEVIATION_WARNING"
        if abs(expansion_microns) > 90.0:
            status = "CRITICAL_NIP_RISK_SHUTDOWN"

        telemetry = {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "average_roll_temp_c": round(avg_temp, 2),
            "temp_delta_c": round(temp_delta, 2),
            "expansion_microns": round(expansion_microns, 2),
            "adjusted_gap_microns": round(self.current_gap_microns, 2),
            "status": status
        }

        self.adjustment_history.append(telemetry)
        if len(self.adjustment_history) > 100:
            self.adjustment_history.pop(0)

        return telemetry

if __name__ == "__main__":
    logger.info("Initializing Roller Gap Thermo Elastic Deviation Sentinel test harness...")
    sentinel = RollerGapThermoElasticSentinel(mill_id="NAIROBI_MILL_B4_MAIZE")
    
    # Simulate warming up over a milling shift
    test_temps = [
        (26.0, 26.5, 27.0),
        (35.0, 36.2, 38.0),
        (48.0, 49.5, 52.0),
        (65.0, 67.0, 71.0)
    ]
    
    for drive, non_drive, shell in test_temps:
        result = sentinel.compute_gap_compensation(drive, non_drive, shell)
        logger.info(f"Telemetry Result: {result}")
    
    logger.info("Roller Gap Thermo Elastic Deviation Sentinel verification complete.")
