import logging
import time
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueResonanceSentinel")

class RollerMillTorqueResonanceSentinel:
    """
    Monitors dynamic torque resonance signatures on commercial grain milling roller mills,
    detecting micro-oscillations and structural harmonic stress before mechanical seizure.
    """
    def __init__(self, mill_id: str, sample_rate_hz: float = 100.0, resonance_threshold_nm: float = 450.0):
        self.mill_id = mill_id
        self.sample_rate_hz = sample_rate_hz
        self.resonance_threshold_nm = resonance_threshold_nm
        self.torque_buffer: List[float] = []
        self.max_buffer_size = 500
        self.status = "NORMAL"
        self.trip_count = 0

    def ingest_torque_reading(self, torque_nm: float) -> Dict[str, Any]:
        """
        Ingests a real-time torque reading in Newton-meters (Nm), updates buffer,
        and evaluates resonant anomalies.
        """
        self.torque_buffer.append(torque_nm)
        if len(self.torque_buffer) > self.max_buffer_size:
            self.torque_buffer.pop(0)

        anomaly_detected = False
        variance = 0.0
        mean_val = 0.0

        if len(self.torque_buffer) >= 10:
            mean_val = statistics.mean(self.torque_buffer)
            variance = statistics.variance(self.torque_buffer)
            if abs(torque_nm - mean_val) > self.resonance_threshold_nm or variance > (self.resonance_threshold_nm * 0.5):
                anomaly_detected = True
                self.status = "TRIPPED_RESONANCE_ANOMALY"
                self.trip_count += 1
                logger.warning(f"[!] MILL {self.mill_id} RESONANCE SPIKE DETECTED: Torque={torque_nm}Nm, Mean={mean_val:.2f}Nm, Var={variance:.2f}")
            else:
                self.status = "NORMAL"

        return {
            "mill_id": self.mill_id,
            "current_torque_nm": torque_nm,
            "mean_torque_nm": round(mean_val, 2),
            "torque_variance": round(variance, 2),
            "status": self.status,
            "anomaly_detected": anomaly_detected,
            "trip_count": self.trip_count,
            "timestamp": time.time()
        }

    def reset_sentinel(self) -> None:
        """Resets sentinel status after operator inspection."""
        self.status = "NORMAL"
        self.torque_buffer.clear()
        logger.info(f"[+] Mill {self.mill_id} dynamic torque resonance sentinel reset to NORMAL.")

if __name__ == "__main__":
    sentinel = RollerMillTorqueResonanceSentinel(mill_id="NAIROBI_MILL_04_UGALI_LINE")
    # Simulate normal operation
    for t in [120.5, 122.1, 119.8, 121.0, 120.2]:
        res = sentinel.ingest_torque_reading(t)
        print(res)
    # Simulate resonant anomaly spike
    spike_res = sentinel.ingest_torque_reading(750.0)
    print(spike_res)
    assert spike_res["anomaly_detected"] is True
    print("RollerMillTorqueResonanceSentinel verification test passed successfully.")
