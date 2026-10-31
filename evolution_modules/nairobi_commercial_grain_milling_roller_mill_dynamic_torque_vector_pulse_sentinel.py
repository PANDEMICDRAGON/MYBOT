"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Vector Pulse Sentinel Module."""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillVectorPulseSentinel")

class RollerMillVectorPulseSentinel:
    """Monitors, analyzes, and mitigates dynamic torque vector pulses in commercial roller mills."""

    def __init__(self, mill_id: str, rated_torque_nm: float = 450.0, pulse_threshold_pct: float = 18.5):
        self.mill_id = mill_id
        self.rated_torque_nm = rated_torque_nm
        self.pulse_threshold_pct = pulse_threshold_pct
        self.telemetry_history: List[Dict[str, Any]] = []
        self.anomaly_count = 0
        logger.info(f"Initialized RollerMillVectorPulseSentinel for {{self.mill_id}} at rated {{self.rated_torque_nm}} Nm.")

    def ingest_torque_vector(self, fast_roll_torque: float, slow_roll_torque: float, phase_angle_deg: float) -> Dict[str, Any]:
        """Ingests instantaneous torque vector data from fast and slow rolls."""
        combined_torque = fast_roll_torque + slow_roll_torque
        torque_delta = abs(fast_roll_torque - slow_roll_torque)
        deviation_pct = (torque_delta / self.rated_torque_nm) * 100.0

        is_pulse_anomaly = deviation_pct > self.pulse_threshold_pct
        if is_pulse_anomaly:
            self.anomaly_count += 1
            logger.warning(f"[{self.mill_id}] TORQUE VECTOR PULSE ANOMALY DETECTED! Deviation: {{deviation_pct:.2f}}% (Phase: {{phase_angle_deg}}°)")

        record = {
            "timestamp": time.time(),
            "fast_roll_torque": fast_roll_torque,
            "slow_roll_torque": slow_roll_torque,
            "combined_torque": combined_torque,
            "phase_angle_deg": phase_angle_deg,
            "deviation_pct": deviation_pct,
            "anomaly": is_pulse_anomaly
        }
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return record

    def compute_vector_stability_index(self) -> float:
        """Computes overall roller mill dynamic torque stability index (0.0 to 100.0)."""
        if not self.telemetry_history:
            return 100.0
        recent = self.telemetry_history[-50:]
        anomalies = sum(1 for r in recent if r["anomaly"])
        stability = max(0.0, 100.0 - (anomalies / len(recent)) * 100.0)
        return round(stability, 2)

    def generate_diagnostic_report(self) -> Dict[str, Any]:
        """Generates a comprehensive diagnostic report for operator Michael Obiero."""
        return {
            "mill_id": self.mill_id,
            "total_telemetry_samples": len(self.telemetry_history),
            "cumulative_anomalies": self.anomaly_count,
            "stability_index": self.compute_vector_stability_index(),
            "status": "CRITICAL_ATTENTION_REQUIRED" if self.anomaly_count > 5 else "OPTIMAL"
        }

if __name__ == "__main__":
    sentinel = RollerMillVectorPulseSentinel("NAIROBI_MILL_UNIT_04")
    # Simulate normal operation
    sentinel.ingest_torque_vector(210.5, 205.2, 12.4)
    sentinel.ingest_torque_vector(212.0, 204.8, 13.1)
    # Simulate pulse spike anomaly
    sentinel.ingest_torque_vector(340.0, 150.0, 45.8)
    report = sentinel.generate_diagnostic_report()
    print("Diagnostic Report:", report)
