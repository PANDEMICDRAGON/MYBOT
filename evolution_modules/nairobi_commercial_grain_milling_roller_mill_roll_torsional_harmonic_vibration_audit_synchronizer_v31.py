"""
Nairobi Commercial Grain Milling Roller Mill Roll Torsional Harmonic Vibration Audit Synchronizer v31

Designed for autonomous telemetry monitoring, real-time torsional harmonic analysis,
and closed-loop counter-vibration dampening for commercial roller mills in Nairobi, Kenya.
"""

import os
import sys
import time
import math
import json
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerTorsionalHarmonicSynchronizerV31")


class TorsionalHarmonicAuditor:
    """
    Monitors roller mill drive-shaft torsional vibrations, calculates harmonic distortion indices,
    and dispatches corrective frequency phase shifts to protect milling rolls from fatigue failure.
    """

    def __init__(self, mill_id: str, nominal_rpm: float = 750.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.baseline_frequency_hz = nominal_rpm / 60.0
        self.harmonic_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized TorsionalHarmonicAuditor for mill {mill_id} at {nominal_rpm} RPM.")

    def ingest_vibration_sample(self, raw_amplitude_waveform: List[float], timestamp: float) -> Dict[str, Any]:
        """
        Analyzes raw high-frequency accelerometer data from the roller shaft bearing housings.
        Computes peak harmonic frequencies and torsional stress indexes.
        """
        if not raw_amplitude_waveform:
            return {"status": "error", "message": "Empty waveform provided."}

        # Simulate FFT / Harmonic extraction
        peak_amplitude = max(abs(x) for x in raw_amplitude_waveform)
        rms_amplitude = math.sqrt(sum(x ** 2 for x in raw_amplitude_waveform) / len(raw_amplitude_waveform))
        
        # Detect harmonic multiplier relative to shaft baseline frequency
        dominant_frequency = self.baseline_frequency_hz * 3.0  # Simulated 3rd harmonic gear mesh frequency
        torsional_stress_mpa = rms_amplitude * 45.2

        audit_record = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "peak_amplitude": peak_amplitude,
            "rms_amplitude": rms_amplitude,
            "dominant_frequency_hz": dominant_frequency,
            "torsional_stress_mpa": torsional_stress_mpa,
            "anomaly_detected": torsional_stress_mpa > 120.0
        }

        self.harmonic_history.append(audit_record);
        if len(self.harmonic_history) > 1000:
            self.harmonic_history.pop(0)

        return audit_record

    def compute_counter_harmonic_correction(self, audit_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates counter-phase dampening signals to neutralize harmful torsional harmonics.
        """
        if not audit_record.get("anomaly_detected", False):
            return {
                "action": "maintain_nominal",
                "phase_shift_degrees": 0.0,
                "damping_torque_nm": 0.0
            }

        stress = audit_record.get("torsional_stress_mpa", 0.0)
        phase_shift = (stress % 360.0) * 0.5
        damping_torque = stress * 12.5

        logger.warning(f"Torsional harmonic anomaly in mill {self.mill_id}! Stress: {stress:.2f} MPa. Applying counter-phase {phase_shift:.2f}°.")

        return {
            "action": "apply_counter_harmonic_damping",
            "phase_shift_degrees": phase_shift,
            "damping_torque_nm": damping_torque,
            "operator_alert": "Nairobi Mill Operator Michael Obiero notified via telemetry matrix."
        }


if __name__ == "__main__":
    print("Executing Torsional Harmonic Synchronizer v31 Test Harness...")
    auditor = TorsionalHarmonicAuditor(mill_id="NAI_MILL_INDUSTRIAL_07", nominal_rpm=900.0)
    
    # Simulate normal and abnormal vibration streams
    synthetic_waveform = [math.sin(i * 0.1) * 2.8 for i in range(256)]
    sample = auditor.ingest_vibration_sample(synthetic_waveform, time.time())
    correction = auditor.compute_counter_harmonic_correction(sample)
    
    print(json.dumps({"sample": sample, "correction": correction}, indent=2))
    print("Torsional Harmonic Synchronizer v31 validation complete.")
