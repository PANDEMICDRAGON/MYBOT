"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Dispersion Sentinel
Designed for real-time monitoring of torque dispersion variance in heavy industrial roller mills.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorqueDispersionSentinel")

class RollerMillTorqueDispersionSentinel:
    """
    Monitors, analyzes, and evaluates dynamic torque dispersion across roller mill drives
    to prevent catastrophic mechanical seizure or motor overload in Nairobi grain processing facilities.
    """
    
    def __init__(self, mill_id: str, dispersion_threshold: float = 14.5):
        self.mill_id = mill_id
        self.dispersion_threshold = dispersion_threshold
        self.telemetry_history: List[Dict[str, Any]] = []
        self.status = "STANDBY"

    def ingest_telemetry(self, torque_readings: List[float]) -> Dict[str, Any]:
        """
        Ingests an array of high-frequency torque samples (Nm) from dual roller mill rolls.
        Calculates statistical dispersion (variance and coefficient of variation).
        """
        if not torque_readings:
            raise ValueError("Empty torque telemetry received.")
            
        n = len(torque_readings)
        mean_torque = sum(torque_readings) / n
        variance = sum((x - mean_torque) ** 2 for x in torque_readings) / n
        std_dev = math.sqrt(variance)
        
        # Coefficient of variation as a percentage
        cv_dispersion = (std_dev / mean_torque * 100.0) if mean_torque > 0 else 0.0
        
        assessment = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "mean_torque_nm": round(mean_torque, 2),
            "torque_variance": round(variance, 4),
            "dispersion_index": round(cv_dispersion, 2),
            "anomaly_detected": cv_dispersion > self.dispersion_threshold
        }
        
        self.telemetry_history.append(assessment)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        self._evaluate_status(assessment)
        return assessment

    def _evaluate_status(self, assessment: Dict[str, Any]) -> None:
        if assessment["anomaly_detected"]:
            self.status = "ALERT_HIGH_DISPERSION"
            logger.warning(
                f"[ALERT] Mill {self.mill_id}: High torque dispersion detected! "
                f"Index: {assessment['dispersion_index']}% (Threshold: {self.dispersion_threshold}%). "
                f"Inspect roll alignment and belt tension immediately."
            )
        else:
            self.status = "OPTIMAL"
            logger.info(
                f"[OK] Mill {self.mill_id} running smoothly. "
                f"Dispersion Index: {assessment['dispersion_index']}%."
            )

    def get_operational_metrics(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "current_status": self.status,
            "total_samples_analyzed": len(self.telemetry_history),
            "threshold": self.dispersion_threshold
        }


if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Dispersion Sentinel...")
    sentinel = RollerMillTorqueDispersionSentinel(mill_id="NAI-MILL-IND-04")
    
    # Simulate normal and abnormal torque profiles
    for cycle in range(3):
        # Normal operation: tight clustering around 250 Nm
        normal_batch = [random.gauss(250.0, 3.5) for _ in range(50)]
        sentinel.ingest_telemetry(normal_batch)
        
    # Inject anomaly: erratic torque fluctuation (bearing slip / grain choke)
    anomaly_batch = [random.gauss(250.0, 45.0) for _ in range(50)]
    sentinel.ingest_telemetry(anomaly_batch)
    
    print(sentinel.get_operational_metrics())
