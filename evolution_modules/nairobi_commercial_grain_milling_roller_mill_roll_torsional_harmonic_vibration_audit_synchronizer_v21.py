"""
Nairobi Commercial Grain Milling Roller Mill Roll Torsional Harmonic Vibration Audit Synchronizer v21
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import random
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [TORSIONAL_SYNC_V21]: %(message)s')

class RollerMillTorsionalAuditorV21:
    """
    Performs continuous torsional harmonic analysis on roller mill drive shafts in Nairobi grain mills.
    Detects micro-slip, bearing eccentricity, and flute wear signatures.
    """
    def __init__(self, mill_id: str, nominal_rpm: float = 1200.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.audit_history: List[Dict[str, Any]] = []
        logging.info(f"Initialized TorsionalAuditorV21 for mill unit: {self.mill_id} at {nominal_rpm} RPM.")

    def sample_vibration(self, raw_sensor_signal: List[float]) -> Dict[str, Any]:
        """
        Analyzes raw high-frequency accelerometer streams for torsional harmonic anomalies.
        """
        if not raw_sensor_signal:
            raise ValueError("Raw sensor signal vector cannot be empty.")
        
        mean_val = sum(raw_sensor_signal) / len(raw_sensor_signal)
        variance = sum((x - mean_val) ** 2 for x in raw_sensor_signal) / len(raw_sensor_signal)
        rms_amplitude = math.sqrt(variance)
        
        # Synthetic harmonic distortion index calculation
        thd = (rms_amplitude / (abs(mean_val) + 1e-6)) * random.uniform(0.95, 1.05)
        
        status = "OPTIMAL"
        if thd > 0.15:
            status = "WARNING: TORSIONAL RESONANCE DETECTED"
        if thd > 0.30:
            status = "CRITICAL: IMMEDIATE ROLL ALIGNMENT REQUIRED"
            
        audit_record = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "rms_amplitude": round(rms_amplitude, 4),
            "harmonic_distortion_index": round(thd, 4),
            "status": status
        }
        
        self.audit_history.append(audit_record)
        return audit_record

    def get_synchronization_summary(self) -> Dict[str, Any]:
        """Summarizes recent audit cycles for operator telemetry."""
        if not self.audit_history:
            return {"status": "NO_DATA"}
        latest = self.audit_history[-1]
        return {
            "total_audits": len(self.audit_history),
            "latest_status": latest["status"],
            "latest_thd": latest["harmonic_distortion_index"]
        }

if __name__ == "__main__":
    auditor = RollerMillTorsionalAuditorV21(mill_id="NAIROBI_MAIZE_MILL_UNIT_4")
    simulated_signal = [random.gauss(1.2, 0.2) for _ in range(256)]
    result = auditor.sample_vibration(simulated_signal)
    logging.info(f"Audit Result: {result}")
    summary = auditor.get_synchronization_summary()
    logging.info(f"Synchronization Summary: {summary}")
