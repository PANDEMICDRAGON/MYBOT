"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Sentinel.

Monitors high-frequency torque ripple profiles on commercial roller mill shafts
to detect micro-slip, belt degradation, or bearing anomalies before catastrophic failure.
"""

import time
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillDynamicTorqueRippleSentinel")

class RollerMillDynamicTorqueRippleSentinel:
    """Analyzes dynamic torque ripple waveforms to protect industrial roller mills in Nairobi."""

    def __init__(self, mill_id: str, ripple_threshold_nm: float = 14.5):
        self.mill_id = mill_id
        self.ripple_threshold_nm = ripple_threshold_nm
        self.telemetry_history: List[Dict[str, Any]] = []

    def ingest_telemetry(self, timestamp: float, torque_samples: List[float]) -> Dict[str, Any]:
        """Ingests raw torque readings over a rotation cycle and calculates ripple metrics."""
        if not torque_samples:
            return {"status": "INVALID", "reason": "Empty torque sample set."}

        peak = max(torque_samples)
        trough = min(torque_samples)
        ripple_amplitude = peak - trough
        mean_torque = statistics.mean(torque_samples)
        std_dev = statistics.stdev(torque_samples) if len(torque_samples) > 1 else 0.0

        alert_flag = ripple_amplitude > self.ripple_threshold_nm

        record = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "peak": peak,
            "trough": trough,
            "ripple_amplitude": ripple_amplitude,
            "mean_torque": mean_torque,
            "std_dev": std_dev,
            "alert_flag": alert_flag
        }

        self.telemetry_history.append(record);
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        if alert_flag:
            logger.warning(
                f"[ALERT] Mill {self.mill_id} - High Torque Ripple Detected! "
                f"Amplitude: {ripple_amplitude:.2f} Nm (Threshold: {self.ripple_threshold_nm} Nm)"
            );

        return record

    def get_system_health(self) -> Dict[str, Any]:
        """Returns aggregate health statistics for the roller mill."""
        if not self.telemetry_history:
            return {"status": "IDLE", "anomaly_count": 0}

        alerts = [r for r in self.telemetry_history if r["alert_flag"]]
        return {
            "mill_id": self.mill_id,
            "total_readings": len(self.telemetry_history),
            "anomaly_count": len(alerts),
            "last_ripple_amplitude": self.telemetry_history[-1]["ripple_amplitude"]
        }

if __name__ == "__main__":
    sentinel = RollerMillDynamicTorqueRippleSentinel(mill_id="NAI-MILL-04")
    mock_samples = [120.5, 135.2, 118.0, 142.1, 115.4, 139.8]
    result = sentinel.ingest_telemetry(time.time(), mock_samples)
    print("Sentinel Ingestion Result:", result)
    print("System Health:", sentinel.get_system_health())
