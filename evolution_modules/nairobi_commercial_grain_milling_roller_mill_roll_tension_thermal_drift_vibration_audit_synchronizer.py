"""
Nairobi Commercial Grain Milling Roller Mill Roll Tension Thermal Drift Vibration Audit Synchronizer
Created for Michael Obiero in Nairobi, Kenya.
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillSynchronizer")

class RollerMillSynchronizer:
    """Synchronizes roll tension, thermal drift coefficients, and vibration harmonics for commercial mills."""
    
    def __init__(self, mill_id: str, nominal_gap_microns: float = 250.0):
        self.mill_id = mill_id
        self.nominal_gap_microns = nominal_gap_microns
        self.temperature_celsius = 25.0
        self.tension_kn = 45.0
        self.vibration_mm_s = 1.2
        self.audit_log: List[Dict[str, Any]] = []

    def update_telemetry(self, temp: float, tension: float, vibration: float) -> None:
        """Updates real-time sensor streams."""
        self.temperature_celsius = temp
        self.tension_kn = tension
        self.vibration_mm_s = vibration

    def compute_thermal_drift_compensation(self) -> float:
        """Calculates required gap compensation based on thermal expansion coefficient of cast iron rolls."""
        # Base expansion coefficient ~ 11 micrometers per meter per degree C
        delta_t = self.temperature_celsius - 25.0
        compensation_microns = delta_t * 0.35
        return compensation_microns

    def audit_sync_cycle(self) -> Dict[str, Any]:
        """Executes a full synchronization and audit check across all vectors."""
        thermal_comp = self.compute_thermal_drift_compensation()
        adjusted_gap = self.nominal_gap_microns - thermal_comp
        
        # Anomaly scoring
        vibration_anomaly = max(0.0, self.vibration_mm_s - 2.5)
        tension_variance = abs(self.tension_kn - 45.0)
        
        status = "OPTIMAL"
        if vibration_anomaly > 1.0 or tension_variance > 10.0:
            status = "WARNING_ALIGNMENT_REQUIRED"
        if vibration_anomaly > 3.0:
            status = "CRITICAL_STOP_RECOMMENDED"

        record = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "temperature": self.temperature_celsius,
            "tension_kn": self.tension_kn,
            "vibration_mm_s": self.vibration_mm_s,
            "thermal_compensation_microns": thermal_comp,
            "adjusted_gap_microns": adjusted_gap,
            "status": status
        }
        self.audit_log.append(record)
        return record

if __name__ == "__main__":
    logger.info("Initializing RollerMillSynchronizer test harness for Nairobi facility...")
    sync = RollerMillSynchronizer(mill_id="NAI_MILL_04", nominal_gap_microns=200.0)
    sync.update_telemetry(temp=38.5, tension=48.2, vibration=1.8)
    result = sync.audit_sync_cycle()
    logger.info(f"Audit Result: {result}")
    assert result["status"] in ["OPTIMAL", "WARNING_ALIGNMENT_REQUIRED"]
    logger.info("RollerMillSynchronizer validation test passed successfully.")
