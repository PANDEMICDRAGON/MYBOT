import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorquePulseSentinel")

class RollerMillTorquePulseSentinel:
    """
    Monitors high-resolution dynamic torque pulse signatures in commercial roller mills
    across Nairobi grain processing facilities, safeguarding heavy milling machinery.
    """
    
    def __init__(self, mill_id: str, pulse_threshold_nm: float = 450.0, sample_window_size: int = 50):
        self.mill_id = mill_id
        self.pulse_threshold_nm = pulse_threshold_nm
        self.sample_window_size = sample_window_size
        self._torque_history: List[float] = []
        self._anomaly_count = 0

    def ingest_torque_reading(self, torque_nm: float, timestamp: Optional[float] = None) -> Dict[str, Any]:
        """
        Ingests a high-frequency torque reading, calculates moving differentials,
        and identifies transient torque pulses.
        """
        ts = timestamp or time.time()
        self._torque_history.append(torque_nm)
        
        if len(self._torque_history) > self.sample_window_size:
            self._torque_history.pop(0)
            
        pulse_delta = 0.0
        is_pulse_anomaly = False
        
        if len(self._torque_history) >= 2:
            pulse_delta = abs(self._torque_history[-1] - self._torque_history[-2])
            if pulse_delta > self.pulse_threshold_nm:
                self._anomaly_count += 1
                is_pulse_anomaly = True
                logger.warning(
                    f"[ALERT] Roller Mill {self.mill_id}: Torque pulse anomaly detected! "
                    f"Delta: {pulse_delta:.2f} Nm (Threshold: {self.pulse_threshold_nm} Nm)"
                )
                
        return {
            "mill_id": self.mill_id,
            "timestamp": ts,
            "current_torque_nm": torque_nm,
            "pulse_delta_nm": pulse_delta,
            "is_anomaly": is_pulse_anomaly,
            "total_anomalies": self._anomaly_count
        }

    def evaluate_health_index(self) -> Dict[str, Any]:
        """
        Evaluates the overall mechanical health index of the roller mill drive train.
        """
        if not self._torque_history:
            return {"health_score": 100.0, "status": "NO_DATA"}
            
        mean_torque = sum(self._torque_history) / len(self._torque_history)
        variance = sum((x - mean_torque) ** 2 for x in self._torque_history) / len(self._torque_history)
        std_dev = math.sqrt(variance)
        
        # Penalty based on anomaly frequency and variance
        penalty = min(50.0, (self._anomaly_count * 5.0) + (std_dev * 0.1))
        health_score = max(0.0, 100.0 - penalty)
        
        status = "OPTIMAL"
        if health_score < 75.0:
            status = "DEGRADED"
        if health_score < 40.0:
            status = "CRITICAL"
            
        return {
            "mill_id": self.mill_id,
            "health_score": round(health_score, 2),
            "mean_torque_nm": round(mean_torque, 2),
            "torque_std_dev": round(std_dev, 2),
            "anomaly_count": self._anomaly_count,
            "status": status
        }

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Pulse Sentinel...")
    sentinel = RollerMillTorquePulseSentinel(mill_id="NAI-MILL-ALPHA-04")
    
    # Simulate normal and spike telemetry
    test_readings = [210.5, 215.0, 212.1, 680.0, 214.3, 211.0, 750.2, 213.8]
    for val in test_readings:
        result = sentinel.ingest_torque_reading(val)
        print(f"Telemetry: {result}")
        
    health = sentinel.evaluate_health_index()
    print(f"Final Health Evaluation: {health}")
    print("Roller Mill Dynamic Torque Pulse Sentinel test execution completed successfully.")
