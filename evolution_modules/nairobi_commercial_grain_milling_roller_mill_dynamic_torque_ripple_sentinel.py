"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Sentinel
Written by Cortana, Autonomous Evolutionary Architect
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorqueRippleSentinel")

class TorqueRippleSentinel:
    """
    Monitors roller mill drive torque ripple signatures to detect micro-slip,
    bearing degradation, and feed starvation in high-throughput grain mills.
    """
    def __init__(self, mill_id: str, sample_rate_hz: float = 100.0, ripple_threshold_pct: float = 8.5):
        self.mill_id = mill_id
        self.sample_rate_hz = sample_rate_hz
        self.ripple_threshold_pct = ripple_threshold_pct
        self.telemetry_buffer: List[float] = []
        self.anomaly_count = 0

    def ingest_torque_signal(self, torque_samples: List[float]) -> Dict[str, Any]:
        """
        Ingests a batch of torque measurements (in Nm) and computes peak-to-peak
        ripple percentage relative to the mean torque.
        """
        if not torque_samples:
            return {"status": "no_data", "ripple_pct": 0.0, "alert": False}

        self.telemetry_buffer.extend(torque_samples)
        # Keep last 500 samples
        if len(self.telemetry_buffer) > 500:
            self.telemetry_buffer = self.telemetry_buffer[-500:]

        mean_torque = sum(torque_samples) / len(torque_samples)
        if mean_torque <= 0.0:
            return {"status": "error", "message": "Zero or negative mean torque", "alert": True}

        max_val = max(torque_samples)
        min_val = min(torque_samples)
        ripple_amplitude = max_val - min_val
        ripple_pct = (ripple_amplitude / mean_torque) * 100.0

        is_anomaly = ripple_pct > self.ripple_threshold_pct
        if is_anomaly:
            self.anomaly_count += 1
            logger.warning(f"[Mill {self.mill_id}] High Torque Ripple Detected! Ripple: {ripple_pct:.2f}% (Threshold: {self.ripple_threshold_pct}%)")

        return {
            "mill_id": self.mill_id,
            "status": "nominal" if not is_anomaly else "warning_ripple_spike",
            "mean_torque_nm": round(mean_torque, 3),
            "ripple_pct": round(ripple_pct, 2),
            "anomaly_count": self.anomaly_count,
            "alert": is_anomaly,
            "timestamp": time.time()
        }

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Sentinel...")
    sentinel = TorqueRippleSentinel(mill_id="MILL-NRB-04", sample_rate_hz=100.0, ripple_threshold_pct=7.5)
    
    # Simulate normal operation torque samples
    normal_torque = [50.2 + math.sin(i * 0.1) * 2.0 for i in range(100)]
    res_normal = sentinel.ingest_torque_signal(normal_torque)
    print("Normal Operation Analysis:", res_normal)
    
    # Simulate abnormal ripple spike (e.g. feed choke or bearing bind)
    anomaly_torque = [50.2 + math.sin(i * 0.5) * 8.0 for i in range(100)]
    res_anomaly = sentinel.ingest_torque_signal(anomaly_torque)
    print("Anomaly Operation Analysis:", res_anomaly)
    print("Roller Mill Torque Ripple Sentinel verification complete.")
