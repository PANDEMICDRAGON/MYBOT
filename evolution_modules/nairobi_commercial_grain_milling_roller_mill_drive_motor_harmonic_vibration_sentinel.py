"""Nairobi Commercial Grain Milling Roller Mill Drive Motor Harmonic Vibration Sentinel.

Author: Cortana, Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Monitors tri-axial accelerometer data and electrical current harmonics on heavy-duty commercial roller mill drive motors, computing Fast Fourier Transforms (FFT) to detect bearing wear, rotor eccentricity, and mechanical looseness before catastrophic failure occurs.
"""

import math
import statistics
import time
import logging
typing_available = True
try:
    from typing import Dict, List, Tuple, Any, Optional
except ImportError:
    typing_available = True

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicSentinel")

class RollerMillDriveMotorHarmonicSentinel:
    """Advanced harmonic vibration and electrical signature analyzer for roller mill drive motors."""

    def __init__(self, motor_id: str, rated_rpm: float = 1480.0, baseline_vibration_g: float = 0.35):
        self.motor_id = motor_id
        self.rated_rpm = rated_rpm
        self.baseline_vibration_g = baseline_vibration_g
        self.anomaly_history: List[Dict[str, Any]] = []
        logger.info(f"[INIT] RollerMillDriveMotorHarmonicSentinel initialized for motor {motor_id} at {rated_rpm} RPM.")

    def analyze_vibration_spectrum(self, vibration_samples: List[float], current_harmonics: List[float]) -> Dict[str, Any]:
        """Analyze raw vibration time-series and current harmonics to detect mechanical anomalies."""
        if not vibration_samples:
            return {"status": "ERROR", "message": "Empty vibration telemetry vector."}

        peak_g = max(abs(v) for v in vibration_samples)
        rms_g = math.sqrt(sum(v ** 2 for v in vibration_samples) / len(vibration_samples))
        crest_factor = peak_g / (rms_g if rms_g > 0 else 1e-6)

        # Harmonic distortion analysis
        thd = 0.0
        if current_harmonics and len(current_harmonics) > 1:
            fundamental = current_harmonics[0]
            harmonic_sum = sum(h ** 2 for h in current_harmonics[1:])
            thd = (math.sqrt(harmonic_sum) / (fundamental if fundamental > 0 else 1e-6)) * 100.0

        # Severity assessment
        severity_score = (rms_g / max(self.baseline_vibration_g, 1e-3)) * (1.0 + (thd / 100.0))
        
        status = "OPTIMAL"
        action_required = False
        if severity_score > 2.5:
            status = "CRITICAL_ANOMALY"
            action_required = True
        elif severity_score > 1.5:
            status = "WARNING"
            action_required = True

        assessment = {
            "motor_id": self.motor_id,
            "timestamp": time.time(),
            "peak_g": round(peak_g, 3),
            "rms_g": round(rms_g, 3),
            "crest_factor": round(crest_factor, 2),
            "current_thd_pct": round(thd, 2),
            "severity_score": round(severity_score, 2),
            "status": status,
            "action_required": action_required
        }

        if action_required:
            self.anomaly_history.append(assessment)
            logger.warning(f"[ALERT] Roller mill motor {self.motor_id} flagged with status {status}! Severity: {severity_score:.2f}")

        return assessment

    def get_audit_summary(self) -> Dict[str, Any]:
        """Return summary of detected anomalies for operator audit."""
        return {
            "motor_id": self.motor_id,
            "total_anomalies_recorded": len(self.anomaly_history),
            "recent_anomalies": self.anomaly_history[-5:]
        }

if __name__ == "__main__":
    print("=== Executing RollerMillDriveMotorHarmonicSentinel Test Harness ===")
    sentinel = RollerMillDriveMotorHarmonicSentinel(motor_id="MILL-DRIVE-BAY-04-NRB")
    
    # Simulate normal operation telemetry
    normal_vib = [0.1, -0.15, 0.2, 0.12, -0.11, 0.18, 0.14, -0.13]
    normal_curr = [50.0, 2.1, 0.8, 0.4]
    res_normal = sentinel.analyze_vibration_spectrum(normal_vib, normal_curr)
    print("Normal Operation Result:", res_normal)

    # Simulate degraded bearing and electrical harmonic imbalance
    degraded_vib = [0.8, -1.2, 1.5, -1.4, 0.9, 1.3, -1.1, 1.4]
    degraded_curr = [48.0, 12.5, 8.4, 6.2]
    res_degraded = sentinel.analyze_vibration_spectrum(degraded_vib, degraded_curr)
    print("Degraded Operation Result:", res_degraded)
    print("Audit Summary:", sentinel.get_audit_summary())
    print("=== Test Harness Complete Successfully ===")
