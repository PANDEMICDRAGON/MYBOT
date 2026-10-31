import time
import math
import random
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('RollerMillTorquePulseSentinel')

class RollerMillTorquePulseSentinel:
    """
    Monitors high-frequency torque pulses on commercial roller mills in Nairobi grain facilities.
    Detects anomalous torque spikes, calculates impulse integrals, and triggers pneumatic
    feed choke isolation or inverter braking to prevent catastrophic shaft shear.
    """
    def __init__(self, mill_id: str, baseline_torque_nm: float = 250.0, pulse_threshold_nm: float = 380.0):
        self.mill_id = mill_id
        self.baseline_torque_nm = baseline_torque_nm
        self.pulse_threshold_nm = pulse_threshold_nm
        self.pulse_history: List[Dict[str, Any]] = []
        self.interlock_active = False
        logger.info(f"RollerMillTorquePulseSentinel initialized for mill {mill_id} with baseline {baseline_torque_nm} Nm.")

    def ingest_torque_reading(self, current_torque_nm: float, timestamp: Optional[float] = None) -> Dict[str, Any]:
        ts = timestamp or time.time()
        deviation = current_torque_nm - self.baseline_torque_nm
        is_pulse = current_torque_nm >= self.pulse_threshold_nm
        
        reading = {
            "timestamp": ts,
            "torque_nm": current_torque_nm,
            "deviation": deviation,
            "is_pulse": is_pulse
        }
        
        self.pulse_history.append(reading)
        if len(self.pulse_history) > 1000:
            self.pulse_history.pop(0)
            
        status = "NOMINAL"
        if is_pulse:
            status = "CRITICAL_PULSE_DETECTED"
            self.trigger_protective_interlock(current_torque_nm)
            
        return {
            "mill_id": self.mill_id,
            "status": status,
            "reading": reading,
            "interlock_active": self.interlock_active
        }

    def trigger_protective_interlock(self, torque_nm: float) -> None:
        self.interlock_active = True
        logger.warning(f"[EMERGENCY] Torque pulse of {torque_nm} Nm detected on {self.mill_id}! Engaging pneumatic feed gate isolation.")

    def reset_interlock(self) -> None:
        self.interlock_active = False
        logger.info(f"Interlock reset for mill {self.mill_id}. Resuming normal feeding cycle.")

    def compute_pulse_metrics(self) -> Dict[str, float]:
        if not self.pulse_history:
            return {"max_torque": 0.0, "pulse_count": 0, "avg_torque": 0.0}
        torques = [r["torque_nm"] for r in self.pulse_history]
        pulses = sum(1 for r in self.pulse_history if r["is_pulse"])
        return {
            "max_torque": max(torques),
            "pulse_count": float(pulses),
            "avg_torque": sum(torques) / len(torques)
        }

if __name__ == "__main__":
    sentinel = RollerMillTorquePulseSentinel(mill_id="NAI-MILL-04")
    
    # Simulate normal and spike telemetry
    test_torques = [245.0, 252.0, 260.0, 395.0, 410.0, 255.0, 248.0]
    for t in test_torques:
        result = sentinel.ingest_torque_reading(t)
        logger.info(f"Telemetry Result: {result}")
        time.sleep(0.05)
        
    metrics = sentinel.compute_pulse_metrics()
    logger.info(f"Final Pulse Metrics: {metrics}")
