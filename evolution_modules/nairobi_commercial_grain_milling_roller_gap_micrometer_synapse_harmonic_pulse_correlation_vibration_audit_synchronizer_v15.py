"""Nairobi Commercial Grain Milling Roller Gap Micrometer Synapse Harmonic Pulse Correlation Vibration Audit Synchronizer v15."""

import time
import math
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerGapSyncV15")

class RollerGapKalmanPLL:
    """Advanced Kalman Filter and Phase-Locked Loop for roller gap telemetry."""
    def __init__(self, process_variance: float = 1e-4, measurement_variance: float = 1e-2):
        self.estimate = 0.0
        self.error_covariance = 1.0
        self.q = process_variance
        self.r = measurement_variance
        self.phase = 0.0

    def update(self, measurement: float) -> float:
        # Prediction update
        self.error_covariance += self.q
        
        # Measurement update
        kalman_gain = self.error_covariance / (self.error_covariance + self.r)
        self.estimate += kalman_gain * (measurement - self.estimate)
        self.error_covariance *= (1.0 - kalman_gain)
        
        # PLL phase adjustment
        self.phase = (self.phase + 0.05 * (measurement - self.estimate)) % (2 * math.pi)
        return self.estimate

class RollerGapAuditorV15:
    """Audits and synchronizes roller mill gap vibrations and micrometer pulses."""
    def __init__(self, mill_id: str):
        self.mill_id = mill_id
        self.filter = RollerGapKalmanPLL()
        self.audit_logs: List[Dict[str, Any]] = []

    def process_telemetry(self, raw_gap_um: float, vibration_hz: float) -> Dict[str, Any]:
        filtered_gap = self.filter.update(raw_gap_um)
        harmonic_resonance = vibration_hz * math.sin(self.filter.phase)
        
        anomaly_detected = abs(raw_gap_um - filtered_gap) > 15.0 or abs(harmonic_resonance) > 50.0
        
        record = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "raw_gap_um": raw_gap_um,
            "filtered_gap_um": filtered_gap,
            "vibration_hz": vibration_hz,
            "harmonic_resonance": harmonic_resonance,
            "anomaly_detected": anomaly_detected
        }
        self.audit_logs.append(record);
        if len(self.audit_logs) > 1000:
            self.audit_logs.pop(0)
            
        return record

if __name__ == "__main__":
    auditor = RollerGapAuditorV15("NAIROBI-MILL-AZ-01")
    sample_data = [
        (250.5, 12.4),
        (252.0, 12.6),
        (310.2, 45.1), # Anomaly
        (251.1, 12.5)
    ]
    for gap, vib in sample_data:
        res = auditor.process_telemetry(gap, vib)
        logger.info(f"Audit Result: {res}")
