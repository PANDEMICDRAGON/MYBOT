"""Nairobi Commercial Grain Milling Roller Mill Roll Torque Harmonic Sentinel.

Provides real-time telemetry analysis, harmonic distortion profiling, and anomaly
detection for commercial grain milling roller drive systems in Nairobi, Kenya.
"""

import math
import statistics
import time
from typing import Dict, List, Optional, Tuple


class RollerMillTorqueHarmonicSentinel:
    """Monitors roller mill drive torque harmonics to detect mechanical binding, bearing wear,
    and belt slippage before catastrophic equipment failure occurs.
    """

    def __init__(self, mill_id: str, nominal_frequency_hz: float = 50.0, harmonic_threshold: float = 0.15):
        self.mill_id = mill_id
        self.nominal_frequency_hz = nominal_frequency_hz
        self.harmonic_threshold = harmonic_threshold
        self.telemetry_buffer: List[Dict[str, float]] = []
        self.alert_history: List[Dict[str, any]] = []

    def ingest_telemetry(self, timestamp: float, current_torque_nm: float,
                         motor_rpm: float, vibration_acceleration_g: float) -> Dict[str, any]:
        """Ingests a new telemetry sample and computes instantaneous harmonic health indices."""
        sample = {
            "timestamp": timestamp,
            "torque_nm": current_torque_nm,
            "rpm": motor_rpm,
            "vibration_g": vibration_acceleration_g
        }
        self.telemetry_buffer.append(sample)
        if len(self.telemetry_buffer) > 1000:
            self.telemetry_buffer.pop(0)

        return self._evaluate_health(sample)

    def _evaluate_health(self, sample: Dict[str, float]) -> Dict[str, any]:
        if len(self.telemetry_buffer) < 10:
            return {"status": "INITIALIZING", "harmonic_index": 0.0, "anomaly_detected": False}

        torques = [s["torque_nm"] for s in self.telemetry_buffer[-50:]]
        mean_torque = statistics.mean(torques)
        stdev_torque = statistics.stdev(torques) if len(torques) > 1 else 0.0

        # Normalized harmonic variance ratio
        harmonic_index = (stdev_torque / mean_torque) if mean_torque > 0 else 0.0
        anomaly = harmonic_index > self.harmonic_threshold

        result = {
            "mill_id": self.mill_id,
            "timestamp": sample["timestamp"],
            "mean_torque_nm": mean_torque,
            "harmonic_index": harmonic_index,
            "anomaly_detected": anomaly,
            "status": "CRITICAL_ATTENTION_REQUIRED" if anomaly else "OPTIMAL"
        }

        if anomaly:
            self.alert_history.append(result)

        return result

    vald_diagnostics = _evaluate_health

    def get_audit_summary(self) -> Dict[str, any]:
        """Returns summary statistics and total recorded anomalies."""
        return {
            "mill_id": self.mill_id,
            "total_samples": len(self.telemetry_buffer),
            "total_alerts": len(self.alert_history),
            "last_status": self.alert_history[-1] if self.alert_history else "NORMAL"
        }


if __name__ == "__main__":
    sentinel = RollerMillTorqueHarmonicSentinel(mill_id="NAI_MILL_UNGA_04")
    print(f"Initialized Sentinel for {sentinel.mill_id}")

    # Simulate normal and anomalous telemetry ingestion
    base_time = time.time()
    for i in range(20):
        # Inject anomaly midway
        torque_noise = 25.0 if i < 10 else 65.5
        status = sentinel.ingest_telemetry(
            timestamp=base_time + (i * 1.0),
            current_torque_nm=200.0 + torque_noise,
            motor_rpm=1480.0,
            vibration_acceleration_g=0.4 if i < 10 else 2.1
        )
        print(f"Sample {i}: Status={status['status']}, Harmonic Index={status['harmonic_index']:.4f}")

    summary = sentinel.get_audit_summary()
    print(f"Final Audit Summary: {summary}")
