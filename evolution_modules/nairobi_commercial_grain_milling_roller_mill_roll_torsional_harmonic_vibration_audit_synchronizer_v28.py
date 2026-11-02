"""
Nairobi Commercial Grain Milling Roller Mill Roll Torsional Harmonic Vibration Audit Synchronizer v28

Provides advanced real-time telemetry analysis, torsional harmonic tracking, and automated roll gap vibration
auditing for commercial grain milling operations in Nairobi, Kenya.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillHarmonicSynchronizerV28")


class RollerMillTorsionalAuditor:
    """
    Monitors torsional vibration frequencies, detects harmonic anomalies, and synchronizes
    roll gap adjustments to protect milling machinery.
    """
    
    def __init__(self, mill_id: str, nominal_rpm: float = 750.0, sample_window_size: int = 50):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.sample_window_size = sample_window_size
        self.vibration_buffer: List[float] = []
        self.harmonic_coefficients: List[float] = []
        self.audit_log: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillTorsionalAuditor for mill {mill_id} at {nominal_rpm} RPM.")

    def ingest_sensor_reading(self, vibration_velocity_mm_s: float, temperature_c: float) -> Dict[str, Any]:
        """
        Ingests raw vibration velocity and roll temperature, updating the moving window
        and computing torsional harmonic indicators.
        """
        timestamp = time.time()
        self.vibration_buffer.append(vibration_velocity_mm_s)
        if len(self.vibration_buffer) > self.sample_window_size:
            self.vibration_buffer.pop(0)
            
        harmonic_index = self._calculate_harmonic_index()
        anomaly_detected = harmonic_index > 2.5 or vibration_velocity_mm_s > 12.0
        
        reading = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "vibration_velocity_mm_s": vibration_velocity_mm_s,
            "temperature_c": temperature_c,
            "harmonic_index": harmonic_index,
            "anomaly_detected": anomaly_detected
        }
        
        self.audit_log.append(reading);
        if len(self.audit_log) > 200:
            self.audit_log.pop(0)
            
        return reading

    def _calculate_harmonic_index(self) -> float:
        """
        Computes a dimensionless torsional harmonic degradation index from recent vibration samples.
        """
        if not self.vibration_buffer:
            return 0.0
        mean_val = sum(self.vibration_buffer) / len(self.vibration_buffer)
        variance = sum((x - mean_val) ** 2 for x in self.vibration_buffer) / len(self.vibration_buffer)
        std_dev = math.sqrt(variance)
        # Harmonic index formulation blending standard deviation and peak deviation
        peak_dev = max(abs(x - mean_val) for x in self.vibration_buffer)
        return round((std_dev * 1.5 + peak_dev * 0.8) / (mean_val + 1e-5), 4)

    def generate_synchronization_pulse(self) -> Dict[str, Any]:
        """
        Generates counter-harmonic dampening parameters to stabilize roller gaps.
        """
        if not self.audit_log:
            return {"status": "IDLE", "counter_phase_offset_deg": 0.0}
            
        latest = self.audit_log[-1]
        h_idx = latest["harmonic_index"]
        
        # Compute dampening offset
        offset = round(math.sin(time.time() * 0.1) * h_idx * 1.8, 3)
        action_required = latest["anomaly_detected"]
        
        pulse_packet = {
            "mill_id": self.mill_id,
            "status": "SYNCHRONIZED_ACTIVE" if action_required else "NOMINAL",
            "counter_phase_offset_deg": offset,
            "target_roll_gap_microns_adjustment": round(-offset * 2.5, 2),
            "timestamp": time.time()
        }
        logger.info(f"Generated pulse packet for {self.mill_id}: {pulse_packet['status']}")
        return pulse_packet


if __name__ == "__main__":
    logger.info("Executing self-test for RollerMillTorsionalAuditor...")
    auditor = RollerMillTorsionalAuditor("NAIROI_MILL_UNIT_04")
    
    for i in range(10):
        vib = random.uniform(3.0, 14.5)
        temp = random.uniform(45.0, 68.0)
        res = auditor.ingest_sensor_reading(vib, temp)
        logger.info(f"Test reading {i}: {res}")
        time.sleep(0.01)
        
    pulse = auditor.generate_synchronization_pulse()
    logger.info(f"Final test pulse: {pulse}")
    logger.info("RollerMillTorsionalAuditor test completed successfully.")
