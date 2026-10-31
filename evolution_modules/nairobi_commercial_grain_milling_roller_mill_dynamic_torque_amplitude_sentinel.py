"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Amplitude Sentinel."""

import math
import random
import time
from typing import Dict, List, Any


class RollerMillTorqueAmplitudeSentinel:
    """Monitors high-frequency torque amplitude variations on roller mill drives."""

    def __init__(self, mill_id: str, nominal_amplitude_nm: float = 450.0, threshold_pct: float = 18.5):
        self.mill_id = mill_id
        self.nominal_amplitude_nm = nominal_amplitude_nm
        self.threshold_pct = threshold_pct
        self.history: List[float] = []

    def ingest_reading(self, raw_amplitude: float) -> Dict[str, Any]:
        """Ingests a torque amplitude reading, evaluates deviation, and returns diagnostics."""
        self.history.append(raw_amplitude)
        if len(self.history) > 100:
            self.history.pop(0)

        deviation = ((raw_amplitude - self.nominal_amplitude_nm) / self.nominal_amplitude_nm) * 100.0
        is_anomaly = abs(deviation) > self.threshold_pct

        status = "CRITICAL_DEVIATION" if is_anomaly else "NOMINAL"
        if is_anomaly:
            action = "ENGAGE_DYNAMIC_BRAKING_OR_THROTTLE"
        else:
            action = "MAINTAIN_FEED_RATE"

        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "raw_amplitude_nm": raw_amplitude,
            "nominal_amplitude_nm": self.nominal_amplitude_nm,
            "deviation_pct": round(deviation, 2),
            "status": status,
            "action_recommended": action
        }

    def batch_audit(self, readings: List[float]) -> List[Dict[str, Any]]:
        """Audits a batch of torque amplitude sensor metrics."""
        return [self.ingest_reading(r) for r in readings]


if __name__ == "__main__":
    sentinel = RollerMillTorqueAmplitudeSentinel(mill_id="NAI_MILL_ALPHA_04")
    simulated_readings = [440.0, 455.2, 460.1, 540.8, 448.3, 380.0]
    audit_results = sentinel.batch_audit(simulated_readings)
    for res in audit_results:
        print(f"[SENTINEL_AUDIT] Mill: {res['mill_id']} | Amp: {res['raw_amplitude_nm']}Nm | Status: {res['status']} | Action: {res['action_recommended']}")
