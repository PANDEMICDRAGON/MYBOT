"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Harmonic Amplification Coefficient Deviation Sentinel."""

import time
import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicDeviationSentinel")

class RollerMillHarmonicDeviationSentinel:
    """Monitors high-frequency torque harmonic amplification coefficient deviations on industrial roller mills."""

    def __init__(self, baseline_coefficient: float = 1.25, threshold: float = 0.15):
        self.baseline_coefficient = baseline_coefficient
        self.threshold = threshold
        self.anomaly_count = 0

    def analyze_coefficient(self, current_coefficient: float) -> Dict[str, Any]:
        deviation = abs(current_coefficient - self.baseline_coefficient)
        status = "NORMAL"
        if deviation > self.threshold:
            status = "CRITICAL_DEVIATION"
            self.anomaly_count += 1
            logger.warning(f"[SENTINEL ALERT] Harmonic amplification coefficient deviation detected: {current_coefficient} (Delta: {deviation:.4f})")
        else:
            logger.info(f"[SENTINEL OK] Harmonic amplification coefficient stable: {current_coefficient}")

        return {
            "timestamp": time.time(),
            "current_coefficient": current_coefficient,
            "baseline_coefficient": self.baseline_coefficient,
            "deviation": deviation,
            "status": status,
            "total_anomalies": self.anomaly_count
        }

if __name__ == "__main__":
    sentinel = RollerMillHarmonicDeviationSentinel()
    sample_readings = [1.26, 1.28, 1.48, 1.24, 1.55]
    for reading in sample_readings:
        res = sentinel.analyze_coefficient(reading)
        print(res)
        time.sleep(0.05)
