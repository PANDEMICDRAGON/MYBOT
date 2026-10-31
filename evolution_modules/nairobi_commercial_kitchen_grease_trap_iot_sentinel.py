"""
Nairobi Commercial Kitchen Grease Trap IoT Sentinel
Monitors FOG (Fats, Oils, Grease) accumulation, temperature, and pH levels
for commercial kitchens in Nairobi, preventing municipal plumbing blockages.
"""

import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GreaseTrapSentinel")

class GreaseTrapSentinel:
    """
    Monitors commercial grease trap telemetry to predict clean-out cycles and prevent overflows.
    """
    def __init__(self, trap_id: str, capacity_liters: float = 200.0):
        self.trap_id = trap_id
        self.capacity_liters = capacity_liters
        self.telemetry_history: List[Dict[str, Any]] = []

    def evaluate_telemetry(self, oil_layer_cm: float, water_temp_c: float, ph_level: float) -> Dict[str, Any]:
        """
        Evaluates real-time sensor inputs and computes risk indices.
        """
        max_depth_cm = 50.0  # standard commercial trap depth
        fill_percentage = min(100.0, (oil_layer_cm / max_depth_cm) * 100.0)
        
        status = "OPTIMAL"
        action_required = False
        alert_message = "Grease trap operating within safe parameters."

        if fill_percentage >= 80.0:
            status = "CRITICAL_OVERFLOW_RISK"
            action_required = True
            alert_message = "URGENT: Grease trap capacity near maximum. Dispatch exhaust/pumping service immediately!"
        elif fill_percentage >= 60.0:
            status = "WARNING_ELEVATED"
            action_required = True
            alert_message = "NOTICE: FOG layer elevated. Schedule maintenance within 48 hours."

        if water_temp_c > 55.0:
            status = "THERMAL_WARNING"
            action_required = True
            alert_message += " Warning: High water temperature liquefying trapped grease."

        if not (6.0 <= ph_level <= 8.5):
            status = "CHEMICAL_ANOMALY"
            action_required = True
            alert_message += f" Warning: Abnormal pH level ({ph_level}) detected, potential chemical corrosion."

        record = {
            "timestamp": time.time(),
            "trap_id": self.trap_id,
            "oil_layer_cm": oil_layer_cm,
            "fill_percentage": round(fill_percentage, 2),
            "water_temp_c": water_temp_c,
            "ph_level": ph_level,
            "status": status,
            "action_required": action_required,
            "alert_message": alert_message
        }
        
        self.telemetry_history.append(record)
        return record

if __name__ == "__main__":
    sentinel = GreaseTrapSentinel(trap_id="TRAP_WESTLANDS_01", capacity_liters=250.0)
    sample_reading = sentinel.evaluate_telemetry(oil_layer_cm=42.5, water_temp_c=48.0, ph_level=7.2)
    logger.info(f"Grease Trap Sentinel Status: {sample_reading}")
