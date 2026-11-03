"""
Nairobi Commercial Grain Milling Roller Gap Micrometer Synapse Harmonic Pulse Correlation Vibration Audit Synchronizer V55.1

Designed for real-time telemetry analysis of commercial roller mills in Nairobi, Kenya.
Provides high-frequency vibration spectrum auditing, gap micrometer synchronization, and
predictive anomaly detection to protect milling machinery and optimize flour consistency.
"""

import os
import sys
import time
import math
import json
import logging
import threading
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerGapHarmonicSynchronizerV551")

class RollerGapHarmonicSynchronizer:
    """
    Core engine for correlating roller gap micrometer drift with harmonic vibration signatures
    in commercial grain milling machinery across Nairobi industrial zones.
    """
    def __init__(self, mill_id: str = "NAI_MILL_055", nominal_gap_microns: float = 120.0):
        self.mill_id = mill_id
        self.nominal_gap_microns = nominal_gap_microns
        self._lock = threading.Lock()
        self.running = False
        self.audit_log: List[Dict[str, Any]] = []
        logger.info(f"Initialized {self.__class__.__name__} for mill {self.mill_id} with nominal gap {self.nominal_gap_microns}um")

    def acquire_telemetry_sample(self, vibration_hz: float, current_gap_microns: float, motor_load_amps: float) -> Dict[str, Any]:
        """
        Acquires a real-time sensor sample and calculates harmonic pulse correlation metrics.
        """
        with self._lock:
            gap_delta = current_gap_microns - self.nominal_gap_microns
            # Calculate harmonic energy index based on vibration frequency deviation and gap delta
            harmonic_energy = abs(vibration_hz * 0.75) + (abs(gap_delta) * 1.45)
            anomaly_detected = harmonic_energy > 85.0 or abs(gap_delta) > 15.0

            sample = {
                "timestamp": time.time(),
                "mill_id": self.mill_id,
                "vibration_hz": vibration_hz,
                "current_gap_microns": current_gap_microns,
                "gap_delta": gap_delta,
                "motor_load_amps": motor_load_amps,
                "harmonic_energy": round(harmonic_energy, 2),
                "anomaly_detected": anomaly_detected
            }
            self.audit_log.append(sample)
            if len(self.audit_log) > 1000:
                self.audit_log.pop(0)
            return sample

    def run_diagnostic_audit(self) -> Dict[str, Any]:
        """
        Runs a comprehensive diagnostic audit across recent telemetry samples.
        """
        with self._lock:
            if not self.audit_log:
                return {"status": "IDLE", "message": "No telemetry samples available for audit."}
            
            recent = self.audit_log[-50:]
            anomalies = [s for s in recent if s["anomaly_detected"]]
            avg_harmonic = sum(s["harmonic_energy"] for s in recent) / len(recent)

            status = "CRITICAL_ATTENTION_REQUIRED" if len(anomalies) > 5 else "OPTIMAL"
            if status == "CRITICAL_ATTENTION_REQUIRED":
                logger.warning(f"[{self.mill_id}] Harmonic anomaly threshold breached! Anomalies in last window: {len(anomalies)}")
            else:
                logger.info(f"[{self.mill_id}] Diagnostic audit passed. Avg Harmonic Energy: {avg_harmonic:.2f}")

            return {
                "mill_id": self.mill_id,
                "status": status,
                "samples_analyzed": len(recent),
                "anomaly_count": len(anomalies),
                "average_harmonic_energy": round(avg_harmonic, 2)
            }

if __name__ == "__main__":
    print("Executing __main__ test harness for RollerGapHarmonicSynchronizer V55.1...")
    synchronizer = RollerGapHarmonicSynchronizer(mill_id="NAI_CBD_MILL_01", nominal_gap_microns=110.0)
    
    # Simulate telemetry feeds
    test_readings = [
        (45.2, 110.5, 34.2),
        (46.0, 111.0, 35.0),
        (88.5, 130.2, 52.8),  # anomaly spike
        (45.5, 110.2, 34.5)
    ]

    for vib, gap, load in test_readings:
        res = synchronizer.acquire_telemetry_sample(vib, gap, load)
        print(f"Sample captured: {json.dumps(res, indent=2)}")

    audit_result = synchronizer.run_diagnostic_audit()
    print(f"Audit Result: {json.dumps(audit_result, indent=2)}")
    print("RollerGapHarmonicSynchronizer V55.1 test completed successfully.")
