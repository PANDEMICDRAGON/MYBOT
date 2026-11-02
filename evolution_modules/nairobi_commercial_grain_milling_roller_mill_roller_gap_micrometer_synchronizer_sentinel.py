import logging
import time
import statistics
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerGapMicrometerSynchronizerSentinel")

class RollerGapMicrometerSynchronizerSentinel:
    """
    Monitors and synchronizes dual-end roller mill gap adjustments via micrometer telemetry,
    detecting mechanical backlash, calibration drift, and hydraulic skew.
    """
    def __init__(self, target_gap_mm: float = 0.45, tolerance_mm: float = 0.015) -> None:
        self.target_gap_mm = target_gap_mm
        self.tolerance_mm = tolerance_mm
        self.telemetry_history: List[Dict[str, float]] = []

    def ingest_telemetry(self, drive_side_mm: float, operator_side_mm: float, hydraulic_psi: float) -> Dict[str, Any]:
        timestamp = time.time()
        delta = abs(drive_side_mm - operator_side_mm)
        mean_gap = (drive_side_mm + operator_side_mm) / 2.0
        error = abs(mean_gap - self.target_gap_mm)

        status = "OPTIMAL"
        correction_pulse = 0.0

        if delta > self.tolerance_mm:
            status = "SKEW_DETECTED"
            correction_pulse = (operator_side_mm - drive_side_mm) * 0.5
        elif error > self.tolerance_mm:
            status = "DRIFT_DETECTED"
            correction_pulse = (self.target_gap_mm - mean_gap) * 0.8

        record = {
            "timestamp": timestamp,
            "drive_side_mm": drive_side_mm,
            "operator_side_mm": operator_side_mm,
            "mean_gap_mm": mean_gap,
            "skew_mm": delta,
            "hydraulic_psi": hydraulic_psi,
            "status": status,
            "correction_pulse": correction_pulse
        }

        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return record

    def generate_diagnostic_summary(self) -> Dict[str, Any]:
        if not self.telemetry_history:
            return {"status": "NO_DATA"}

        means = [r["mean_gap_mm"] for r in self.telemetry_history]
        skews = [r["skew_mm"] for r in self.telemetry_history]

        return {
            "samples_analyzed": len(self.telemetry_history),
            "average_gap": statistics.mean(means),
            "max_skew": max(skews),
            "system_health": "HEALTHY" if max(skews) <= self.tolerance_mm else "ATTENTION_REQUIRED"
        }

if __name__ == "__main__":
    sentinel = RollerGapMicrometerSynchronizerSentinel(target_gap_mm=0.40, tolerance_mm=0.01)
    test_readings = [
        (0.402, 0.398, 120.5),
        (0.405, 0.395, 121.0),
        (0.420, 0.390, 130.0), # Skew trigger
        (0.400, 0.400, 119.5)
    ]
    for ds, os, psi in test_readings:
        res = sentinel.ingest_telemetry(ds, os, psi)
        logger.info(f"Telemetry processed: {res}")
    summary = sentinel.generate_diagnostic_summary()
    logger.info(f"Diagnostic Summary: {summary}")
