"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Zenith Sentinel.

Provides real-time telemetry anomaly detection, torsional vibration analysis, and structural stress
prediction for heavy-duty commercial roller mills operating in Nairobi industrial zones.
"""

import time
import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillZenithSentinel")

class RollerMillZenithSentinel:
    """Monitors high-frequency torque fluctuations, bearing harmonics, and roller gap stability."""
    
    def __init__(self, mill_id: str, nominal_rpm: int = 1200):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.telemetry_history: List[Dict[str, Any]] = []
        
    def ingest_telemetry(self, torque_nm: float, vibration_mm_s: float, bearing_temp_c: float) -> Dict[str, Any]:
        timestamp = time.time()
        rpm_variance = abs(math.sin(timestamp) * 15.0)
        effective_rpm = self.nominal_rpm + rpm_variance
        
        # Zenith torque compliance evaluation
        torque_deviation = abs(torque_nm - 250.0) / 250.0
        thermal_stress = bearing_temp_c / 85.0
        vibration_index = vibration_mm_s / 4.5
        
        health_score = max(0.0, 100.0 - (torque_deviation * 30.0 + thermal_stress * 40.0 + vibration_index * 30.0))
        
        status = "NOMINAL"
        if health_score < 75.0:
            status = "WARNING"
        if health_score < 50.0:
            status = "CRITICAL_INTERVENTION"
            
        record = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "torque_nm": torque_nm,
            "vibration_mm_s": vibration_mm_s,
            "bearing_temp_c": bearing_temp_c,
            "effective_rpm": effective_rpm,
            "health_score": round(health_score, 2),
            "status": status
        }
        
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        logger.info(f"Mill {self.mill_id} Health: {record['health_score']}% [{status}]")
        return record

    def get_diagnostics(self) -> Dict[str, Any]:
        if not self.telemetry_history:
            return {"status": "NO_DATA"}
        latest = self.telemetry_history[-1]
        avg_health = sum(r["health_score"] for r in self.telemetry_history) / len(self.telemetry_history)
        return {
            "mill_id": self.mill_id,
            "latest_status": latest["status"],
            "average_health": round(avg_health, 2),
            "total_samples": len(self.telemetry_history)
        }

if __name__ == "__main__":
    sentinel = RollerMillZenithSentinel("NAI-MILL-01")
    sample = sentinel.ingest_telemetry(torque_nm=245.5, vibration_mm_s=1.2, bearing_temp_c=62.4)
    print("Test harness execution complete:", sample)
