"""
Nairobi Commercial Grain Milling Roller Gap Micrometer Synapse Harmonic Pulse Correlation Vibration Audit Synchronizer V39.1

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

This module provides high-precision telemetry auditing, harmonic pulse correlation, and 
real-time micrometer gap synchronization for commercial roller mills across Nairobi.
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerGapAuditorV39_1")


class RollerGapAuditor:
    def __init__(self, mill_id: str, nominal_gap_microns: float = 250.0):
        self.mill_id = mill_id
        self.nominal_gap_microns = nominal_gap_microns
        self.vibration_history: List[float] = []
        self.gap_history: List[float] = []
        logger.info(f"Initialized RollerGapAuditor for Mill {self.mill_id} with nominal gap {nominal_gap_microns}um.")

    def audit_cycle(self, current_gap: float, vibration_amplitude: float) -> Dict[str, Any]:
        self.gap_history.append(current_gap)
        self.vibration_history.append(vibration_amplitude)
        
        gap_delta = current_gap - self.nominal_gap_microns
        harmonic_pulse_score = self._compute_harmonic_correlation(vibration_amplitude)
        
        status = "OPTIMAL"
        if abs(gap_delta) > 15.0 or harmonic_pulse_score < 0.75:
            status = "RECALIBRATION_REQUIRED"
        
        audit_result = {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "current_gap_microns": current_gap,
            "gap_delta": gap_delta,
            "vibration_amplitude": vibration_amplitude,
            "harmonic_pulse_score": harmonic_pulse_score,
            "status": status
        }
        logger.info(f"Audit completed for {self.mill_id}: status={status}, score={harmonic_pulse_score:.3f}")
        return audit_result

    def _compute_harmonic_correlation(self, vibration: float) -> float:
        if not self.vibration_history:
            return 1.0
        mean_vib = sum(self.vibration_history) / len(self.vibration_history)
        if mean_vib == 0:
            return 1.0
        deviation = abs(vibration - mean_vib) / mean_vib
        score = max(0.0, 1.0 - deviation)
        return float(score)


if __name__ == "__main__":
    auditor = RollerGapAuditor(mill_id="NAI_CBD_MILL_04", nominal_gap_microns=200.0)
    sample_data = [
        (201.2, 0.05),
        (205.5, 0.12),
        (220.1, 0.45),  # Triggers recalibration threshold
        (199.8, 0.04)
    ]
    for gap, vib in sample_data:
        result = auditor.audit_cycle(gap, vib)
        print(result)
