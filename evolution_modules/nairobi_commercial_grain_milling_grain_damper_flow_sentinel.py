"""
Nairobi Commercial Grain Milling Grain Damper Water Flow & Conditioning Sentinel

Autonomously monitors water flow rate, incoming grain mass flow, target moisture differential,
and solenoid valve actuation status on commercial grain dampening and tempering units in Nairobi.
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(name)s: %(message)s')
logger = logging.getLogger("GrainDamperFlowSentinel")

class GrainDamperFlowSentinel:
    """
    Monitors water-to-grain ratio calibration, flow meter telemetry, and solenoid valve
    response latency to ensure exact tempering moisture targets for optimal wheat/maize milling.
    """
    def __init__(self, target_moisture_pct: float = 15.5, tolerance_pct: float = 0.3) -> None:
        self.target_moisture_pct = target_moisture_pct
        self.tolerance_pct = tolerance_pct
        self.active_alerts: List[str] = []
        self.telemetry_history: List[Dict[str, Any]] = []

    def evaluate_conditioning_cycle(
        self, 
        grain_mass_flow_tph: float, 
        incoming_moisture_pct: float, 
        water_flow_lph: float,
        solenoid_status: bool
    ) -> Dict[str, Any]:
        """
        Evaluates real-time water addition against incoming grain mass flow and moisture.
        Ideal water addition rate (L/h) = Grain Flow (tph) * 1000 * (Target% - Incoming%) / (100 - Target%)
        """
        timestamp = time.time()
        
        # Prevent division issues
        effective_target = max(self.target_moisture_pct, incoming_moisture_pct + 0.1)
        
        # Calculate theoretical required water flow in Liters per hour (L/h)
        moisture_diff = effective_target - incoming_moisture_pct
        theoretical_water_lph = (grain_mass_flow_tph * 1000.0 * moisture_diff) / (100.0 - effective_target)
        theoretical_water_lph = max(0.0, theoretical_water_lph)

        flow_deviation = abs(water_flow_lph - theoretical_water_lph)
        deviation_pct = (flow_deviation / (theoretical_water_lph + 1e-6)) * 100.0

        status = "OPTIMAL"
        self.active_alerts.clear()

        if not solenoid_status and grain_mass_flow_tph > 0.5:
            status = "CRITICAL_FAILURE"
            self.active_alerts.append("Water solenoid valve closed while grain flow is active.")
        elif deviation_pct > 15.0:
            status = "WARNING_DEVIATION"
            self.active_alerts.append(f"Water flow deviation {deviation_pct:.1f}% exceeds threshold.")

        record = {
            "timestamp": timestamp,
            "grain_mass_flow_tph": grain_mass_flow_tph,
            "incoming_moisture_pct": incoming_moisture_pct,
            "water_flow_lph": water_flow_lph,
            "theoretical_water_lph": round(theoretical_water_lph, 2),
            "deviation_pct": round(deviation_pct, 2),
            "solenoid_status": solenoid_status,
            "status": status,
            "alerts": list(self.active_alerts)
        }

        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        logger.info(f"Damper evaluation: Status={status}, Water={water_flow_lph}L/h (Target: {theoretical_water_lph:.1f}L/h)")
        return record

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "target_moisture_pct": self.target_moisture_pct,
            "tolerance_pct": self.tolerance_pct,
            "total_evaluations": len(self.telemetry_history),
            "active_alerts": self.active_alerts
        }

if __name__ == "__main__":
    sentinel = GrainDamperFlowSentinel(target_moisture_pct=15.0)
    # Test normal operation: 5 tph grain flow, 12% incoming moisture
    # Theoretical water: 5 * 1000 * (15 - 12) / (100 - 15) = 15000 / 85 = 176.47 L/h
    res = sentinel.evaluate_conditioning_cycle(
        grain_mass_flow_tph=5.0,
        incoming_moisture_pct=12.0,
        water_flow_lph=175.0,
        solenoid_status=True
    )
    print("Test Execution Result:", res)
