"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Band Sentinel

Monitors roller mill drive motor torque bands in real-time, detecting multi-band
frequency excursions that indicate uneven grain feeding, bearing binding, or
impending mechanical seizure in Nairobi milling operations.
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillDynamicTorqueBandSentinel")

class RollerMillDynamicTorqueBandSentinel:
    """
    Analyzes torque readings across multiple frequency bands to protect commercial
    roller mills against sudden mechanical resistance and asymmetrical roll loading.
    """
    def __init__(self, mill_id: str, nominal_torque_nm: float = 250.0, band_tolerance: float = 0.15):
        self.mill_id = mill_id
        self.nominal_torque_nm = nominal_torque_nm
        self.band_tolerance = band_tolerance
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillDynamicTorqueBandSentinel for Mill [{self.mill_id}]")

    def ingest_torque_bands(self, low_band_nm: float, mid_band_nm: float, high_band_nm: float) -> Dict[str, Any]:
        """
        Ingests low, mid, and high frequency torque band measurements.
        Returns an assessment dictionary with anomaly scores and mitigation triggers.
        """
        timestamp = time.time()
        total_torque = low_band_nm + mid_band_nm + high_band_nm
        
        # Evaluate deviations from nominal distribution
        low_dev = abs(low_band_nm - (self.nominal_torque_nm * 0.4)) / (self.nominal_torque_nm * 0.4)
        mid_dev = abs(mid_band_nm - (self.nominal_torque_nm * 0.4)) / (self.nominal_torque_nm * 0.4)
        high_dev = abs(high_band_nm - (self.nominal_torque_nm * 0.2)) / (self.nominal_torque_nm * 0.2)

        composite_anomaly_score = (low_dev + mid_dev + (high_dev * 1.5)) / 3.5
        
        status = "NORMAL"
        action_required = False
        if composite_anomaly_score > (self.band_tolerance * 2.0):
            status = "CRITICAL_EXCURSION"
            action_required = True
            logger.error(f"[{self.mill_id}] Critical torque band excursion detected! Score: {composite_anomaly_score:.3f}")
        elif composite_anomaly_score > self.band_tolerance:
            status = "WARNING"
            logger.warning(f"[{self.mill_id}] Elevated torque band variance. Score: {composite_anomaly_score:.3f}")

        record = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "low_band_nm": low_band_nm,
            "mid_band_nm": mid_band_nm,
            "high_band_nm": high_band_nm,
            "total_torque": total_torque,
            "anomaly_score": composite_anomaly_score,
            "status": status,
            "action_required": action_required
        }
        
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return record

    def generate_diagnostic_summary(self) -> Dict[str, Any]:
        """Summarizes recent telemetry and health metrics for operator dashboard."""
        if not self.telemetry_history:
            return {"status": "NO_DATA"}

        recent = self.telemetry_history[-1]
        return {
            "mill_id": self.mill_id,
            "last_status": recent["status"],
            "last_anomaly_score": recent["anomaly_score"],
            "total_samples_logged": len(self.telemetry_history)
        }

if __name__ == "__main__":
    sentinel = RollerMillDynamicTorqueBandSentinel(mill_id="NAI-MILL-04")
    # Simulate normal operation telemetry
    assessment = sentinel.ingest_torque_bands(100.2, 99.8, 50.1)
    print("Normal Operation Test:", assessment)
    
    # Simulate anomalous high frequency vibration/torque surge
    anomaly_assessment = sentinel.ingest_torque_bands(140.0, 130.0, 95.5)
    print("Anomalous Operation Test:", anomaly_assessment)
    
    print("Diagnostic Summary:", sentinel.generate_diagnostic_summary())
