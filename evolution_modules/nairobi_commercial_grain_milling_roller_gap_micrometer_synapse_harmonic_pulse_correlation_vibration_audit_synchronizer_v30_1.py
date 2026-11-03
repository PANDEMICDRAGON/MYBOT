"""
Module: nairobi_commercial_grain_milling_roller_gap_micrometer_synapse_harmonic_pulse_correlation_vibration_audit_synchronizer_v30_1.py
Description: High-precision harmonic pulse correlation and vibration audit synchronizer for commercial roller mills in Nairobi.
"""

import math
import statistics
import time
from typing import Dict, List, Optional, Tuple


class RollerGapMicrometerSynapseSynchronizer:
    """Synchronizes roller gap micrometers with harmonic vibration pulses in grain milling operations."""

    def __init__(self, mill_id: str, nominal_gap_mm: float = 0.5):
        self.mill_id = mill_id
        self.nominal_gap_mm = nominal_gap_mm
        self.audit_log: List[Dict[str, float]] = []

    def correlate_harmonics(self, vibration_amplitudes: List[float], current_gap_mm: float) -> Dict[str, float]:
        """Correlates vibration harmonic frequencies with current gap tolerances."""
        if not vibration_amplitudes:
            return {"correlation_score": 0.0, "stability_index": 1.0, "adjustment_delta": 0.0}

        mean_amp = statistics.mean(vibration_amplitudes)
        stdev_amp = statistics.stdev(vibration_amplitudes) if len(vibration_amplitudes) > 1 else 0.0
        
        gap_deviation = current_gap_mm - self.nominal_gap_mm
        correlation_score = max(0.0, 1.0 - (abs(gap_deviation) * 2.0) - (stdev_amp / (mean_amp + 1e-6)))
        stability_index = max(0.0, min(1.0, 1.0 - (stdev_amp / 10.0)))
        adjustment_delta = -gap_deviation * 0.1  # damped feedback

        audit_entry = {
            "timestamp": time.time(),
            "current_gap": current_gap_mm,
            "correlation_score": correlation_score,
            "stability_index": stability_index,
            "adjustment_delta": adjustment_delta
        }
        self.audit_log.append(audit_entry)
        return audit_entry

    def get_audit_summary(self) -> Dict[str, float]:
        """Summarizes recent synchronization audits."""
        if not self.audit_log:
            return {"avg_correlation": 0.0, "avg_stability": 0.0}
        
        avg_corr = statistics.mean([entry["correlation_score"] for entry in self.audit_log])
        avg_stab = statistics.mean([entry["stability_index"] for entry in self.audit_log])
        return {"avg_correlation": avg_corr, "avg_stability": avg_stab}


if __name__ == "__main__":
    syncer = RollerGapMicrometerSynapseSynchronizer(mill_id="NAI_MILL_04", nominal_gap_mm=0.45)
    test_vibrations = [1.2, 1.3, 1.25, 1.22, 1.28]
    result = syncer.correlate_harmonics(test_vibrations, current_gap_mm=0.47)
    print(f"[SYNAPSE V30.1] Audit Result for {syncer.mill_id}: {result}")
    summary = syncer.get_audit_summary()
    print(f"[SYNAPSE V30.1] Summary: {summary}")
