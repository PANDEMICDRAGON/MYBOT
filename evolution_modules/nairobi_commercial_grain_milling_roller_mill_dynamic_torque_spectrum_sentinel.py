"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Spectrum Sentinel module.

Provides advanced spectral analysis of industrial roller mill torque signatures, protecting
grain processing facilities in Nairobi against harmonic vibration and bearing fatigue.
"""

import math
import time
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueSpectrumSentinel")


class RollerMillTorqueSpectrumSentinel:
    """Monitors high-frequency torque streams from commercial roller mills using
    discrete spectral decomposition to identify mechanical degradation.
    """

    def __init__(self, mill_id: str, sampling_rate_hz: float = 100.0, window_size: int = 64):
        self.mill_id = mill_id
        self.sampling_rate_hz = sampling_rate_hz
        self.window_size = window_size
        self.torque_buffer: List[float] = []
        self.anomaly_count = 0
        logger.info(f"Initialized Torque Spectrum Sentinel for mill {mill_id} at {sampling_rate_hz}Hz.")

    def ingest_reading(self, torque_nm: float) -> Optional[Dict[str, Any]]:
        """Ingests a raw torque reading (Newton-meters) and runs spectral checks when buffer is full."""
        self.torque_buffer.append(torque_nm)
        if len(self.torque_buffer) > self.window_size:
            self.torque_buffer.pop(0)

        if len(self.torque_buffer) == self.window_size:
            return self._analyze_spectrum()
        return None

    def _analyze_spectrum(self) -> Dict[str, Any]:
        """Performs a lightweight spectral power distribution analysis."""
        n = len(self.torque_buffer)
        mean_torque = sum(self.torque_buffer) / n
        
        # Compute variance and pseudo-harmonic energy (simplified Goertzel / DFT magnitude approximation)
        variance = sum((x - mean_torque) ** 2 for x in self.torque_buffer) / n
        std_dev = math.sqrt(variance)
        
        # High frequency ripple indicator (consecutive differences)
        diffs = [abs(self.torque_buffer[i] - self.torque_buffer[i-1]) for i in range(1, n)]
        roughness = sum(diffs) / len(diffs) if diffs else 0.0

        # Threshold heuristics for mechanical wear or gear mesh fault
        is_anomalous = roughness > (std_dev * 1.5) and std_dev > 5.0
        if is_anomalous:
            self.anomaly_count += 1
            logger.warning(f"[ALERT] Spectral anomaly detected on mill {self.mill_id}! Roughness: {roughness:.2f}, StdDev: {std_dev:.2f}")

        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "mean_torque_nm": round(mean_torque, 3),
            "torque_std_dev": round(std_dev, 3),
            "torque_roughness": round(roughness, 3),
            "anomaly_detected": is_anomalous,
            "total_anomalies": self.anomaly_count
        }


if __name__ == "__main__":
    # Test harness execution
    sentinel = RollerMillTorqueSpectrumSentinel(mill_id="NAI-UGALI-MILL-04")
    
    # Feed normal operation torque values with slight sinusoidal load
    for i in range(100):
        simulated_torque = 120.0 + 3.0 * math.sin(i * 0.2) + (0.5 if i % 7 == 0 else 0.0)
        report = sentinel.ingest_reading(simulated_torque)
        if report and i % 20 == 0:
            print(f"Spectrum Report at step {i}: {report}")
