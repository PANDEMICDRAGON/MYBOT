"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Phase Sentinel
Designed to monitor roller mill drive phase angles, detect mechanical load imbalances,
slip, or transmission binding, and protect milling operations in industrial Nairobi facilities.
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorquePhaseSentinel")


class RollerMillTorquePhaseSentinel:
    """
    Monitors multi-phase torque telemetry from commercial roller mills, analyzing
    phase angle dispersion and harmonic symmetry to preempt drive-train failure.
    """

    def __init__(self, mill_id: str, nominal_frequency_hz: float = 50.0, max_phase_deviation_deg: float = 4.5):
        self.mill_id = mill_id
        self.nominal_frequency_hz = nominal_frequency_hz
        self.max_phase_deviation_deg = max_phase_deviation_deg
        self.telemetry_history: List[Dict[str, Any]] = []
        self.status = "STANDBY"

    def ingest_telemetry(self, phase_angles: List[float], current_draws: List[float]) -> Dict[str, Any]:
        """
        Ingests instantaneous phase angles (degrees) and current draws (Amps) for 3-phase drive.
        """
        timestamp = time.time()
        if len(phase_angles) != 3 or len(current_draws) != 3:
            raise ValueError("Telemetry must contain exactly 3 phase values for standard industrial drives.")

        # Calculate mean phase angle
        mean_phase = sum(phase_angles) / 3.0
        deviations = [abs(p - mean_phase) for p in phase_angles]
        max_deviation = max(deviations)

        # Calculate current imbalance
        mean_current = sum(current_draws) / 3.0
        current_imbalance = max([abs(c - mean_current) for c in current_draws]) / (mean_current if mean_current > 0 else 1.0)

        anomaly_flag = max_deviation > self.max_phase_deviation_deg or current_imbalance > 0.12

        record = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "phase_angles": phase_angles,
            "max_deviation": max_deviation,
            "current_imbalance": current_imbalance,
            "anomaly": anomaly_flag
        }

        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        if anomaly_flag:
            self.status = "WARNING_PHASE_ASYMMETRY"
            logger.warning(f"[ALERT] Mill {self.mill_id}: Phase deviation {max_deviation:.2f} deg or current imbalance {current_imbalance:.2f} detected!")
        else:
            self.status = "OPTIMAL"

        return record

    def generate_diagnostic_report(self) -> Dict[str, Any]:
        """
        Generates a diagnostic summary for the operator.
        """
        if not self.telemetry_history:
            return {"status": self.status, "message": "No telemetry recorded yet."}

        recent = self.telemetry_history[-1]
        return {
            "mill_id": self.mill_id,
            "status": self.status,
            "last_check": recent,
            "total_samples_analyzed": len(self.telemetry_history)
        }


if __name__ == "__main__":
    sentinel = RollerMillTorquePhaseSentinel(mill_id="NAI_UGALI_MILL_04")
    # Simulate normal operation
    res1 = sentinel.ingest_telemetry([0.0, 120.2, 239.8], [45.1, 44.9, 45.2])
    print("Normal Ingestion Result:", res1)

    # Simulate phase asymmetry due to belt slip or gearbox wear
    res2 = sentinel.ingest_telemetry([0.0, 126.5, 235.1], [52.3, 41.0, 48.6])
    print("Anomaly Ingestion Result:", res2)
    print("Diagnostic Report:", sentinel.generate_diagnostic_report())
