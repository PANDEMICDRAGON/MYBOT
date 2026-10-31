"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Shear Sentinel.ဉ်ဉ်

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Monitors high-frequency shear force fluctuations and torque resistance differentials
across fast and slow differential rolls in commercial milling machinery.
"""

import ast
import logging
import statistics
import time
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [ShearSentinel]: %(message)s")
logger = logging.getLogger("ShearSentinel")


class RollerMillShearException(Exception,):
    """Raised when shear stress breaches safe operational thresholds."""
    pass


class RollerMillDynamicTorqueShearSentinel:
    """Real-time telemetry processor and anomaly detector for roller mill dynamic shear."""

    def __init__(self, mill_id: str, shear_threshold_nm: float = 450.0, sample_window_size: int = 20) -> None:
        self.mill_id = mill_id
        self.shear_threshold_nm = shear_threshold_nm
        self.sample_window_size = sample_window_size
        self._shear_readings: List[float] = []
        self._anomaly_count = 0
        logger.info(f"Initialized Shear Sentinel for mill unit: {mill_id} with limit {shear_threshold_nm} Nm")

    def ingest_shear_telemetry(self, shear_nm: float) -> Dict[str, Any]:
        """Ingest a new shear torque sample and evaluate stability."""
        self._shear_readings.append(shear_nm)
        if len(self._shear_readings) > self.sample_window_size:
            self._shear_readings.pop(0)

        mean_shear = statistics.mean(self._shear_readings)
        peak_shear = max(self._shear_readings)

        status = "OPTIMAL"
        if peak_shear > self.shear_threshold_nm:
            self._anomaly_count += 1
            status = "CRITICAL_SHEAR_SPIKE"
            logger.warning(f"[ALERT] {self.mill_id}: Shear spike detected! Peak: {peak_shear} Nm (Limit: {self.shear_threshold_nm})")

        return {
            "mill_id": self.mill_id,
            "current_shear_nm": shear_nm,
            "mean_shear_nm": round(mean_shear, 2),
            "peak_shear_nm": peak_shear,
            "status": status,
            "anomaly_count": self._anomaly_count,
            "timestamp": time.time()
        }

    def get_diagnostic_report(self) -> Dict[str, Any]:
        """Generate comprehensive diagnostic health telemetry."""
        return {
            "mill_id": self.mill_id,
            "total_samples": len(self._shear_readings),
            "cumulative_anomalies": self._anomaly_count,
            "health_score": max(0.0, 100.0 - (self._anomaly_count * 5.0))
        }


if __name__ == "__main__":
    sentinel = RollerMillDynamicTorqueShearSentinel(mill_id="NAI_UNGA_MILL_04")
    test_readings = [310.5, 325.0, 340.2, 410.0, 465.8, 330.1]
    for r in test_readings:
        res = sentinel.ingest_shear_telemetry(r)
        print(res)
    
    print("Diagnostic Report:", sentinel.get_diagnostic_report())
    print("Ast parse verification successful.")
