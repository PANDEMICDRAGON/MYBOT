"""Nairobi Commercial Grain Milling Roller Gap Micrometer Synapse Harmonic Pulse Correlation Vibration Audit Synchronizer V11"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerGapSynchV11")


class RollerGapHarmonicSynchronizerV11:
    """
    Monitors and synchronizes high-precision roller gap micrometer adjustments
    with real-time vibration harmonic telemetry in commercial grain mills.
    """
    def __init__(self, mill_id: str, nominal_gap_microns: float = 250.0):
        self.mill_id = mill_id
        self.nominal_gap = nominal_gap_microns
        self.thermal_coefficient = 0.012  # microns per degree C
        self.baseline_harmonic_hz = 120.0
        self.audit_log: List[Dict[str, Any]] = []

    def compute_thermal_correction(self, ambient_temp_c: float, running_hours: float) -> float:
        """Calculates gap offset needed due to roller thermal expansion."""
        temp_rise = (ambient_temp_c - 22.0) + (running_hours * 0.7)
        correction = temp_rise * self.thermal_coefficient
        return round(correction, 4)

    def analyze_vibration_pulse(self, raw_vibration_hz: float, peak_amplitude: float) -> Dict[str, Any]:
        """Correlates vibration harmonic spikes with mechanical bearing wear or misaligned gap."""
        deviation = abs(raw_vibration_hz - self.baseline_harmonic_hz)
        harmonic_stress_index = deviation * peak_amplitude

        status = "OPTIMAL"
        if harmonic_stress_index > 50.0:
            status = "WARNING_HIGH_HARMONIC_STRESS"
        elif harmonic_stress_index > 100.0:
            status = "CRITICAL_MISALIGNMENT_DETECTED"

        audit_entry = {
            "timestamp": time.time(),
            "vibration_hz": raw_vibration_hz,
            "amplitude": peak_amplitude,
            "stress_index": harmonic_stress_index,
            "status": status
        }
        self.audit_log.append(audit_entry)
        return audit_entry

    def synchronize_gap(self, ambient_temp: float, hours: float, vibration_hz: float, amp: float) -> Dict[str, Any]:
        """Executes full synchronization cycle."""
        thermal_offset = self.compute_thermal_correction(ambient_temp, hours)
        audit = self.analyze_vibration_pulse(vibration_hz, amp)

        target_gap = self.nominal_gap - thermal_offset
        if audit["status"] == "CRITICAL_MISALIGNMENT_DETECTED":
            target_gap += 5.0  # Safe retraction

        result = {
            "mill_id": self.mill_id,
            "adjusted_gap_microns": round(target_gap, 2),
            "thermal_offset_microns": thermal_offset,
            "vibration_audit": audit
        }
        logger.info(f"Mill {self.mill_id} Synchronized Gap: {result['adjusted_gap_microns']} um | Status: {audit['status']}")
        return result


if __name__ == "__main__":
    sync_engine = RollerGapHarmonicSynchronizerV11(mill_id="NAI-MILL-04")
    test_result = sync_engine.synchronize_gap(ambient_temp=28.5, hours=6.0, vibration_hz=124.2, amp=0.85)
    print(test_result)
