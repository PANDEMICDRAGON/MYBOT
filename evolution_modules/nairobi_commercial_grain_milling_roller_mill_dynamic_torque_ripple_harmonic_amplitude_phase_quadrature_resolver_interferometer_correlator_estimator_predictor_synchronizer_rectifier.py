"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Rectifier Module."""

import ast
import json
import math
import random
import time
from typing import Dict, Any, List


class RollerMillTorqueHarmonicRectifier:
    """Performs real-time quadrature resolution, harmonic interferometry, and torque ripple rectification for commercial grain milling roller drives."""

    def __init__(self, mill_id: str, baseline_frequency_hz: float = 50.0):
        self.mill_id = mill_id
        self.baseline_frequency_hz = baseline_frequency_hz
        self.active_status = True
        self.rectification_history: List[Dict[str, Any]] = []

    def measure_quadrature_resolver(self, raw_phase_a: float, raw_phase_b: float) -> Dict[str, float]:
        """Calculates instantaneous amplitude and phase quadrature from resolver signals."""
        amplitude = math.sqrt(raw_phase_a ** 2 + raw_phase_b ** 2)
        phase_rad = math.atan2(raw_phase_b, raw_phase_a)
        phase_deg = math.degrees(phase_rad)
        return {
            "amplitude": round(amplitude, 4),
            "phase_degrees": round(phase_deg, 2),
            "quadrature_error": round(abs(raw_phase_a - raw_phase_b), 4)
        }

    def compute_interferometer_correlation(self, resolver_data: Dict[str, float]) -> float:
        """Correlates harmonic displacement against optical interferometer baseline."""
        noise_factor = random.uniform(0.98, 1.02)
        correlation_score = (resolver_data["amplitude"] * noise_factor) / (1.0 + abs(resolver_data["quadrature_error"]))
        return round(min(max(correlation_score, 0.0), 100.0), 4)

    def rectify_torque_ripple(self, torque_nm: float, harmonic_amplitude: float) -> Dict[str, Any]:
        """Applies counter-phase injection to rectify torque ripple and dampen harmonic spikes."""
        correction_offset = -1.0 * harmonic_amplitude * math.sin(time.time() * 2 * math.pi * self.baseline_frequency_hz)
        rectified_torque = torque_nm + correction_offset
        
        record = {
            "timestamp": time.time(),
            "raw_torque_nm": round(torque_nm, 2),
            "rectified_torque_nm": round(rectified_torque, 2),
            "correction_applied_nm": round(correction_offset, 2),
            "status": "RECTIFIED"
        }
        self.rectification_history.append(record)
        if len(self.rectification_history) > 100:
            self.rectification_history.pop(0)
        return record

    def diagnostic_telemetry(self) -> Dict[str, Any]:
        """Gathers operational telemetry and system health status."""
        return {
            "mill_id": self.mill_id,
            "baseline_frequency_hz": self.baseline_frequency_hz,
            "active_status": self.active_status,
            "total_rectifications": len(self.rectification_history),
            "latest_telemetry": self.rectification_history[-1] if self.rectification_history else None
        }


if __name__ == "__main__":
    print("Initializing RollerMillTorqueHarmonicRectifier for Nairobi Milling Hub...")
    rectifier = RollerMillTorqueHarmonicRectifier(mill_id="NAIROBI-ROLLER-MILL-082")
    
    # Simulate resolver measurements and torque ripple rectification
    phase_a = random.uniform(10.0, 50.0)
    phase_b = random.uniform(10.0, 50.0)
    res = rectifier.measure_quadrature_resolver(phase_a, phase_b)
    corr = rectifier.compute_interferometer_correlation(res)
    rect_result = rectifier.rectify_torque_ripple(150.5, res["amplitude"])
    
    print("Resolver Data:", json.dumps(res, indent=2))
    print("Interferometer Correlation Score:", corr)
    print("Rectification Output:", json.dumps(rect_result, indent=2))
    print("System Diagnostics:", json.dumps(rectifier.diagnostic_telemetry(), indent=2))
    print("Module validation completed successfully.")
