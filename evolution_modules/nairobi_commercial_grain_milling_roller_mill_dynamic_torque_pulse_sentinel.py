"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Pulse Sentinel

Monitor high-frequency torque pulses and transient fluctuations in commercial
roller mills across industrial milling plants in Nairobi, Kenya.
"""

import time
import math
import logging
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorquePulseSentinel")

class RollerMillTorquePulseSentinel:
    """
    Analyzes dynamic torque pulse telemetry from roller mill drive assemblies,
    detecting micro-anomalies, impact spikes, and torsional fatigue precursors.
    """

    def __init__(self, mill_id: str, pulse_threshold_nm: float = 450.0, sample_window_size: int = 50):
        self.mill_id = mill_id
        self.pulse_threshold_nm = pulse_threshold_nm
        self.sample_window_size = sample_window_size
        self.torque_history: List[float] = []
        self.anomaly_count = 0
        logger.info(f"Initialized RollerMillTorquePulseSentinel for mill: {mill_id} with threshold {pulse_threshold_nm} Nm")

    def ingest_reading(self, torque_nm: float, rpm: float, vibration_mm_s: float) -> Dict[str, Any]:
        """
        Ingests a new telemetry sample and evaluates pulse anomalies.
        """
        timestamp = time.time()
        self.torque_history.append(torque_nm)
        if len(self.torque_history) > self.sample_window_size:
            self.torque_history.pop(0)

        mean_torque = sum(self.torque_history) / len(self.torque_history)
        pulse_delta = abs(torque_nm - mean_torque)
        
        is_pulse_anomaly = pulse_delta > self.pulse_threshold_nm
        if is_pulse_anomaly:
            self.anomaly_count += 1
            logger.warning(f"[{self.mill_id}] Torque pulse anomaly detected! Delta: {pulse_delta:.2f} Nm (Current: {torque_nm} Nm, Mean: {mean_torque:.2f} Nm)")

        severity = "CRITICAL" if pulse_delta > (self.pulse_threshold_nm * 1.5) else ("WARNING" if is_pulse_anomaly else "NORMAL")

        return {
            "mill_id": self.mill_id,
            "timestamp": timestamp,
            "torque_nm": torque_nm,
            "mean_torque_nm": mean_torque,
            "pulse_delta_nm": pulse_delta,
            "rpm": rpm,
            "vibration_mm_s": vibration_mm_s,
            "severity": severity,
            "anomaly_count": self.anomaly_count
        }

    def get_diagnostic_report(self) -> Dict[str, Any]:
        """
        Returns cumulative diagnostic statistics for the roller mill sentinel.
        """
        return {
            "mill_id": self.mill_id,
            "total_samples": len(self.torque_history),
            "cumulative_anomalies": self.anomaly_count,
            "status": "ACTIVE_MONITORING"
        }

if __name__ == "__main__":
    sentinel = RollerMillTorquePulseSentinel(mill_id="NAIROBI_MILL_UGALI_04")
    
    # Simulate standard telemetry feed with an injected high-frequency torque pulse
    test_readings = [
        (320.0, 1500.0, 1.2),
        (325.5, 1502.0, 1.3),
        (318.0, 1498.0, 1.1),
        (850.0, 1450.0, 4.8),  # Sudden hard grain foreign object pulse
        (322.0, 1500.0, 1.2)
    ]

    for t, r, v in test_readings:
        result = sentinel.ingest_reading(t, r, v)
        logger.info(f"Test ingestion result: {result}")

    report = sentinel.get_diagnostic_report()
    logger.info(f"Diagnostic Report: {report}")
