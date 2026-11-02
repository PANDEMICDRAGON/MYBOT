"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Micrometer Correlation Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Monitors and correlates micrometer roller gap feedback with dynamic motor load
and acoustic vibration signatures to maintain optimal flour extraction parameters.
"""

import logging
import random
import time
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerGapMicrometerCorrelationSentinel")


class RollerGapMicrometerCorrelationSentinel:
    """Performs real-time correlation between mechanical roller gap micrometer sensors,
drive motor load, and vibration telemetry in Nairobi commercial grain mills.
    """

    def __init__(self, mill_id: str, target_gap_microns: float = 150.0, tolerance_microns: float = 5.0) -> None:
        self.mill_id = mill_id
        self.target_gap_microns = target_gap_microns
        self.tolerance_microns = tolerance_microns
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerGapMicrometerCorrelationSentinel for mill '{mill_id}' with target gap {target_gap_microns}um")

    def ingest_sensor_reading(self, actual_gap_microns: float, motor_load_amps: float, vibration_mm_s: float) -> Dict[str, Any]:
        """Ingests telemetry from gap micrometer, motor current sensor, and vibration transducer.
        """
        timestamp = time.time()
        gap_deviation = actual_gap_microns - self.target_gap_microns
        is_out_of_tolerance = abs(gap_deviation) > self.tolerance_microns
        
        # Correlation index combining gap drift with motor load anomalies
        load_factor = motor_load_amps / 50.0  # Normalized baseline
        correlation_index = round(abs(gap_deviation) * load_factor * (1.0 + vibration_mm_s), 4)
        
        status = "OPTIMAL"
        action_required = "NONE"
        
        if is_out_of_tolerance:
            status = "WARNING"
            action_required = "CALIBRATE_MICROMETER_ACTUATOR"
            if abs(gap_deviation) > (self.tolerance_microns * 2.0):
                status = "CRITICAL"
                action_required = "EMERGENCY_ROLLER_SHUTDOWN"

        reading = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "actual_gap_microns": actual_gap_microns,
            "gap_deviation_microns": gap_deviation,
            "motor_load_amps": motor_load_amps,
            "vibration_mm_s": vibration_mm_s,
            "correlation_index": correlation_index,
            "status": status,
            "action_required": action_required
        }

        self.telemetry_history.append(reading)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return reading

    def generate_diagnostic_summary(self) -> Dict[str, Any]:
        """Summarizes recent roller gap health and anomaly distribution.
        """
        if not self.telemetry_history:
            return {"status": "NO_DATA"}

        recent = self.telemetry_history[-50:]
        critical_count = sum(1 for r in recent if r["status"] == "CRITICAL")
        warning_count = sum(1 for r in recent if r["status"] == "WARNING")
        avg_gap = sum(r["actual_gap_microns"] for r in recent) / len(recent)
        avg_correlation = sum(r["correlation_index"] for r in recent) / len(recent)

        return {
            "mill_id": self.mill_id,
            "samples_analyzed": len(recent),
            "average_gap_microns": round(avg_gap, 2),
            "average_correlation_index": round(avg_correlation, 4),
            "warning_events": warning_count,
            "critical_events": critical_count,
            "system_health": "DEGRADED" if critical_count > 0 else ("STABLE" if warning_count == 0 else "ATTENTION_REQUIRED")
        }


if __name__ == "__main__":
    print("Executing Test Harness for RollerGapMicrometerCorrelationSentinel...")
    sentinel = RollerGapMicrometerCorrelationSentinel(mill_id="NAI_MILL_04_UNGA")
    
    # Simulate readings
    for i in range(10):
        gap = 150.0 + random.uniform(-8.0, 8.0)
        load = 45.0 + random.uniform(-2.0, 5.0)
        vib = 1.2 + random.uniform(0.0, 0.8)
        res = sentinel.ingest_sensor_reading(gap, load, vib)
        print(f"Iteration {i+1}: Gap={res['actual_gap_microns']:.1f}um, Status={res['status']}, Action={res['action_required']}")

    summary = sentinel.generate_diagnostic_summary()
    print("Diagnostic Summary:", summary)
    print("Module executed successfully.")
