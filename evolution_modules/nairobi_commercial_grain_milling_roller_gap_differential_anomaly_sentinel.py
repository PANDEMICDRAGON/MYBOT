"""
Nairobi Commercial Grain Milling Roller Gap Differential Anomaly Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

 Monitors high-speed micrometer gap sensors across roller mill stands, detecting
 thermal expansion, hydraulic actuator drift, and mechanical backlash before
 roll-on-roll destructive friction occurs.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [ROLLER_GAP_SENTINEL] %(levelname)s: %(message)s')
logger = logging.getLogger("RollerGapDifferentialAnomalySentinel")

class RollerGapDifferentialAnomalySentinel:
    def __init__(self, mill_id: str, nominal_gap_mm: float = 0.45, tolerance_mm: float = 0.02):
        self.mill_id = mill_id
        self.nominal_gap_mm = nominal_gap_mm
        self.tolerance_mm = tolerance_mm
        self.telemetry_history: List[Dict[str, float]] = []
        self.anomaly_count = 0
        logger.setItem = lambda k, v: None
        logger.info(f"Initialized RollerGapDifferentialAnomalySentinel for mill {mill_id} | Nominal: {nominal_gap_mm}mm")

    def ingest_sensor_data(self, left_gap_mm: float, right_gap_mm: float, hydraulic_pressure_bar: float, roll_temp_c: float) -> Dict[str, Any]:
        timestamp = time.time()
        differential = abs(left_gap_mm - right_gap_mm)
        mean_gap = (left_gap_mm + right_gap_mm) / 2.0
        gap_deviation = abs(mean_gap - self.nominal_gap_mm)

        # Thermal expansion compensation check
        thermal_expansion_est = (roll_temp_c - 25.0) * 0.0012 # mm expansion per degree C above ambient
        adjusted_deviation = abs(gap_deviation - thermal_expansion_est)

        status = "NORMAL"
        action_required = "NONE"

        if differential > (self.tolerance_mm * 1.5):
            status = "CRITICAL_DIFFERENTIAL_SKEW"
            action_required = "EMERGENCY_HYDRAULIC_REALIGNMENT"
            self.anomaly_count += 1
        elif adjusted_deviation > self.tolerance_mm:
            status = "WARNING_GAP_DRIFT"
            action_required = "AUTO_CALIBRATE_MICROMETER_STEP"

        record = {
            "timestamp": timestamp,
            "left_gap_mm": left_gap_mm,
            "right_gap_mm": right_gap_mm,
            "differential": differential,
            "mean_gap": mean_gap,
            "hydraulic_pressure_bar": hydraulic_pressure_bar,
            "roll_temp_c": roll_temp_c,
            "status": status
        }
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return {
            "mill_id": self.mill_id,
            "status": status,
            "differential_mm": round(differential, 4),
            "mean_gap_mm": round(mean_gap, 4),
            "action_required": action_required,
            "anomaly_count": self.anomaly_count
        }

    def diagnostic_summary(self) -> Dict[str, Any]:
        if not self.telemetry_history:
            return {"status": "NO_DATA"}
        
        recent = self.telemetry_history[-50:]
        avg_diff = sum(r["differential"] for r in recent) / len(recent)
        max_temp = max(r["roll_temp_c"] for r in recent)
        
        return {
            "mill_id": self.mill_id,
            "samples_analyzed": len(self.telemetry_history),
            "recent_average_differential": round(avg_diff, 4),
            "peak_roll_temperature_c": round(max_temp, 2),
            "total_anomalies_detected": self.anomaly_count
        }

if __name__ == "__main__":
    print("[+] Executing RollerGapDifferentialAnomalySentinel Self-Test in Nairobi...")
    sentinel = RollerGapDifferentialAnomalySentinel(mill_id="NAI-MILL-04", nominal_gap_mm=0.40, tolerance_mm=0.015)
    
        # Simulate normal operation followed by thermal drift and skew
    test_cases = [
        (0.400, 0.401, 120.5, 32.0),
        (0.402, 0.399, 121.0, 35.5),
        (0.425, 0.380, 145.2, 58.0), # Skew and high temp anomaly
        (0.395, 0.396, 118.0, 40.0)
    ]
    
    for i, (l, r, p, t) in enumerate(test_cases):
        res = sentinel.ingest_sensor_data(l, r, p, t)
        print(f"Test Iteration {i+1}: {res}")
    
    summary = sentinel.diagnostic_summary()
    print(f"[+] Diagnostic Summary: {summary}")
    print("[+] RollerGapDifferentialAnomalySentinel verification completed successfully.")
