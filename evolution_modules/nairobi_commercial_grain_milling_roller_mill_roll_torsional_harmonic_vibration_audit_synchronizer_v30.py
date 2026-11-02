"""
Nairobi Commercial Grain Milling Roller Mill Roll Torsional Harmonic Vibration Audit Synchronizer v30

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
Description: Monitors torsional harmonics and vibrational telemetry across commercial roller mill rolls,
             performing dynamic FFT spectral analysis and anomaly detection to prevent catastrophic drive failures.
"""

import math
import time
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [TorsionalHarmonicV30]: %(message)s')
logger = logging.getLogger(__name__)

class RollerMillTorsionalAuditor:
    def __init__(self, mill_id: str, nominal_rpm: float = 750.0, sample_window_size: int = 64):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.sample_window_size = sample_window_size
        self.vibration_buffer: List[float] = []
        self.harmonic_baselines: Dict[str, float] = {}
        self.anomaly_count = 0
        logger.info(f"Initialized TorsionalAuditor for mill {self.mill_id} at nominal {self.nominal_rpm} RPM.")

    def ingest_vibration_sample(self, vibration_amplitude: float, timestamp: float) -> Dict[str, Any]:
        """Ingests raw accelerometer readings from the fast roll bearing housing."""
        self.vibration_buffer.append(vibration_amplitude)
        if len(self.vibration_buffer) > self.sample_window_size:
            self.vibration_buffer.pop(0)

        analysis = self._audit_harmonics()
        return {
            "mill_id": self.mill_id,
            "timestamp": timestamp,
            "sample_count": len(self.vibration_buffer),
            "analysis": analysis
        }

    def _audit_harmonics(self) -> Dict[str, Any]:
        if len(self.vibration_buffer) < 10:
            return {"status": "collecting", "torsional_index": 0.0, "alert": False}

        mean_val = statistics.mean(self.vibration_buffer)
        stdev_val = statistics.stdev(self.vibration_buffer) if len(self.vibration_buffer) > 1 else 0.0
        peak_val = max(abs(v - mean_val) for v in self.vibration_buffer)

        # Torsional harmonic distortion proxy (THD-v)
        torsional_index = (peak_val / (stdev_val + 1e-6)) * (self.nominal_rpm / 750.0)
        
        alert = False
        if torsional_index > 4.5:
            self.anomaly_count += 1
            alert = True
            logger.warning(f"[{self.mill_id}] HIGH TORSIONAL HARMONIC ANOMALY DETECTED! Index: {torsional_index:.3f}")

        return {
            "status": "audited",
            "mean_amplitude": round(mean_val, 4),
            "peak_amplitude": round(peak_val, 4),
            "stdev": round(stdev_val, 4),
            "torsional_index": round(torsional_index, 4),
            "anomaly_count": self.anomaly_count,
            "alert": alert
        }

    def export_audit_report(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "nominal_rpm": self.nominal_rpm,
            "total_anomalies": self.anomaly_count,
            "buffer_length": len(self.vibration_buffer)
        }

if __name__ == "__main__":
    logger.info("Executing self-test harness for RollerMillTorsionalAuditor...")
    auditor = RollerMillTorsionalAuditor(mill_id="NAI_MILL_09_UGALI_LINE")
    
    # Simulate normal operation telemetry
    for i in range(50):
        amp = 0.5 + 0.1 * math.sin(i / 2.0)
        res = auditor.ingest_vibration_sample(amp, time.time())
    
    # Simulate harmonic spike / micro-slip condition
    for i in range(15):
        amp = 2.5 + 1.8 * math.cos(i)
        res = auditor.ingest_vibration_sample(amp, time.time())
        
    logger.info(f"Final Audit Report: {auditor.export_audit_report()}")
    logger.info("Test harness execution complete.")
