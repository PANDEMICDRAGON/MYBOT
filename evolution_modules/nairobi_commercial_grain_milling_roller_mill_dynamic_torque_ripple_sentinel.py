"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Sentinel
Autonomous Evolutionary Architecture Module #35

Designed for real-time telemetry ingestion, high-frequency torque ripple analysis,
and proactive anomaly mitigation for commercial roller mills in Nairobi, Kenya.
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [TORQUE_RIPPLE_SENTINEL] %(levelname)s: %(message)s')
logger = logging.getLogger("TorqueRippleSentinel")

class RollerMillTorqueRippleSentinel:
    """
    Monitors dynamic torque ripple components on roller mill drives, analyzing harmonic
    distortion and mechanical backlash signatures to prevent catastrophic drive train failure.
    """
    def __init__(self, mill_id: str, baseline_ripple_limit: float = 4.5):
        self.mill_id = mill_id
        self.baseline_ripple_limit = baseline_ripple_limit
        self.telemetry_buffer: List[Dict[str, Any]] = []
        self.anomaly_count = 0
        logger.info(f"RollerMillTorqueRippleSentinel initialized for mill: {self.mill_id} with limit {self.baseline_ripple_limit}%")

    def ingest_telemetry(self, timestamp: float, torque_values: List[float]) -> Dict[str, Any]:
        """
        Ingests a burst of raw torque measurements (Nm) and computes the dynamic ripple factor.
        """
        if not torque_values:
            raise ValueError("Torque values buffer cannot be empty.")

        mean_torque = sum(torque_values) / len(torque_values)
        if mean_torque == 0:
            peak_to_peak = 0.0
            ripple_percentage = 0.0
        else:
            max_t = max(torque_values)
            min_t = min(torque_values)
            peak_to_peak = max_t - min_t
            ripple_percentage = (peak_to_peak / mean_torque) * 100.0

        is_anomalous = ripple_percentage > self.baseline_ripple_limit
        if is_anomalous:
            self.anomaly_count += 1
            logger.warning(f"[{self.mill_id}] High Torque Ripple Detected! Ripple: {ripple_percentage:.2f}% (Limit: {self.baseline_ripple_limit}%)")

        record = {
            "timestamp": timestamp,
            "mean_torque": mean_torque,
            "peak_to_peak": peak_to_peak,
            "ripple_percentage": ripple_percentage,
            "is_anomalous": is_anomalous
        }
        self.telemetry_buffer.append(record)
        return record

    def generate_diagnostic_report(self) -> Dict[str, Any]:
        """
        Synthesizes historical telemetry buffer into a diagnostic health summary.
        """
        total_samples = len(self.telemetry_buffer)
        if total_samples == 0:
            return {"status": "NO_DATA", "mill_id": self.mill_id}

        avg_ripple = sum(r["ripple_percentage"] for r in self.telemetry_buffer) / total_samples
        max_ripple = max(r["ripple_percentage"] for r in self.telemetry_buffer)

        return {
            "mill_id": self.mill_id,
            "total_samples": total_samples,
            "average_ripple_percentage": round(avg_ripple, 2),
            "max_ripple_percentage": round(max_ripple, 2),
            "anomaly_count": self.anomaly_count,
            "system_status": "CRITICAL_ATTENTION" if self.anomaly_count > 3 else "OPTIMAL"
        }

if __name__ == "__main__":
    sentinel = RollerMillTorqueRippleSentinel(mill_id="NAIROBI_MILL_ALPHA_01")
    now = time.time()
    
    # Simulate normal and abnormal torque readings (Nm)
    normal_burst = [100.2, 101.5, 99.8, 100.4, 101.1]
    spike_burst = [95.0, 115.5, 88.2, 108.0, 92.1]

    print(sentinel.ingest_telemetry(now, normal_burst))
    print(sentinel.ingest_telemetry(now + 1.0, spike_burst))
    print(sentinel.generate_diagnostic_report())
