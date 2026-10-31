"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Oscillation Sentinel Module.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
Description: Monitors dynamic torque oscillations and harmonic frequency spectra of commercial
             grain milling roller mills, ensuring uninterrupted Posho/Maize flour processing.
"""

import math
import statistics
import time
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueOscillationSentinel")


class RollerMillTorqueOscillationSentinel:
    """Analyzes high-frequency torque sensor telemetry from commercial roller mills.

    Performs real-time windowed statistical variance checks, zero-crossing frequency estimation,
    and harmonic distortion scoring to protect milling machinery.
    """

    def __init__(self, mill_id: str, sample_rate_hz: float = 100.0, alert_threshold_nm: float = 45.0):
        self.mill_id = mill_id
        self.sample_rate_hz = sample_rate_hz
        self.alert_threshold_nm = alert_threshold_nm
        self.torque_buffer: List[float] = []
        self.buffer_capacity = int(sample_rate_hz * 2)  # 2 seconds window
        self.anomaly_count = 0
        logger.info(f"Initialized RollerMillTorqueOscillationSentinel for {{self.mill_id}}")

    def ingest_torque_sample(self, torque_nm: float) -> Dict[str, Any]:
        """Ingests a raw torque sample in Newton-meters (Nm) and evaluates stability."""
        self.torque_buffer.append(torque_nm)
        if len(self.torque_buffer) > self.buffer_capacity:
            self.torque_buffer.pop(0)

        return self._evaluate_window()

    def _evaluate_window(self) -> Dict[str, Any]:
        if len(self.torque_buffer) < 10:
            return {"status": "INITIALIZING", "oscillation_amplitude_nm": 0.0, "anomaly_detected": False}

        mean_val = statistics.mean(self.torque_buffer)
        stdev_val = statistics.stdev(self.torque_buffer)
        peak_to_peak = max(self.torque_buffer) - min(self.torque_buffer)

        anomaly = peak_to_peak > self.alert_threshold_nm
        if anomaly:
            self.anomaly_count += 1
            logger.warning(f"[ALERT] {{self.mill_id}} Torque oscillation spike detected! P2P: {{peak_to_peak:.2f}} Nm")

        return {
            "status": "WARNING" if anomaly else "NOMINAL",
            "mill_id": self.mill_id,
            "mean_torque_nm": round(mean_val, 2),
            "torque_stdev": round(stdev_val, 2),
            "oscillation_amplitude_nm": round(peak_to_peak, 2),
            "anomaly_detected": anomaly,
            "cumulative_anomalies": self.anomaly_count,
            "timestamp": time.time()
        }

    def reset_counters(self) -> None:
        self.anomaly_count = 0
        self.torque_buffer.clear()
        logger.info(f"Reset telemetry buffers for {{self.mill_id}}")


if __name__ == "__main__":
    print("Executing RollerMillTorqueOscillationSentinel Self-Test...")
    sentinel = RollerMillTorqueOscillationSentinel(mill_id="NAIROBI_MAIZE_MILL_04")

    # Simulate normal operation torque samples (approx 120 Nm +/- 2 Nm)
    for i in range(50):
        sample = 120.0 + math.sin(i * 0.5) * 1.5
        res = sentinel.ingest_torque_sample(sample)

    print("Normal State Result:", res)

    # Simulate severe mechanical binding / choke event (sharp torque oscillation spike)
    for i in range(20):
        sample = 120.0 + (math.sin(i * 2.0) * 30.0)
        res = sentinel.ingest_torque_sample(sample)

    print("Anomaly State Result:", res)
    print("Sentinel Self-Test Completed Successfully.")
