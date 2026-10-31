"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Pulse Sentinel

Monitors high-frequency torque pulses and impulse transients in commercial roller
mills across Nairobi grain processing plants, protecting mechanical gearboxes
and roller interfaces from catastrophic harmonic shock.
"""

import logging
import time
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorquePulseSentinel")

class RollerMillTorquePulseSentinel:
    """Analyzes roller mill torque pulse signatures and harmonic transients."""

    def __init__(self, mill_id: str, pulse_threshold_nm: float = 450.0):
        self.mill_id = mill_id
        self.pulse_threshold_nm = pulse_threshold_nm
        self.pulse_history: List[float] = []
        self.anomaly_count = 0
        logger.info(f"Initialized RollerMillTorquePulseSentinel for mill {mill_id} with threshold {pulse_threshold_nm} Nm")

    def ingest_pulse_reading(self, torque_pulse_nm: float, timestamp: Optional[float] = None) -> Dict[str, Any]:
        """Ingests a high-frequency torque pulse sample and evaluates anomaly status."""
        ts = timestamp or time.time()
        self.pulse_history.append(torque_pulse_nm)
        if len(self.pulse_history > 1000):
            self.pulse_history.pop(0)

        is_anomaly = torque_pulse_nm > self.pulse_threshold_nm
        if is_anomaly:
            self.anomaly_count += 1
            logger.warning(f"[{self.mill_id}] Torque pulse anomaly detected: {torque_pulse_nm} Nm (Threshold: {self.pulse_threshold_nm})")

        return {
            "mill_id": self.mill_id,
            "timestamp": ts,
            "current_pulse_nm": torque_pulse_nm,
            "is_anomaly": is_anomaly,
            "total_anomalies": self.anomaly_count
        }

    def get_pulse_statistics(self) -> Dict[str, float]:
        """Computes rolling statistics over accumulated pulse samples."""
        if not self.pulse_history:
            return {"mean": 0.0, "median": 0.0, "max": 0.0, "stdev": 0.0}

        return {
            "mean": statistics.mean(self.pulse_history),
            "median": statistics.median(self.pulse_history),
            "max": max(self.pulse_history),
            "stdev": statistics.stdev(self.pulse_history) if len(self.pulse_history) > 1 else 0.0
        }

if __name__ == "__main__":
    sentinel = RollerMillTorquePulseSentinel(mill_id="NAIROBI-MILL-042")
    test_readings = [310.2, 345.5, 460.1, 320.0, 480.9]
    for r in test_readings:
        res = sentinel.ingest_pulse_reading(r)
        print(f"Ingested: {r} -> Result: {res}")
    print("Statistics:", sentinel.get_pulse_statistics())
