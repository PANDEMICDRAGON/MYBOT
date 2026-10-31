import time
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger('RollerMillTorqueStressSentinel')

class RollerMillTorqueStressSentinel:
    """
    Monitors high-frequency dynamic torque stress signatures on commercial grain milling roller mills,
    detecting micro-fractures, shaft misalignment, or bearing binding before failure occurs.
    """
    def __init__(self, mill_id: str, stress_threshold_nm: float = 1250.0, sample_window_size: int = 50):
        self.mill_id = mill_id
        self.stress_threshold_nm = stress_threshold_nm
        self.sample_window_size = sample_window_size
        self._stress_buffer: List[float] = []
        self._alert_count = 0

    def ingest_torque_reading(self, torque_nm: float, vibration_mm_s: float) -> Dict[str, Any]:
        """
        Ingests live torque (Nm) and vibration velocity (mm/s) metrics.
        Returns real-time analysis, anomaly flags, and stress health status.
        """
        self._stress_buffer.append(torque_nm)
        if len(self._stress_buffer) > self.sample_window_size:
            self._stress_buffer.pop(0)

        mean_stress = statistics.mean(self._stress_buffer)
        peak_stress = max(self._stress_buffer)
        stress_variance = statistics.variance(self._stress_buffer) if len(self._stress_buffer) > 1 else 0.0

        is_stressed = peak_stress > self.stress_threshold_nm or vibration_mm_s > 4.5
        status = "OPTIMAL"

        if is_stressed:
            self._alert_count += 1
            status = "WARNING_HIGH_TORSIONAL_STRESS"
            logger.warning(f"[{self.mill_id}] High torsional stress detected! Peak: {peak_stress:.2f} Nm, Vibration: {vibration_mm_s} mm/s")

        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "mean_stress_nm": round(mean_stress, 2),
            "peak_stress_nm": round(peak_stress, 2),
            "stress_variance": round(stress_variance, 4),
            "vibration_mm_s": vibration_mm_s,
            "status": status,
            "alert_count": self._alert_count
        }

    def reset_baseline(self) -> None:
        self._stress_buffer.clear()
        logger.info(f"[{self.mill_id}] Torsional stress baseline reset.")

if __name__ == "__main__":
    sentinel = RollerMillTorqueStressSentinel(mill_id="MILL_NAIROBI_INDUSTRIAL_01", stress_threshold_nm=1100.0)
    
    # Simulate normal operation
    for i in range(10):
        res = sentinel.ingest_torque_reading(torque_nm=950.0 + (i * 5), vibration_mm_s=1.2)
        logger.info(f"Test cycle {i}: {res['status']}")

    # Simulate stress event spike
    stress_spike = sentinel.ingest_torque_reading(torque_nm=1280.5, vibration_mm_s=5.1)
    logger.info(f"Spike test result: {stress_spike}")
