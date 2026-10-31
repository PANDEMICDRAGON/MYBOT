"""
Nairobi Commercial Grain Milling Roller Mill Roller Corrugation Wear Sentinel
Autonomous Evolutionary Module for Cortana Autonomous Evolutionary Architect

Monitors roller mill flute/corrugation wear patterns, calculates sharpness index,
and predicts optimal maintenance and re-fluting windows for maize and wheat milling.
"""

import json
import logging
import math
import time
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerCorrugationWearSentinel")

class RollerCorrugationWearSentinel:
    """
    Tracks roller mill corrugation degradation, shear angle deviations, and thermal spikes
    to prevent flour quality drop and excessive power consumption in Nairobi mills.
    """
    def __init__(self, mill_id: str, roll_pair_id: str, initial_flute_angle_deg: float = 45.0):
        self.mill_id = mill_id
        self.roll_pair_id = roll_pair_id
        self.initial_flute_angle_deg = initial_flute_angle_deg
        self.accumulated_tonnage = 0.0
        self.wear_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerCorrugationWearSentinel for Mill: {mill_id}, RollPair: {roll_pair_id}")

    def assess_wear(self, operating_hours: float, tonnage_processed: float, current_shear_angle_deg: float,
                    harmonic_vibration_amplitude_g: float, motor_current_draw_amps: float) -> Dict[str, Any]:
        """
        Evaluates current roller wear based on shear angle degradation, vibration harmonics,
        and motor load trends.
        """
        self.accumulated_tonnage = tonnage_processed
        angle_deviation = abs(self.initial_flute_angle_deg - current_shear_angle_deg)
        
        # Sharpness index calculation (100% = brand new, 0% = totally blunt)
        sharpness_index = max(0.0, 100.0 - (angle_deviation * 3.5) - (harmonic_vibration_amplitude_g * 15.0))
        
        # Status determination
        if sharpness_index > 80.0:
            status = "OPTIMAL"
            action = "Continue standard operation."
        elif sharpness_index > 50.0:
            status = "MODERATE_WEAR"
            action = "Schedule re-fluting within the next 200 operational hours."
        elif sharpness_index > 25.0:
            status = "HIGH_WEAR"
            action = "Plan immediate re-fluting during next scheduled maintenance window."
        else:
            status = "CRITICAL_BLUNTNESS"
            action = "EMERGENCY STOP: Risk of excessive bran shearing and high temperature rise."

        assessment = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "roll_pair_id": self.roll_pair_id,
            "operating_hours": operating_hours,
            "tonnage_processed": tonnage_processed,
            "current_shear_angle_deg": current_shear_angle_deg,
            "angle_deviation": angle_deviation,
            "harmonic_vibration_amplitude_g": harmonic_vibration_amplitude_g,
            "motor_current_draw_amps": motor_current_draw_amps,
            "sharpness_index": round(sharpness_index, 2),
            "status": status,
            "recommended_action": action
        }

        self.wear_history.append(assessment)
        if len(self.wear_history) > 1000:
            self.wear_history.pop(0)

        logger.info(f"Assessed {self.roll_pair_id}: Sharpness={sharpness_index:.1f}%, Status={status}")
        return assessment

    def export_telemetry(self) -> str:
        """Exports recent telemetry and wear metrics as JSON."""
        return json.dumps({
            "mill_id": self.mill_id,
            "roll_pair_id": self.roll_pair_id,
            "accumulated_tonnage": self.accumulated_tonnage,
            "latest_assessment": self.wear_history[-1] if self.wear_history else None
        }, indent=2)

if __name__ == "__main__":
    print("Executing RollerCorrugationWearSentinel Test Harness...")
    sentinel = RollerCorrugationWearSentinel(mill_id="NAIROBI_MILL_01", roll_pair_id="B1_FAST_SLOW_PAIR")
    result = sentinel.assess_wear(
        operating_hours=450.5,
        tonnage_processed=1250.8,
        current_shear_angle_deg=41.2,
        harmonic_vibration_amplitude_g=0.85,
        motor_current_draw_amps=48.2
    )
    print(json.dumps(result, indent=2))
    print("Test harness executed successfully.")
