"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Viscosity Sentinel Module."""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(filename)s] - %(message)s')
logger = logging.getLogger("RollerMillTorqueViscositySentinel")

class TorqueViscositySentinel:
    """
    Monitors dynamic torque variations corresponding to ground product viscosity in commercial grain milling,
    detecting jamming, choke conditions, or raw grain inconsistency in Nairobi milling plants.
    """
    def __init__(self, mill_id: str, viscosity_threshold_pascal_sec: float = 4.5):
        self.mill_id = mill_id
        self.threshold = viscosity_threshold_pascal_sec
        self.history: List[Dict[str, Any]] = []
        logger.info(f"Initialized TorqueViscositySentinel for mill {self.mill_id} with threshold {self.threshold} Pa·s")

    def analyze_torque_stream(self, torque_nm: float, roller_rpm: float, grain_moisture_pct: float) -> Dict[str, Any]:
        """
        Computes apparent dynamic viscosity from torque and shear rate derived from roller RPM.
        """
        try:
            # Shear rate proportional to roller RPM
            shear_rate = max(0.1, roller_rpm * (2.0 * math.pi / 60.0))
            # Apparent viscosity approximation: eta = Tau / gamma_dot
            apparent_viscosity = torque_nm / shear_rate
            
            anomaly_detected = apparent_viscosity > self.threshold
            
            telemetry = {
                "timestamp": time.time(),
                "mill_id": self.mill_id,
                "torque_nm": torque_nm,
                "roller_rpm": roller_rpm,
                "grain_moisture_pct": grain_moisture_pct,
                "apparent_viscosity_pascal_sec": round(apparent_viscosity, 4),
                "anomaly_detected": anomaly_detected
            }
            
            self.history.append(telemetry)
            if len(self.history) > 1000:
                self.history.pop(0)
                
            if anomaly_detected:
                logger.warning(f"[{self.mill_id}] High viscosity anomaly detected! Viscosity: {telemetry['apparent_viscosity_pascal_sec']} Pa·s")
                
            return telemetry
        except Exception as e:
            logger.error(f"Error analyzing torque stream for {self.mill_id}: {e}")
            return {"error": str(	), "timestamp": time.time()}

    def get_audit_summary(self) -> Dict[str, Any]:
        total_readings = len(self.history)
        if total_readings == 0:
            return {"total_readings": 0, "anomaly_count": 0}
        anomalies = [h for h in self.history if h.get("anomaly_detected", False)]
        return {
            "mill_id": self.mill_id,
            "total_readings": total_readings,
            "anomaly_count": len(anomalies),
            "average_viscosity": round(sum(h.get("apparent_viscosity_pascal_sec", 0.0) for h in self.history) / total_readings, 4)
        }

if __name__ == "__main__":
    sentinel = TorqueViscositySentinel(mill_id="NRB-MILL-042")
    for _ in range(5):
        simulated_torque = random.uniform(80.0, 160.0)
        simulated_rpm = random.uniform(500.0, 750.0)
        simulated_moisture = random.uniform(12.5, 15.0)
        result = sentinel.analyze_torque_stream(simulated_torque, simulated_rpm, simulated_moisture)
        print(result)
        time.sleep(0.1)
    print("Audit Summary:", sentinel.get_audit_summary())
