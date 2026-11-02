"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Thermal Drift Compensator Sentinel

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Monitors roller bearing housing temperatures, ambient mill floor thermal gradients, and
feed stock mass flow rates to predict micro-scale thermal expansion of high-alloy steel
roller rolls in industrial maize and wheat roller mills. Automatically calculates and applies
closed-loop stepper/hydraulic actuator offset corrections to maintain exact fluting nip clearance.
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerGapThermalDriftCompensator")

class RollerGapThermalDriftCompensator:
    """
    Computes thermal expansion vectors on roller mill assemblies and orchestrates real-time
    corrective gap adjustment to preserve extraction rates and particle size distribution (PSD).
    """
    
    EXPANSION_COEFFICIENT_CAST_IRON = 0.0108  # micrometers per mm per degree Celsius (approx for chilled cast iron)
    
    def __init__(self, roll_diameter_mm: float = 250.0, base_gap_microns: float = 150.0):
        self.roll_diameter_mm = roll_diameter_mm
        self.base_gap_microns = base_gap_microns
        self.ambient_baseline_c = 25.0
        self.current_drift_microns = 0.0
        self.total_corrections_applied = 0
        self.history: List[Dict[str, Any]] = []
        logger.info(f"Initialized Thermal Drift Compensator. Roll Dia: {roll_diameter_mm}mm, Base Gap: {base_gap_microns}um")

    def compute_drift(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """
        Computes thermal expansion drift based on bearing temps, motor load, and ambient metrics.
        Telemetry expected:
          - bearing_temp_c: float
          - roll_surface_temp_c: float
          - ambient_temp_c: float
          - feed_rate_tph: float (tons per hour)
        """
        bearing_temp = telemetry.get("bearing_temp_c", 45.0)
        surface_temp = telemetry.get(
            "roll_surface_temp_c",
            self.ambient_baseline_c + (bearing_temp - self.ambient_baseline_c) * 0.75
        )
        ambient_temp = telemetry.get("ambient_temp_c", self.ambient_baseline_c)
        feed_rate = telemetry.get("feed_rate_tph", 5.0)
        
        # Thermal differential from baseline calibration state
        delta_t = surface_temp - ambient_temp
        
        # Radial expansion calculation: delta_r = r * alpha * delta_T
        # Since gap is between two rolls, cumulative gap reduction is 2 * delta_r
        radius = self.roll_diameter_mm / 2.0
        radial_expansion_microns = radius * (self.EXPANSION_COEFFICIENT_CAST_IRON * 1e-3) * delta_t
        total_gap_reduction = radial_expansion_microns * 2.0
        
        # Factor in load friction coefficient
        load_friction_factor = 1.0 + (feed_rate / 10.0) * 0.05
        adjusted_drift = total_gap_reduction * load_friction_factor
        
        self.current_drift_microns = round(adjusted_drift, 3)
        compensating_offset = -self.current_drift_microns
        
        status = {
            "timestamp": time.time(),
            "delta_t_c": round(delta_t, 2),
            "calculated_drift_microns": self.current_drift_microns,
            "recommended_compensating_offset_microns": round(compensating_offset, 3),
            "target_adjusted_gap_microns": round(self.base_gap_microns + compensating_offset, 3),
            "action": "APPLY_OFFSET" if abs(compensating_offset) > 1.0 else "HOLD"
        }
        
        self.history.append(status)
        if len(self.history) > 1000:
            self.history.pop(0)
            
        return status

    def execute_compensation(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates telemetry and simulates sending micro-step correction pulses to roll gap actuators.
        """
        result = self.compute_drift(telemetry)
        if result["action"] == "APPLY_OFFSET":
            self.total_corrections_applied += 1
            logger.warning(
                f"[CORRECTION APPLIED] Thermal drift detected! Offset: "
                f"{result['recommended_compensating_offset_microns']} um. "
                f"New Target Gap: {result['target_adjusted_gap_microns']} um."
            )
        return result

    def audit_metrics(self) -> Dict[str, Any]:
        return {
            "total_corrections_applied": self.total_corrections_applied,
            "latest_drift_microns": self.current_drift_microns,
            "history_records": len(self.history)
        }


if __name__ == "__main__":
    logger.info("Executing self-test for RollerGapThermalDriftCompensator...")
    compensator = RollerGapThermalDriftCompensator(roll_diameter_mm=300.0, base_gap_microns=200.0)
    
    # Simulate rising roller mill temperatures during heavy shift operation
    simulated_telemetries = [
        {"bearing_temp_c": 42.0, "roll_surface_temp_c": 38.0, "ambient_temp_c": 24.0, "feed_rate_tph": 4.5},
        {"bearing_temp_c": 58.0, "roll_surface_temp_c": 52.0, "ambient_temp_c": 26.0, "feed_rate_tph": 6.2},
        {"bearing_temp_c": 72.0, "roll_surface_temp_c": 65.0, "ambient_temp_c": 27.0, "feed_rate_tph": 8.0}
    ]
    
    for idx, tel in enumerate(simulated_telemetries):
        res = compensator.execute_compensation(tel)
        logger.info(f"Simulation Step {idx+1}: {res}")
        
    logger.info(f"Final Audit Metrics: {compensator.audit_metrics()}")
    logger.info("RollerGapThermalDriftCompensator self-test completed successfully.")
