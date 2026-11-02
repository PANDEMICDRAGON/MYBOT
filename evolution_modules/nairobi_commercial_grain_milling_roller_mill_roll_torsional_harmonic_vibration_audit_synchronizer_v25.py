"""
Nairobi Commercial Grain Milling Roller Mill Roll Torsional Harmonic Vibration Audit Synchronizer v25
Designed for Cortana's Autonomous Evolutionary Architect.

Provides real-time torsional harmonic resonance analysis and automated gap calibration audit 
for commercial roller mills operating in Nairobi, Kenya.
"""

import time
import math
import logging
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorsionalSynchronizerV25")

class RollerMillTorsionalSynchronizerV25:
    """
    Monitors roll torsional vibration signatures, calculates harmonic distortion factors,
    and synchronizes gap adjustments to prevent bearing wear and uneven flour granulation.
    """

    def __init__(self, mill_id: str, nominal_rpm: float = 750.0, tolerance_hz: float = 2.5):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.tolerance_hz = tolerance_hz
        self.audit_log: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillTorsionalSynchronizerV25 for Mill ID: {self.mill_id} at {self.nominal_rpm} RPM")

    def compute_harmonic_distortion(self, vibration_frequencies: List[float]) -> float:
        """
        Computes the Total Harmonic Distortion (THD) of torsional vibration spikes.
        """
        if not vibration_frequencies:
            return 0.0
        
        fundamental = self.nominal_rpm / 60.0
        harmonic_sum = sum(f**2 for f in vibration_frequencies if f > fundamental)
        base_val = sum(f**2 for f in vibration_frequencies) if vibration_frequencies else 1.0
        
        thd = math.sqrt(harmonic_sum) / (math.sqrt(base_val) + 1e-9)
        return float(thd)

    def audit_cycle(self, sensor_readings: List[float]) -> Dict[str, Any]:
        """
        Executes a single audit cycle over incoming vibration telemetry.
        """
        timestamp = time.time()
        thd = self.compute_harmonic_distortion(sensor_readings)
        
        status = "OPTIMAL"
        adjustment_micron = 0.0

        if thd > 0.15:
            status = "CRITICAL_HARMONIC_ANOMALY"
            adjustment_micron = -12.5
        elif thd > 0.08:
            status = "WARNING_ELEVATED_VIBRATION"
            adjustment_micron = -5.0

        audit_entry = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "thd": thd,
            "status": status,
            "recommended_gap_adjustment_micron": adjustment_micron
        }

        self.audit_log.append(audit_entry)
        logger.info(f"Audit complete for {self.mill_id}: THD={thd:.4f}, Status={status}")
        return audit_entry

    def get_latest_audit(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves the most recent audit entry.
        """
        return self.audit_log[-1] if self.audit_log else None

if __name__ == "__main__":
    synchronizer = RollerMillTorsionalSynchronizerV25(mill_id="NAIROBI-MILL-BLOCK-04")
    mock_readings = [12.5, 25.0, 50.0, 110.2, 12.8]
    result = synchronizer.audit_cycle(mock_readings)
    print("Test Execution Result:", result)
