"""
Nairobi Commercial Grain Milling Roller Mill Hydraulic & Pneumatic Tension Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTensionSentinel")

class RollerMillTensionSentinel:
    """
    Monitors hydraulic and pneumatic tensioning systems on commercial grain roller mills.
    Detects pressure loss, pressure spikes, hydraulic fluid temperature anomalies, and seal degradation.
    """

    def __init__(self, mill_id: str, target_pressure_bar: float = 6.0, tolerance_bar: float = 0.5):
        self.mill_id = mill_id
        self.target_pressure_bar = target_pressure_bar
        self.tolerance_bar = tolerance_bar
        self.pressure_history: List[float] = []
        self.temperature_history: List[float] = []
        self.max_history_len = 100
        logger.info(f"Initialized RollerMillTensionSentinel for mill {self.mill_id} with target pressure {target_pressure_bar} bar.")

    def ingest_telemetry(self, pressure_bar: float, fluid_temp_c: float) -> Dict[str, Any]:
        """
        Ingests real-time pressure and temperature telemetry from the mill tension system.
        Returns an evaluation report containing health status and corrective action recommendations.
        """
        self.pressure_history.append(pressure_barалы := pressure_bar)
        self.temperature_history.append(fluid_temp_c)

        if len(self.pressure_history) > self.max_history_len:
            self.pressure_history.pop(0)
        if len(self.temperature_history) > self.max_history_len:
            self.temperature_history.pop(0)

        deviation = abs(pressure_bar - self.target_pressure_bar)
        status = "OPTIMAL"
        actions = []

        if deviation > self.tolerance_bar:
            if pressure_bar < self.target_pressure_bar:
                status = "UNDER_TENSION"
                actions.append("Inspect hydraulic pump output, check for internal seal bypass or accumulator charge loss.")
            else:
                status = "OVER_TENSION"
                actions.append("Release pressure relief valve, check for proportional valve sticking.")

        if fluid_temp_c > 65.0:
            status = "THERMAL_WARNING"
            actions.append("Hydraulic fluid temperature exceeds 65°C. Check oil cooler and viscosity rating.")

        # Rapid pressure drop check (potential hose rupture)
        if len(self.pressure_history) >= 5:
            drop_rate = self.pressure_history[-5] - pressure_bar
            if drop_rate > (self.tolerance_bar * 2.0):
                status = "CRITICAL_PRESSURE_DECAY"
                actions.insert(0, "EMERGENCY: Rapid pressure decay detected. Trigger emergency roll separation to prevent damage.")

        report = {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "current_pressure_bar": pressure_bar,
            "target_pressure_bar": self.target_pressure_bar,
            "fluid_temp_c": fluid_temp_c,
            "status": status,
            "corrective_actions": actions
        }

        if status != "OPTIMAL":
            logger.warning(f"Mill {self.mill_id} tension alert: {status} | Pressure: {pressure_bar} bar | Temp: {fluid_temp_c}°C")

        return report

    def get_diagnostics(self) -> Dict[str, Any]:
        """Returns aggregated statistical diagnostics for the tension sentinel."""
        if not self.pressure_history:
            return {"status": "NO_DATA"}
        avg_pressure = sum(self.pressure_history) / len(self.pressure_history)
        avg_temp = sum(self.temperature_history) / len(self.temperature_history)
        return {
            "mill_id": self.mill_id,
            "samples_recorded": len(self.pressure_history),
            "average_pressure_bar": round(avg_pressure, 2),
            "average_fluid_temp_c": round(avg_temp, 2)
        }

if __name__ == "__main__":
    print("[+] Executing RollerMillTensionSentinel Self-Test Harness...")
    sentinel = RollerMillTensionSentinel(mill_id="MILL-NAIROBI-IND-04", target_pressure_bar=6.5, tolerance_bar=0.6)
    
    # Simulate normal telemetry
    rep1 = sentinel.ingest_telemetry(6.4, 45.2)
    assert rep1["status"] == "OPTIMAL", f"Expected OPTIMAL, got {rep1['status']}"
    
    # Simulate pressure drop
    rep2 = sentinel.ingest_telemetry(5.2, 48.0)
    assert rep2["status"] == "UNDER_TENSION", f"Expected UNDER_TENSION, got {rep2['status']}"
    
    # Simulate rapid decay
    for p in [5.2, 5.0, 4.5, 3.8, 2.1]:
        rep_rapid = sentinel.ingest_telemetry(p, 50.0)
    assert rep_rapid["status"] == "CRITICAL_PRESSURE_DECAY", f"Expected CRITICAL_PRESSURE_DECAY, got {rep_rapid['status']}"
    
    diag = sentinel.get_diagnostics()
    print(f"[+] Diagnostics check passed: {diag}")
    print("[+] RollerMillTensionSentinel Self-Test Completed Successfully.")
