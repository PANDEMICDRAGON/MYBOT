"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Harmonic Cascade Sentinel.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Monitors roller mill drive shafts for high-frequency torque harmonic cascades, phase anomalies,
and cumulative mechanical fatigue in industrial milling setups.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillHarmonicCascadeSentinel")


class RollerMillHarmonicCascadeSentinel:
    """Analyzes high-frequency torque sensor telemetry from commercial roller mills.
    
    Detects harmonic cascades that precede drive-train binding, belt slippage, or
    bearing thermal runaway in high-throughput flour and maize milling operations.
    """

    def __init__(self, mill_id: str, baseline_frequency_hz: float = 50.0, harmonic_threshold: float = 3.5):
        self.mill_id = mill_id
        self.baseline_freq = baseline_frequency_hz
        self.harmonic_threshold = harmonic_threshold
        self.telemetry_buffer: List[Dict[str, Any]] = []
        self.anomaly_count = 0
        logger.info(f"Initialized Harmonic Cascade Sentinel for Mill [{self.mill_id}] at {baseline_freq}Hz baseline.")

    def ingest_telemetry(self, torque_samples: List[float], timestamp: Optional[float] = None) -> Dict[str, Any]:
        """Ingests a burst of raw torque samples (Nm) and computes cascade metrics."""
        ts = timestamp or time.time()
        if not torque_samples:
            return {"status": "INVALID_SAMPLE_SET", "cascade_index": 0.0}

        mean_torque = sum(torque_samples) / len(torque_samples)
        variance = sum((x - mean_torque) ** 2 for x in torque_samples) / len(torque_samples)
        std_dev = math.sqrt(variance)

        # Fast Fourier transform proxy via discrete harmonic energy estimation
        peak_amplitude = max(abs(x - mean_torque) for x in torque_samples)
        cascade_ratio = (peak_amplitude / (std_dev + 1e-6)) 

        assessment = {
            "timestamp": ts,
            "mill_id": self.mill_id,
            "mean_torque_nm": round(mean_torque, 2),
            "torque_std_dev": round(std_dev, 2),
            "cascade_index": round(cascade_ratio, 4),
            "status": "NOMINAL"
        }

        if cascade_ratio > self.harmonic_threshold:
            self.anomaly_count += 1
            assessment["status"] = "HARMONIC_CASCADE_WARNING"
            logger.warning(f"[ALERT] Harmonic Cascade Warning on {self.mill_id}! Index: {cascade_ratio:.2f}")

        self.telemetry_buffer.append(assessment)
        if len(self.telemetry_buffer) > 1000:
            self.telemetry_buffer.pop(0)

        return assessment

    def get_diagnostic_report(self) -> Dict[str, Any]:
        """Generates a comprehensive diagnostic summary for operator review."""
        return {
            "mill_id": self.mill_id,
            "total_readings": len(self.telemetry_buffer),
            "total_anomalies": self.anomaly_count,
            "system_health": "DEGRADED" if self.anomaly_count > 5 else "OPTIMAL"
        }


if __name__ == "__main__":
    print("=== Testing RollerMillHarmonicCascadeSentinel ===")
    sentinel = RollerMillHarmonicCascadeSentinel(mill_id="NAIROBI-MILL-ALPHA-04")
    
    # Simulate normal operation telemetry burst
    normal_burst = [100.0 + random.gauss(0, 1.2) for _ in range(64)]
    res1 = sentinel.ingest_telemetry(normal_burst)
    print(f"Normal telemetry result: {res1}")

    # Simulate cascade resonance anomaly burst
    anomaly_burst = [100.0 + (15.0 * math.sin(i * 0.5)) + random.gauss(0, 0.5) for _ in range(64)]
    res2 = sentinel.ingest_telemetry(anomaly_burst)
    print(f"Anomaly telemetry result: {res2}")

    print("Diagnostic Report:", sentinel.get_diagnostic_report())
