"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Deflection Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import logging
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueDeflectionSentinel")

class RollerMillTorqueDeflectionSentinel:
    """
    Monitors dynamic torque deflection vectors across commercial grain milling roller
    mill drives in Nairobi industrial zones, detecting micro-slip and torsional resonance.
    """
    def __init__(self, mill_id: str, nominal_torque_nm: float = 450.0, threshold_deflection_pct: float = 4.5):
        self.mill_id = mill_id
        self.nominal_torque_nm = nominal_torque_nm
        self.threshold_deflection_pct = threshold_deflection_pct
        self.deflection_history: List[float] = []
        self.anomaly_count = 0
        logger.info(f"Initialized RollerMillTorqueDeflectionSentinel for mill: {mill_id}")

    def ingest_torque_telemetry(self, current_torque_nm: float, rpm: float) -> Dict[str, Any]:
        """
        Ingests live torque and rotational speed telemetry to calculate deflection variance.
        """
        timestamp = time.time()
        torque_delta = current_torque_nm - self.nominal_torque_nm
        deflection_pct = (abs(torque_delta) / self.nominal_torque_nm) * 100.0
        
        self.deflection_history.append(deflection_pct)
        if len(self.deflection_history > 100):
            self.deflection_history.pop(0)
            
        status = "NOMINAL"
        action_required = False
        
        if deflection_pct > self.threshold_deflection_pct:
            self.anomaly_count += 1
            status = "DEFLECTION_WARNING"
            action_required = True
            logger.warning(f"[{self.mill_id}] High Torque Deflection Detected: {deflection_pct:.2f}% (RPM: {rpm})")
            
        return {
            "mill_id": self.mill_id,
            "timestamp": timestamp,
            "current_torque_nm": current_torque_nm,
            "deflection_pct": deflection_pct,
            "rpm": rpm,
            "status": status,
            "action_required": action_required,
            "anomaly_count": self.anomaly_count
        }

    def get_diagnostic_report(self) -> Dict[str, Any]:
        avg_deflection = sum(self.deflection_history) / max(1, len(self.deflection_history))
        return {
            "mill_id": self.mill_id,
            "average_deflection_pct": avg_deflection,
            "total_anomalies": self.anomaly_count,
            "system_health": "OPTIMAL" if self.anomaly_count < 3 else "NEEDS_MAINTENANCE"
        }

if __name__ == "__main__":
    sentinel = RollerMillTorqueDeflectionSentinel(mill_id="NAI_UNGA_MILL_04")
    # Simulate normal and anomalous telemetry
    telemetry_samples = [
        (452.0, 1500.0),
        (455.5, 1498.0),
        (478.2, 1450.0), # Potential anomaly
        (451.0, 1500.0)
    ]
    for torque, rpm in telemetry_samples:
        result = sentinel.ingest_torque_telemetry(torque, rpm)
        print(result)
    print(sentinel.get_diagnostic_report())
