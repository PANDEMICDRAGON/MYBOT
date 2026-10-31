"""
Nairobi Commercial Grain Milling Roller Mill Choke Feed Sentinel
Autonomous Evolutionary Architecture - Cycle #385

Monitors differential pressure, feeder motor current draw, and product level
in roller mill feed hoppers. Automatically triggers anti-choke pneumatic pulses
and regulates feed gate servo positions to maintain optimal uniform product curtain.
"""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillChokeFeedSentinel")

class RollerMillChokeFeedSentinel:
    def __init__(self, mill_id: str, max_current_amps: float = 45.0, warning_threshold_pct: float = 85.0):
        self.mill_id = mill_id
        self.max_current_amps = max_current_amps
        self.warning_threshold_pct = warning_threshold_pct
        self.choke_events_prevented = 0
        self.active_choke_state = False
        logger.info(f"[INIT] RollerMillChokeFeedSentinel initialized for mill {self.mill_id}.")

    def evaluate_sensor_telemetry(self, current_draw: float, feed_gate_opening_pct: float, hopper_dp_kpa: float) -> Dict[str, Any]:
        """
        Evaluates real-time roller mill telemetry to detect choke conditions.
        """
        load_pct = (current_draw / self.max_current_amps) * 100.0
        action_taken = "NORMAL"
        vibrator_pulse = False
        gate_adjustment_pct = 0.0

        # Check for choke risk
        if load_pct >= self.warning_threshold_pct or hopper_dp_kpa > 2.5:
            self.active_choke_state = True
            self.choke_events_prevented += 1
            vibrator_pulse = True
            gate_adjustment_pct = -10.0  # Reduce feed opening by 10%
            action_taken = "ANTI_CHOKE_INTERVENTION_ACTIVATED"
            logger.warning(f"[CHOKE ALERT] Mill {self.mill_id} load at {load_pct:.1f}%, DP {hopper_dp_kpa} kPa. Pulsing vibrator & closing gate.")
        else:
            self.active_choke_state = False
            action_taken = "NOMINAL_OPERATION"

        return {
            "mill_id": self.mill_id,
            "load_percentage": round(load_pct, 2),
            "hopper_dp_kpa": hopper_dp_kpa,
            "feed_gate_opening_pct": feed_gate_opening_pct,
            "action_taken": action_taken,
            "vibrator_pulse_triggered": vibrator_pulse,
            "recommended_gate_adjustment": gate_adjustment_pct,
            "total_choke_interventions": self.choke_events_prevented,
            "timestamp": time.time()
        }

if __name__ == "__main__":
    sentinel = RollerMillChokeFeedSentinel(mill_id="RM-NAIROBI-04")
    # Test normal condition
    res_normal = sentinel.evaluate_sensor_telemetry(current_draw=32.0, feed_gate_opening_pct=75.0, hopper_dp_kpa=1.1)
    print("Normal Telemetry Test:", res_normal)
    
    # Test impending choke condition
    res_choke = sentinel.evaluate_sensor_telemetry(current_draw=43.5, feed_gate_opening_pct=85.0, hopper_dp_kpa=2.8)
    print("Choke Risk Telemetry Test:", res_choke)
