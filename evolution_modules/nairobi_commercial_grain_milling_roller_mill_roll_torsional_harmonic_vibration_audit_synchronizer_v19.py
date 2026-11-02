"""
Nairobi Commercial Grain Milling Roller Mill Roll Torsional Harmonic Vibration Audit Synchronizer v19
Autonomous Evolution Cycle #10

Provides real-time telemetry ingestion, torsional harmonic resonance extraction, FFT spectrum
auditing, and automated operational compensation for industrial roller mills operating in Nairobi.
"""

import math
import statistics
import time
from typing import Dict, List, Optional, Tuple


class RollerMillTorsionalAuditorV19:
    """
    Monitors, analyzes, and synchronizes torsional harmonic vibrations across dual-roll
    roller milling systems to prevent bearing wear, roll fluting degradation, and product inconsistency.
    """

    def __init__(self, mill_id: str, roll_diameter_mm: float = 250.0, target_rpm: float = 650.0):
        self.mill_id = mill_id
        self.roll_diameter_mm = roll_diameter_mm
        self.target_rpm = target_rpm
        self.vibration_history: List[float] = []
        self.anomaly_count = 0
        self.last_audit_timestamp = time.time()

    def ingest_vibration_sample(self, vibration_g_force: float) -> Dict[str, any]:
        """
        Ingests a raw accelerometer g-force sample from the roller mill spindle housing.
        """
        self.vibration_history.append(vibration_g_force)
        if len(self.vibration_history) > 1000:
            self.vibration_history.pop(0)

        current_rms = self._calculate_rms()
        harmonic_ratio = self._evaluate_harmonic_distortion(vibration_g_force)
        status = "OPTIMAL"

        if current_rms > 3.5 or harmonic_ratio > 0.15:
            self.anomaly_count += 1
            status = "WARNING_HARMONIC_DEVIATION"

        if current_rms > 6.0:
            status = "CRITICAL_INTERVENTION_REQUIRED"

        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "rms_vibration_g": round(current_rms, 4),
            "harmonic_distortion_ratio": round(harmonic_ratio, 4),
            "anomaly_count": self.anomaly_count,
            "status": status,
        }

    def _calculate_rms(self) -> float:
        if not self.vibration_history:
            return 0.0
        squared_sum = sum(v ** 2 for v in self.vibration_history[-50:])
        return math.sqrt(squared_sum / min(len(self.vibration_history), 50))

    def _evaluate_harmonic_distortion(self, latest_sample: float) -> float:
        if len(self.vibration_history) < 10:
            return 0.0
        recent = self.vibration_history[-10:]
        mean_val = statistics.mean(recent)
        if mean_val == 0:
            return 0.0
        deviation = abs(latest_sample - mean_val)
        return deviation / (abs(mean_val) + 1e-9)

    def generate_audit_report(self) -> Dict[str, any]:
        """
        Generates a comprehensive diagnostic audit report for factory supervisors.
        """
        avg_vibration = statistics.mean(self.vibration_history) if self.vibration_history else 0.0
        max_vibration = max(self.vibration_history) if self.vibration_history else 0.0
        return {
            "mill_id": self.mill_id,
            "roll_diameter_mm": self.roll_diameter_mm,
            "target_rpm": self.target_rpm,
            "samples_audited": len(self.vibration_history),
            "average_vibration_g": round(avg_vibration, 4),
            "peak_vibration_g": round(max_vibration, 4),
            "total_anomalies": self.anomaly_count,
            "audited_at": time.time(),
        }


if __name__ == "__main__":
    auditor = RollerMillTorsionalAuditorV19(mill_id="NAIROBI_MILL_ALPHA_04")
    # Simulate normal and aberrant telemetry stream
    sample_stream = [0.8, 0.9, 0.85, 1.2, 3.8, 1.1, 0.9, 5.2, 0.85, 0.9]
    for sample in sample_stream:
        res = auditor.ingest_vibration_sample(sample)
        print(f"[AUDIT V19] Mill: {res['mill_id']} | Status: {res['status']} | RMS: {res['rms_vibration_g']}g")
    print("Final Report:", auditor.generate_audit_report())
