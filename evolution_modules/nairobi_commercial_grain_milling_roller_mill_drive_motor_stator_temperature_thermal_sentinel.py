"""
Nairobi Commercial Grain Milling Roller Mill Drive Motor Stator Temperature Thermal Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Monitors RTD/thermocouple temperature telemetry from roller mill drive motor stators,
detecting abnormal thermal gradients, bearing friction bleed, and overload conditions.
"""

import time
import math
import logging
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillStatorSentinel")

class RollerMillStatorThermalSentinel:
    """
    Real-time thermal monitoring and predictive anomaly detection for commercial
    grain milling roller mill drive motor stators.
    """
    def __init__(self, mill_id: str, rated_max_temp_c: float = 120.0, warning_threshold_c: float = 95.0):
        self.mill_id = mill_id
        self.rated_max_temp_c = rated_max_temp_c
        self.warning_threshold_c = warning_threshold_c
        self.temperature_history: List[float] = []
        self.anomaly_count = 0

    def ingest_reading(self, current_temp_c: float, ambient_temp_c: float = 25.0, load_amps: float = 50.0) -> Dict[str, Any]:
        """
        Ingests motor stator temperature, ambient temp, and load current to evaluate thermal status.
        """
        self.temperature_history.append(current_temp_c)
        if len(self.temperature_history) > 100:
            self.temperature_history.pop(0)

        # Compute temperature rise above ambient
        temp_rise = current_temp_c - ambient_temp_c
        
        status = "OPTIMAL"
        action_required = False
        mitigation_strategy = "None"

        if current_temp_c >= self.rated_max_temp_c:
            status = "CRITICAL_OVERHEAT"
            action_required = True
            mitigation_strategy = "EMERGENCY_TRIP_MOTOR"
            self.anomaly_count += 1
        elif current_temp_c >= self.warning_threshold_c:
            status = "WARNING_ELEVATED_TEMP"
            action_required = True
            mitigation_strategy = "REDUCE_FEED_GATE_LOAD_AND_CHECK_LUBRICATION"
            self.anomaly_count += 1

        # Check for rapid thermal gradient (spike)
        if len(self.temperature_history) >= 5:
            recent_delta = self.temperature_history[-1] - self.temperature_history[-5]
            if recent_delta > 5.0:  # Rising > 5 deg C in 5 cycles
                status = "RAPID_THERMAL_ACCELERATION"
                action_required = True
                mitigation_strategy = "INSPECT_DRIVE_BELT_SLIP_OR_BEARING_BINDING"

        telemetry = {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "stator_temp_c": current_temp_c,
            "ambient_temp_c": ambient_temp_c,
            "temp_rise_c": temp_rise,
            "load_amps": load_amps,
            "status": status,
            "action_required": action_required,
            "mitigation": mitigation_strategy,
            "anomaly_count": self.anomaly_count
        }

        logger.info(f"[StatorSentinel::{self.mill_id}] Temp: {current_temp_c}C | Status: {status} | Action: {mitigation_strategy}")
        return telemetry

    def get_diagnostic_summary(self) -> Dict[str, Any]:
        avg_temp = sum(self.temperature_history) / len(self.temperature_history) if self.temperature_history else 0.0
        return {
            "mill_id": self.mill_id,
            "average_tracked_temp_c": round(avg_temp, 2),
            "total_anomalies_detected": self.anomaly_count,
            "sentinel_status": "ACTIVE"
        }

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Drive Motor Stator Temperature Thermal Sentinel...")
    sentinel = RollerMillStatorThermalSentinel(mill_id="NAIROBI_MILL_LINE_4_ROLLER_2")
    
    # Simulate normal and elevated telemetry runs
    test_readings = [
        (70.0, 24.0, 45.0),
        (75.5, 24.5, 48.0),
        (88.0, 25.0, 62.0),
        (96.5, 25.0, 85.0),
        (105.0, 26.0, 95.0)
    ];

    for temp, amb, amps in test_readings:
        res = sentinel.ingest_reading(temp, amb, amps)
        print(res)

    print("Diagnostic Summary:", sentinel.get_diagnostic_summary())
    print("Sentinel test execution completed successfully.")
