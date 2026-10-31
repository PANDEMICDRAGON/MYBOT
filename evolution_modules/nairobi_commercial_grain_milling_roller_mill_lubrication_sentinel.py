"""
Nairobi Commercial Grain Milling Roller Mill Lubrication Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillLubricationSentinel")

class RollerMillLubricationSentinel:
    """
    Monitors centralized oil lubrication pressure, flow rates, and temperature-viscosity
    profiles across commercial roller mill bearing housings in Nairobi grain mills.
    """
    def __init__(self, mill_id: str, oil_grade: str = "ISO VG 150") -> None:
        self.mill_id = mill_id
        self.oil_grade = oil_grade
        self.status = "INITIALIZING"
        self.metrics_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillLubricationSentinel for Mill [{self.mill_id}] using {self.oil_grade}")

    def analyze_lubrication_cycle(
        self, 
        oil_pressure_bar: float, 
        flow_rate_lpm: float, 
        oil_temp_c: float,
        contamination_ppm: float
    ) -> Dict[str, Any]:
        """
        Evaluates lubrication parameters against safe operating thresholds.
        Normal ranges:
          - Pressure: 1.5 - 3.5 bar
          - Flow rate: 4.0 - 8.0 L/min per manifold
          - Oil temperature: 35.0°C - 65.0°C
          - Contamination (metallic/debris): < 50 ppm
        """
        alerts: List[str] = []
        severity = "NORMAL"

        # Pressure checks
        if oil_pressure_bar < 1.2:
            alerts.append("CRITICAL_LOW_PRESSURE: Risk of boundary lubrication and bearing scoring.")
            severity = "CRITICAL"
        elif oil_pressure_bar > 4.0:
            alerts.append("HIGH_PRESSURE: Potential line blockage or filter blinding.")
            severity = "WARNING" if severity != "CRITICAL" else "CRITICAL"

        # Flow rate checks
        if flow_rate_lpm < 3.0:
            alerts.append("LOW_FLOW_RATE: Insufficient oil feed to roller journals.")
            severity = "CRITICAL"

        # Temperature and Viscosity correlation check
        if oil_temp_c > 70.0:
            alerts.append("OVERHEAT: Oil viscosity breakdown imminent.")
            severity = "CRITICAL"
        elif oil_temp_c < 30.0:
            alerts.append("LOW_TEMP: Excessive oil viscosity; poor pumpability.")
            severity = "WARNING" if severity != "CRITICAL" else "CRITICAL"

        # Contamination checks
        if contamination_ppm > 75.0:
            alerts.append("HIGH_CONTAMINATION: Particulate threshold exceeded. Flush required.")
            severity = "CRITICAL"

        evaluation = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "oil_pressure_bar": oil_pressure_bar,
            "flow_rate_lpm": flow_rate_lpm,
            "oil_temp_c": oil_temp_c,
            "contamination_ppm": contamination_ppm,
            "severity": severity,
            "alerts": alerts
        }

        self.metrics_history.append(evaluation)
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)

        if severity != "NORMAL":
            logger.warning(f"[{self.mill_id}] Lubrication Alert [{severity}]: {alerts}")
        else:
            logger.info(f"[{self.mill_id}] Lubrication nominal. Pressure: {oil_pressure_bar} bar, Flow: {flow_rate_lpm} L/min")

        return evaluation

    def get_system_health(self) -> Dict[str, Any]:
        """Returns summary statistics of the lubrication sentinel."""
        if not self.metrics_history:
            return {"status": "NO_DATA"}
        
        recent = self.metrics_history[-1]
        return {
            "mill_id": self.mill_id,
            "last_severity": recent["severity"],
            "total_telemetries_recorded": len(self.metrics_history),
            "status": "ACTIVE"
        }

if __name__ == "__main__":
    print("--- Executing RollerMillLubricationSentinel Test Harness ---")
    sentinel = RollerMillLubricationSentinel(mill_id="NAI_MILL_04_UGALI_LINE")
    
    # Simulate normal pulse
    res1 = sentinel.analyze_lubrication_cycle(2.4, 6.2, 45.5, 12.0)
    assert res1["severity"] == "NORMAL"
    
    # Simulate low pressure anomaly
    res2 = sentinel.analyze_lubrication_cycle(0.9, 2.1, 55.0, 30.0)
    assert res2["severity"] == "CRITICAL"
    
    print("All Lubrication Sentinel assertions passed successfully.")
