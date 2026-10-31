"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Resonance Damping Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillResonanceDampingSentinel")

class RollerMillResonanceDampingSentinel:
    """
    Monitors dynamic torque resonance frequencies of commercial roller mills in Nairobi grain processing plants,
    calculating damping thresholds and mitigating harmonic oscillations before mechanical degradation occurs.
    """
    def __init__(self, mill_id: str, resonance_limit_hz: float = 75.0, sample_window_size: int = 50):
        self.mill_id = mill_id
        self.resonance_limit_hz = resonance_limit_hz
        self.sample_window_size = sample_window_size
        self.torque_samples: List[float] = []
        self.resonance_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillResonanceDampingSentinel for mill: {self.mill_id}")

    def ingest_torque_reading(self, torque_nm: float, frequency_hz: float) -> Dict[str, Any]:
        """
        Ingests a live torque and harmonic frequency reading from the roller mill drive assembly.
        """
        timestamp = time.time()
        self.torque_samples.append(torque_nm)
        if len(self.torque_samples) > self.sample_window_size:
            self.torque_samples.pop(0)

        status = "NORMAL"
        damping_coefficient = 1.0

        if frequency_hz > self.resonance_limit_hz:
            status = "RESONANCE_WARNING"
            excess = frequency_hz - self.resonance_limit_hz
            damping_coefficient = round(1.0 + (excess / 10.0), 3)
            logger.warning(f"[{self.mill_id}] High torque resonance detected: {frequency_hz} Hz (Limit: {self.resonance_limit_hz} Hz). Applying damping factor: {damping_coefficient}")

        reading = {
            "timestamp": timestamp,
            "torque_nm": torque_nm,
            "frequency_hz": frequency_hz,
            "status": status,
            "damping_coefficient": damping_coefficient
        }
        self.resonance_history.append(reading)
        return reading

    def compute_stability_index(self) -> Dict[str, Any]:
        """
        Computes statistical stability metrics across recent torque and resonance samples.
        """
        if not self.torque_samples:
            return {"status": "NO_DATA"}

        mean_torque = statistics.mean(self.torque_samples)
        stdev_torque = statistics.stdev(self.torque_samples) if len(self.torque_samples) > 1 else 0.0

        anomaly_count = sum(1 for r in self.resonance_history if r["status"] == "RESONANCE_WARNING")

        return {
            "mill_id": self.mill_id,
            "sample_count": len(self.torque_samples),
            "mean_torque_nm": round(mean_torque, 2),
            "stdev_torque_nm": round(stdev_torque, 2),
            "total_warnings": anomaly_count,
            "operational_integrity": "OPTIMAL" if anomaly_count == 0 else "ATTENTION_REQUIRED"
        }

if __name__ == "__main__":
    sentinel = RollerMillResonanceDampingSentinel(mill_id="NAIROBI_MILL_ALPHA_04")
    
    # Simulate normal and resonant telemetry
    test_readings = [
        (245.5, 45.2),
        (248.0, 50.1),
        (290.2, 78.5),  # Resonance warning trigger
        (310.8, 82.4),  # Resonance warning trigger
        (250.1, 55.0)
    ]

    for t_val, f_val in test_readings:
        res = sentinel.ingest_torque_reading(t_val, f_val)
        print(f"Telemetry processed: {res}")

    stability = sentinel.compute_stability_index()
    print(f"Final Mill Stability Report: {stability}")
