"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Investigator Module."""

import math
import statistics
import time
from typing import Dict, List, Any


class RollerMillTorqueInvestigator:
    """Investigates harmonic torque ripples and phase quadrature interference in industrial roller mills."""

    def __init__(self, mill_id: str, baseline_frequency_hz: float = 50.0):
        self.mill_id = mill_id
        self.baseline_frequency_hz = baseline_frequency_hz
        self.telemetry_history: List[Dict[str, float]] = []

    def ingest_resolver_data(self, torque_amplitude: float, phase_angle_deg: float, quadrature_error: float) -> Dict[str, Any]:
        timestamp = time.time()
        phase_rad = math.radians(phase_angle_deg)
        in_phase_component = torque_amplitude * math.cos(phase_rad)
        quadrature_component = torque_amplitude * math.sin(phase_rad)
        
        metric = {
            "timestamp": timestamp,
            "torque_amplitude": torque_amplitude,
            "phase_angle_deg": phase_angle_deg,
            "quadrature_error": quadrature_error,
            "in_phase": in_phase_component,
            "quadrature": quadrature_component
        }
        self.telemetry_history.append(metric)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        return metric

    def analyze_harmonic_interference(self) -> Dict[str, Any]:
        if not self.telemetry_history:
            return {"status": "insufficient_data"}
            
        amplitudes = [m["torque_amplitude"] for m in self.telemetry_history]
        quad_errors = [m["quadrature_error"] for m in self.telemetry_history]
        
        mean_amp = statistics.mean(amplitudes)
        max_amp = max(amplitudes)
        mean_quad = statistics.mean(quad_errors)
        
        risk_score = (max_amp / (mean_amp + 1e-6)) * abs(mean_quad)
        anomaly_detected = risk_score > 2.5
        
        return {
            "mill_id": self.mill_id,
            "samples_analyzed": len(self.telemetry_history),
            "mean_torque_amplitude": mean_amp,
            "max_torque_amplitude": max_amp,
            "mean_quadrature_error": mean_quad,
            "harmonic_risk_score": risk_score,
            "anomaly_detected": anomaly_detected,
            "recommendation": "Inspect drive coupling and alignment" if anomaly_detected else "Nominal operation"
        }


if __name__ == "__main__":
    investigator = RollerMillTorqueInvestigator("MILL-NRB-01")
    investigator.ingest_resolver_data(120.5, 14.2, 0.03)
    investigator.ingest_resolver_data(125.1, 15.0, 0.05)
    investigator.ingest_resolver_data(185.8, 45.5, 0.89)
    report = investigator.analyze_harmonic_interference()
    print(f"[TEST HARNESS] Roller Mill Investigation Report: {report}")
