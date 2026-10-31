"""Nairobi Commercial Grain Milling Damper Tempering Valve Sentinel. Real-time control and diagnostic module for grain moisture conditioning valves."""

import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("DamperTemperingSentinel")

class DamperTemperingSentinel:
    """Monitors and optimizes grain damper tempering valves in commercial milling plants."""

    def __init__(self, target_moisture: float = 14.5, tolerance: float = 0.3) -> None:
        self.target_moisture = target_moisture
        self.tolerance = tolerance
        self.valve_position_pct = 50.0
        self.history: List[Dict[str, Any]] = []

    def evaluate_moisture_feedback(self, current_moisture: float, flow_rate_tph: float) -> Dict[str, Any]:
        """Evaluate incoming grain moisture against target and adjust tempering valve position."""
        error = self.target_moisture - current_moisture
        adjustment = error * 2.5
        self.valve_position_pct = max(0.0, min(100.0, self.valve_position_pct + adjustment))
        
        status = "OPTIMAL"
        if abs(error) > self.tolerance:
            status = "UNDER_WATERED" if error > 0 else "OVER_WATERED"

        telemetry = {
            "timestamp": time.time(),
            "current_moisture": current_moisture,
            "target_moisture": self.target_moisture,
            "flow_rate_tph": flow_rate_tph,
            "valve_position_pct": round(self.valve_position_pct, 2),
            "status": status
        }
        self.history.append(telemetry)
        logger.info(f"Damper telemetry recorded: {telemetry}")
        return telemetry

    def get_diagnostics(self) -> Dict[str, Any]:
        """Return operational diagnostics of the tempering valve subsystem."""
        return {
            "total_evaluations": len(self.history),
            "current_valve_position": self.valve_position_pct,
            "system_status": "ACTIVE_REGULATION"
        }

if __name__ == "__main__":
    sentinel = DamperTemperingSentinel()
    sample_readings = [(13.8, 12.0), (14.2, 12.5), (14.9, 12.2)]
    for moisture, flow in sample_readings:
        sentinel.evaluate_moisture_feedback(moisture, flow)
    print(sentinel.get_diagnostics())
