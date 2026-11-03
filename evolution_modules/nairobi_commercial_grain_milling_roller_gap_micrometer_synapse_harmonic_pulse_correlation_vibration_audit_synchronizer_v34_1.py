"""Nairobi Commercial Grain Milling Roller Gap Micrometer Synapse Harmonic Pulse
Correlation Vibration Audit Synchronizer V34.1

Designed for high-precision grain milling operations in Nairobi, Kenya.
Correlates roller gap micrometers with harmonic vibration signatures in real-time.
"""

import math
import statistics
import time
from typing import Dict, List, Any, Optional


class RollerGapVibrationAuditSynchronizer:
    """Synchronizes micrometer gap measurements with high-frequency vibration telemetry."""

    def __init__(self, mill_id: str, nominal_gap_mm: float = 0.45):
        self.mill_id = mill_id
        self.nominal_gap_mm = nominal_gap_mm
        self.gap_history: List[float] = []
        self.vibration_history: List[float] = []
        self.audit_logs: List[Dict[str, Any]] = []

    def ingest_telemetry(self, current_gap_mm: float, vibration_rms_g: float) -> Dict[str, Any]:
        """Ingests current gap and vibration metrics, computing harmonic correlation."""
        self.gap_history.append(current_gap_mm)
        self.vibration_history.append(vibration_rms_g)

        # Keep rolling window of last 100 samples
        if len(self.gap_history) > 100:
            self.gap_history.pop(0)
            self.vibration_history.pop(0)

        gap_drift = current_gap_mm - self.nominal_gap_mm
        harmonic_index = self._calculate_harmonic_pulse_index()

        status = "OPTIMAL"
        if abs(gap_drift) > 0.05 or vibration_rms_g > 2.5:
            status = "WARNING_ALIGNMENT_DRIFT"
        if abs(gap_drift) > 0.10 or vibration_rms_g > 4.0:
            status = "CRITICAL_BEARING_WEAR"

        audit_record = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "gap_mm": current_gap_mm,
            "gap_drift_mm": round(gap_drift, 4),
            "vibration_rms_g": vibration_rms_g,
            "harmonic_index": harmonic_index,
            "status": status
        }
        self.audit_logs.append(audit_record)
        return audit_record

    def _calculate_harmonic_pulse_index(self) -> float:
        """Calculates a normalized harmonic pulse index based on vibration variance."""
        if len(self.vibration_history) < 5:
            return 0.0
        mean_v = statistics.mean(self.vibration_history)
        stdev_v = statistics.pstdev(self.vibration_history)
        if mean_v == 0:
            return 0.0
        return round((stdev_v / mean_v) * math.pi, 4)

    def get_audit_summary(self) -> Dict[str, Any]:
        """Summarizes audit findings for operator review."""
        if not self.audit_logs:
            return {"status": "NO_DATA"}
        latest = self.audit_logs[-1]
        return {
            "mill_id": self.mill_id,
            "total_audits": len(self.audit_logs),
            "latest_status": latest["status"],
            "latest_harmonic_index": latest["harmonic_index"]
        }


if __name__ == "__main__":
    print("Initializing RollerGapVibrationAuditSynchronizer V34.1...")
    sync = RollerGapVibrationAuditSynchronizer(mill_id="NAIROBI_MILL_07_UGALI_LINE")
    
    # Test normal ingestion
    res1 = sync.ingest_telemetry(0.46, 1.2)
    print(f"Audit 1 Result: {res1["status"]}, Harmonic Index: {res1["harmonic_index"]}")
    
    # Test drift injection
    res2 = sync.ingest_telemetry(0.58, 3.8)
    print(f"Audit 2 Result: {res2["status"]}, Drift: {res2["gap_drift_mm"]}mm")
    
    summary = sync.get_audit_summary()
    print(f"Audit Summary: {summary}")
    print("Roller Gap Synapse Harmonic Pulse Correlation Audit Synchronizer V34.1 operational.")
