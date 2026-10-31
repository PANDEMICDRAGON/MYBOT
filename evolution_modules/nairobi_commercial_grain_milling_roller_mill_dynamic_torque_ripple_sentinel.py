"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Sentinel

Monitor high-frequency torque ripple harmonics on commercial roller mill drives
in Nairobi's milling plants to predict shaft fatigue, coupling wear, and gear degradation.
"""

import logging
import time
import random
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillDynamicTorqueRippleSentinel")

class RollerMillDynamicTorqueRippleSentinel:
    def __init__(self, mill_id: str, rated_torque_nm: float = 450.0, ripple_threshold_pct: float = 8.5):
        self.mill_id = mill_id
        self.rated_torque_nm = rated_torque_nm
        self.ripple_threshold_pct = ripple_threshold_pct
        self.anomaly_count = 0
        logger.info(f"Initialized Dynamic Torque Ripple Sentinel for Roller Mill {self.mill_id} (Rated: {self.rated_torque_nm} Nm)")

    def analyze_torque_waveform(self, torque_samples: List[float]) -> Dict[str, Any]:
        if not torque_samples:
            return {"status": "ERROR", "message": "Empty torque sample set"}
        
        mean_torque = sum(torque_samples) / len(torque_samples)
        peak_torque = max(torque_samples)
        min_torque = min(torque_samples)
        peak_to_peak = peak_torque - min_torque
        
        # Ripple percentage calculation
        ripple_pct = (peak_to_peak / mean_torque) * 100.0 if mean_torque > 0 else 0.0
        
        status = "OPTIMAL"
        if ripple_pct > self.ripple_threshold_pct:
            status = "WARNING"
            self.anomaly_count += 1
            logger.warning(f"[{self.mill_id}] High Torque Ripple Detected! Ripple: {ripple_pct:.2f}% (Threshold: {self.ripple_threshold_pct}%)")
        else:
            logger.info(f"[{self.mill_id}] Torque ripple nominal: {ripple_pct:.2f}%")

        return {
            "mill_id": self.mill_id,
            "mean_torque_nm": round(mean_torque, 2),
            "peak_to_peak_nm": round(peak_to_peak, 2),
            "ripple_percentage": round(ripple_pct, 2),
            "status": status,
            "anomaly_count": self.anomaly_count,
            "timestamp": time.time()
        }

if __name__ == "__main__":
    sentinel = RollerMillDynamicTorqueRippleSentinel(mill_id="RM-NAIROBI-WEST-04")
    # Simulate normal and anomalous torque waveform captures
    normal_samples = [440.0 + random.uniform(-15, 15) for _ in range(100)]
    result_normal = sentinel.analyze_torque_waveform(normal_samples)
    print("Normal Test Result:", result_normal)

    anomalous_samples = [450.0 + random.uniform(-60, 65) for _ in range(100)]
    result_anomaly = sentinel.analyze_torque_waveform(anomalous_samples)
    print("Anomalous Test Result:", result_anomaly)
