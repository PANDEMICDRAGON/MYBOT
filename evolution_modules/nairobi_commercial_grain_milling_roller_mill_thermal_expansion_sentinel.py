"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Thermal Expansion Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import logging
import math
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillThermalSentinel")

class RollerMillThermalSentinel:
    """
    Monitors roller mill bearing and shell temperatures, calculates dynamic thermal
    expansion coefficients, and provides real-time roll gap adjustments to maintain
    consistent flour reduction standards.
    """
    def __init__(self, mill_id: str, roll_material: str = "cast_chilled_iron", base_gap_microns: float = 250.0):
        self.mill_id = mill_id
        self.roll_material = roll_material
        self.base_gap_microns = base_gap_microns
        # Thermal expansion coefficient for chilled cast iron (~10.5 x 10^-6 / °C)
        self.alpha = 10.5e-6 
        self.ambient_reference_temp_c = 25.0
        self.current_drive_temp_c = 25.0
        self.current_operator_temp_c = 25.0
        self.history: List[Dict[str, Any]] = []

    def update_telemetry(self, drive_side_temp: float, operator_side_temp: float, ambient_temp: float = 25.0) -> Dict[str, Any]:
        """
        Ingests real-time telemetry from roller mill sensors and calculates required gap adjustment.
        """
        self.current_drive_temp_c = drive_side_temp
        self.current_operator_temp_c = operator_side_temp
        self.ambient_reference_temp_c = ambient_temp

        # Calculate mean shell temperature rise
        mean_temp_drive = drive_side_temp - self.ambient_reference_temp_c
        mean_temp_operator = operator_side_temp - self.ambient_reference_temp_c

        # Assume standard roll diameter of 250mm (250,000 microns)
        roll_diameter_microns = 250000.0
        
        # Thermal growth delta = alpha * diameter * delta_T
        growth_drive_microns = self.alpha * roll_diameter_microns * mean_temp_drive
        growth_operator_microns = self.alpha * roll_diameter_microns * mean_temp_operator

        # Compensation required: If rolls expand inward, gap closes. We need to back off gap.
        adjusted_gap = self.base_gap_microns - ((growth_drive_microns + growth_operator_microns) / 2.0)
        
        status = "OPTIMAL"
        if abs(mean_temp_drive - mean_temp_operator) > 8.0:
            status = "ASYMMETRIC_THERMAL_SKEW_WARNING"
        elif mean_temp_drive > 65.0 or mean_temp_operator > 65.0:
            status = "CRITICAL_OVERHEAT_THERMAL_EXPANSION"

        telemetry_record = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "drive_temp": drive_side_temp,
            "operator_temp": operator_side_temp,
            "growth_drive_microns": round(growth_drive_microns, 2),
            "growth_operator_microns": round(growth_operator_microns, 2),
            "calculated_gap_microns": round(max(50.0, adjusted_gap), 2),
            "status": status
        }

        self.history.append(telemetry_record)
        if len(self.history) > 1000:
            self.history.pop(0)

        return telemetry_record

    def generate_diagnostic_report(self) -> Dict[str, Any]:
        """Generates summary analytics of thermal expansion behavior."""
        if not self.history:
            return {"status": "NO_DATA"}

        latest = self.history[-1]
        avg_drive = sum(h["drive_temp"] for h in self.history) / len(self.history)
        
        return {
            "mill_id": self.mill_id,
            "total_samples": len(self.history),
            "latest_status": latest["status"],
            "latest_adjusted_gap_microns": latest["calculated_gap_microns"],
            "lifetime_mean_drive_temp_c": round(avg_drive, 2)
        }

if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Thermal Expansion Sentinel Test Harness...")
    sentinel = RollerMillThermalSentinel(mill_id="MILL_NAIROBI_INDUSTRIAL_04")
    
    # Simulate temperature rise over continuous production shift
    simulated_readings = [
        (28.0, 27.5, 24.0),
        (35.2, 34.8, 24.5),
        (48.5, 47.1, 25.0),
        (62.0, 52.0, 25.5),  # Notice asymmetric thermal skew
        (66.5, 65.8, 26.0)   # High operating temperature
    ]

    for idx, (drv, op, amb) in enumerate(simulated_readings):
        result = sentinel.update_telemetry(drv, op, amb)
        logger.info(f"Cycle {idx+1}: {result}")

    report = sentinel.generate_diagnostic_report()
    logger.info(f"Diagnostic Summary Report: {report}")
    logger.info("Roller Mill Dynamic Thermal Expansion Sentinel operational check completed successfully.")
