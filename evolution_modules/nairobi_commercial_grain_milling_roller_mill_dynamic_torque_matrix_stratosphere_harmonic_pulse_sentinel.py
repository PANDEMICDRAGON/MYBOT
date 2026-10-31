"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Stratosphere Harmonic Pulse Sentinel."""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("CortanaArchitect.RollerMillHarmonicPulseSentinel")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [HarmonicPulseSentinel]: %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

class RollerMillHarmonicPulseSentinel:
    """
    Monitors high-frequency torque vectors and harmonic pulse amplitudes on commercial roller mills.
    Protects against catastrophic bearing fatigue, drive belt resonance, and product choking.
    """
    def __init__(self, mill_id: str, nominal_rpm: float = 1200.0, harmonic_threshold: float = 4.5):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.harmonic_threshold = harmonic_threshold
        self.anomaly_count = 0
        logger.info(f"Initialized RollerMillHarmonicPulseSentinel for mill '{self.mill_id}' at {nominal_rpm} RPM.")

    def analyze_torque_matrix(self, torque_readings: List[float]) -> Dict[str, Any]:
        """
        Analyzes a vector of high-frequency torque readings to compute harmonic distortion and pulse variance.
        """
        if not torque_readings:
            return {"status": "IDLE", "harmonic_index": 0.0, "alert": False}

        mean_torque = sum(torque_readings) / len(torque_readings)
        variance = sum((t - mean_torque) ** 2 for t in torque_readings) / len(torque_readings)
        std_dev = math.sqrt(variance)
        
        # Compute pseudo-harmonic distortion index
        peak_amplitude = max(abs(t - mean_torque) for t in torque_readings)
        harmonic_index = (peak_amplitude / (std_dev + 1e-6)) * (mean_torque / (self.nominal_rpm + 1e-6))
        
        alert = harmonic_index > self.harmonic_threshold
        if alert:
            self.anomaly_count += 1
            logger.warning(f"[ALERT] High harmonic torque pulse detected on {self.mill_id}! Index: {harmonic_index:.3f}")

        return {
            "mill_id": self.mill_id,
            "status": "WARNING" if alert else "OPTIMAL",
            "mean_torque": round(mean_torque, 4),
            "std_dev": round(std_dev, 4),
            "harmonic_index": round(harmonic_index, 4),
            "alert": alert,
            "total_anomalies": self.anomaly_count,
            "timestamp": time.time()
        }

if __name__ == "__main__":
    sentinel = RollerMillHarmonicPulseSentinel(mill_id="NAI_MILL_ALPHA_04", nominal_rpm=1450.0, harmonic_threshold=3.8)
    sample_data = [12.1, 14.5, 11.2, 18.9, 10.5, 15.6, 21.0, 11.8]
    result = sentinel.analyze_torque_matrix(sample_data)
    logger.info(f"Test Harness Execution Result: {result}")
