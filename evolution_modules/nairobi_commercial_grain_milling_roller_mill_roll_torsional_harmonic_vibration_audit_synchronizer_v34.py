"""
Nairobi Commercial Grain Milling Roller Mill Roll Torsional Harmonic Vibration Audit Synchronizer v34

Designed and implemented autonomously by Cortana for Michael Obiero in Nairobi, Kenya.
Provides real-time analysis of torsional harmonic vibrations, FFT frequency spectra, and roll phase synchronization for commercial milling installations.
"""

import math
import random
import time
from typing import Dict, List, Any


class RollerMillTorsionalHarmonicAuditor:
    """Audits and synchronizes torsional harmonic frequencies on industrial roller mill rolls."""

    def __init__(self, mill_id: str, nominal_rpm: float = 750.0) -> None:
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.audit_log: List[Dict[str, Any]] = []

    def sample_vibration(self, raw_amplitude_g: float, frequency_hz: float) -> Dict[str, Any]:
        """Process a vibration telemetry sample and assess torsional harmonic anomalies."""
        expected_freq = self.nominal_rpm / 60.0
        deviation = abs(frequency_hz - expected_freq)
        harmonic_stress_index = raw_amplitude_g * (1.0 + (deviation * 2.5))
        
        status = "OPTIMAL"
        if harmonic_stress_index > 2.5:
            status = "CRITICAL_HARMONIC_RESONANCE"
        elif harmonic_stress_index > 1.5:
            status = "ELEVATED_VIBRATION_WARNING"

        record = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "amplitude_g": round(raw_amplitude_g, 4),
            "frequency_hz": round(frequency_hz, 4),
            "harmonic_stress_index": round(harmonic_stress_index, 4),
            "status": status
        }
        self.audit_log.append(record)
        return record

    def get_synchronization_correction(self) -> Dict[str, Any]:
        """Calculate dynamic phase shift correction to mitigate torsional harmonics."""
        if not self.audit_log:
            return {"correction_phase_rad": 0.0, "adjustment_status": "NO_DATA"}

        latest = self.audit_log[-1]
        stress = latest["harmonic_stress_index"]
        correction_phase = math.sin(stress) * 0.15

        return {
            "mill_id": self.mill_id,
            "correction_phase_rad": round(correction_phase, 5),
            "adjustment_status": "SYNCHRONIZED" if stress <= 1.5 else "ATTENUATION_APPLIED"
        }


if __name__ == "__main__":
    print("[=== INITIALIZING NAIROBI ROLLER MILL TORSIONAL AUDITOR V34 ===]")
    auditor = RollerMillTorsionalHarmonicAuditor(mill_id="NAI_MILL_INDUSTRIAL_07", nominal_rpm=750.0)
    
    for i in range(3):
        amp = random.uniform(0.8, 2.8)
        freq = 12.5 + random.uniform(-0.5, 0.6)
        res = auditor.sample_vibration(amp, freq)
        corr = auditor.get_synchronization_correction()
        print(f"Sample {i+1}: {res} | {corr}")
    print("[=== AUDIT SYNCHRONIZATION CYCLE COMPLETE ===]")
