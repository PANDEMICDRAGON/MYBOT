"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Stratosphere Harmonic Sentinel

Provides real-time harmonic analysis, cross-roller phase telemetry, and predictive anomaly detection
for industrial roller mills operating in Nairobi, Kenya.
"""

import math
import time
import statistics
from typing import Dict, List, Any, Optional

class RollerMillHarmonicSentinel:
    """Monitors high-frequency torque harmonics and phase angles across dual roller mill assemblies."""
    
    def __init__(self, mill_id: str, nominal_rpm: float = 1200.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.harmonic_history: List[Dict[str, float]] = []
        self.anomaly_count = 0

    def ingest_torque_spectrum(self, timestamp: float, fundamental_torque: float, harmonic_amplitudes: List[float]) -> Dict[str, Any]:
        """Ingests a spectrum of torque harmonics, computing THD (Total Harmonic Distortion) and assessing health."""
        if not harmonic_amplitudes:
            thd = 0.0
        else:
            fundamental = max(abs(fundamental_torque), 1e-6)
            sum_sq = sum(h ** 2 for h in harmonic_amplitudes)
            thd = math.sqrt(sum_sq) / fundamental

        status = "NOMINAL"
        if thd > 0.35:
            status = "CRITICAL_HARMONIC_DISTORTION"
            self.anomaly_count += 1
        elif thd > 0.20:
            status = "ELEVATED_VIBRATION_WARNING"

        record = {
            "timestamp": timestamp,
            "fundamental_torque": fundamental_torque,
            "thd": thd,
            "status": status
        }
        self.harmonic_history.append(record)
        if len(self.harmonic_history) > 1000:
            self.harmonic_history.pop(0)

        return record

    def get_aggregate_telemetry(self) -> Dict[str, Any]:
        """Summarizes recent harmonic performance."""
        if not self.harmonic_history:
            return {"mill_id": self.mill_id, "avg_thd": 0.0, "anomalies": 0}
        
        thds = [r["thd"] for r in self.harmonic_history]
        return {
            "mill_id": self.mill_id,
            "avg_thd": statistics.mean(thds),
            "max_thd": max(thds),
            "total_anomalies": self.anomaly_count,
            "samples_analyzed": len(self.harmonic_history)
        }

if __name__ == "__main__":
    sentinel = RollerMillHarmonicSentinel(mill_id="MILL-NAIROBI-EAST-01")
    now = time.time()
    # Simulate normal and anomalous runs
    for i in range(10):
        res = sentinel.ingest_torque_spectrum(
            timestamp=now + i,
            fundamental_torque=150.0,
            harmonic_amplitudes=[10.0, 5.0, 2.0]
        )
    print("Nominal check:", res)
    
    # Anomalous spike
    res_anomaly = sentinel.ingest_torque_spectrum(
        timestamp=now + 11,
        fundamental_torque=140.0,
        harmonic_amplitudes=[60.0, 45.0, 30.0]
    )
    print("Anomaly check:", res_anomaly)
    print("Aggregate Telemetry:", sentinel.get_aggregate_telemetry())
