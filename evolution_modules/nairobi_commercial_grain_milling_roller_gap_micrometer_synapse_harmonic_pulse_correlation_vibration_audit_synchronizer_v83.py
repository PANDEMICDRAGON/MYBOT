"""
Nairobi Commercial Grain Milling Roller Gap Micrometer Synapse Harmonic Pulse Correlation Vibration Audit Synchronizer V83.1
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import math
import time
import statistics
from typing import Dict, List, Any, Optional


class RollerGapVibrationAuditSynchronizer:
    """
    Monitors roller mill gap settings, micro-vibrations, and harmonic pulse correlations
    to optimize grain milling output and protect heavy machinery in Nairobi processing plants.
    """

    def __init__(self, mill_id: str, nominal_gap_mm: float = 0.15):
        self.mill_id = mill_id
        self.nominal_gap_mm = nominal_gap_mm
        self.audit_log: List[Dict[str, Any]] = []
        self.status = "INITIALIZED"

    def analyze_pulse_correlation(self, vibration_amplitudes: List[float], measured_gaps: List[float]) -> Dict[str, Any]:
        """
        Correlates vibration harmonic pulses with roller gap variance.
        """
        if not vibration_amplitudes or not measured_gaps:
            return {"status": "ERROR", "message": "Empty telemetry stream."}

        mean_vibration = statistics.mean(vibration_amplitudes)
        stdev_vibration = statistics.stdev(vibration_amplitudes) if len(vibration_amplitudes) > 1 else 0.0
        mean_gap = statistics.mean(measured_gaps)
        gap_variance = statistics.variance(measured_gaps) if len(measured_gaps) > 1 else 0.0

        # Harmonic pulse correlation metric
        harmonic_index = mean_vibration * (1.0 + abs(mean_gap - self.nominal_gap_mm))
        
        anomaly_detected = stdev_vibration > 2.5 or gap_variance > 0.01 or harmonic_index > 5.0

        audit_record = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "mean_vibration": mean_vibration,
            "mean_gap": mean_gap,
            "harmonic_index": harmonic_index,
            "anomaly_detected": anomaly_detected
        }

        self.audit_log.append(audit_record)
        self.status = "ALERT" if anomaly_detected else "OPTIMAL"

        return {
            "mill_id": self.mill_id,
            "status": self.status,
            "harmonic_index": harmonic_index,
            "anomaly_detected": anomaly_detected,
            "recommendation": "CALIBRATE_GAP" if anomaly_detected else "CONTINUE_OPERATION"
        }


if __name__ == "__main__":
    synagogue = RollerGapVibrationAuditSynchronizer(mill_id="NAI_MILL_WESTLANDS_04")
    sample_vibrations = [1.2, 1.4, 1.3, 1.5, 4.8, 1.4]
    sample_gaps = [0.15, 0.15, 0.16, 0.14, 0.22, 0.15]
    result = synagogue.analyze_pulse_correlation(sample_vibrations, sample_gaps)
    print("[TEST HARNESS OUTPUT]", result)
