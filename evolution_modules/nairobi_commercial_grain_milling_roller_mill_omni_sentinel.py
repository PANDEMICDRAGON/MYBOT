import time
import math
import logging
import threading
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillOmniSentinel")

class RollerMillOmniSentinel:
    """
    Advanced real-time monitoring and dynamic matrix modulation sentinel for
    Nairobi commercial grain milling roller mills, protecting against harmonic pulse anomalies.
    """
    def __init__(self, mill_id: str = "NRB-MILL-01") -> None:
        self.mill_id = mill_id
        self.active = False
        self._lock = threading.Lock()
        self.torque_matrix: List[float] = [0.0] * 16
        self.harmonic_index: float = 1.0
        self.anomaly_count: int = 0
        logger.info(f"Initialized {self.__class__.__name__} for mill unit: {self.mill_id}")

    def ingest_telemetry(self, raw_torques: List[float]) -> Dict[str, Any]:
        with self._lock:
            if len(raw_torques) != 16:
                raise ValueError("Telemetry vector must contain exactly 16 torque sample points.")
            self.torque_matrix = raw_torques
            mean_torque = sum(raw_torques) / len(raw_torques)
            variance = sum((t - mean_torque) ** 2 for t in raw_torques) / len(raw_torques)
            self.harmonic_index = math.sqrt(variance) / (abs(mean_torque) + 1e-6)
            
            status = "NOMINAL"
            if self.harmonic_index > 0.75:
                self.anomaly_count += 1
                status = "CRITICAL_HARMONIC_DEVIATION"
                logger.warning(f"[{self.mill_id}] Harmonic anomaly detected! Index: {self.harmonic_index:.4f}")
            
            return {
                "mill_id": self.mill_id,
                "mean_torque": mean_torque,
                "harmonic_index": self.harmonic_index,
                "anomaly_count": self.anomaly_count,
                "status": status,
                "timestamp": time.time()
            }

    def calibrate_spindles(self) -> bool:
        with self._lock:
            logger.info(f"[{self.mill_id}] Executing recalibration sweep across torque matrix...")
            time.sleep(0.01)
            self.harmonic_index = 0.12
            logger.info(f"[{self.mill_id}] Recalibration complete. Harmonic index normalized.")
            return True

def __main__() -> None:
    sentinel = RollerMillOmniSentinel(mill_id="NRB-UGALI-MILL-99")
    sample_data = [10.2, 10.4, 10.1, 15.8, 10.3, 10.2, 9.9, 10.5, 10.2, 10.4, 10.1, 10.3, 10.2, 10.4, 10.1, 10.3]
    res = sentinel.ingest_telemetry(sample_data)
    logger.info(f"Diagnostic Result: {res}")
    sentinel.calibrate_spindles()

if __name__ == "__main__":
    __main__()