"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Analyst

Provides advanced real-time DSP analysis of roller mill drive torque ripple, quadrature resolver feedback, and harmonic phase alignment to ensure optimal flour milling efficiency in Nairobi grain processing facilities.
"""

import math
import time
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicAnalyst")


class RollerMillHarmonicAnalyst:
    """Analyzes roller mill drive torque ripple and phase quadrature harmonics."""

    def __init__(self, mill_id: str, nominal_rpm: float = 1450.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.sample_buffer: List[Dict[str, float]] = []

    def ingest_telemetry(self, torque_nm: float, phase_deg: float, quadrature_v: float) -> Dict[str, Any]:
        """Ingests instantaneous torque, phase, and quadrature telemetry."""
        timestamp = time.time()
        sample = {
            "timestamp": timestamp,
            "torque_nm": torque_nm,
            "phase_deg": phase_deg,
            "quadrature_v": quadrature_v
        }
        self.sample_buffer.append(sample)
        if len(self.sample_buffer) > 1000:
            self.sample_buffer.pop(0)
        return self._analyze_latest(sample)

    def _analyze_latest(self, sample: Dict[str, float]) -> Dict[str, Any]:
        torque = sample["torque_nm"]
        phase = sample["phase_deg"]
        quad = sample["quadrature_v"]

        # Compute synthetic harmonic amplitude and phase quadrature correlation
        harmonic_amplitude = abs(torque * math.sin(math.radians(phase))) * (1.0 + abs(quad) * 0.01)
        quadrature_interference = math.cos(math.radians(phase)) * quad

        status = "OPTIMAL"
        if harmonic_amplitude > 120.0:
            status = "WARNING_HIGH_HARMONIC_RIPPLE"
        if abs(quadrature_interference) > 50.0:
            status = "CRITICAL_PHASE_MISALIGNMENT"

        analysis = {
            "mill_id": self.mill_id,
            "timestamp": sample["timestamp"],
            "harmonic_amplitude": round(harmonic_amplitude, 4),
            "quadrature_interference": round(quadrature_interference, 4),
            "status": status
        }
        return analysis

    def generate_report(self) -> Dict[str, Any]:
        """Generates a comprehensive diagnostic summary of recent samples."""
        if not self.sample_buffer:
            return {"error": "No telemetry recorded."}
        
        avg_torque = sum(s["torque_nm"] for s in self.sample_buffer) / len(self.sample_buffer)
        latest = self._analyze_latest(self.sample_buffer[-1])
        
        return {
            "mill_id": self.mill_id,
            "total_samples": len(self.sample_buffer),
            "average_torque_nm": round(avg_torque, 2),
            "latest_analysis": latest
        }


if __name__ == "__main__":
    analyst = RollerMillHarmonicAnalyst(mill_id="NAIROBI_MILL_ALPHA_01")
    
    # Simulate some operational telemetry cycles
    test_data = [
        (85.5, 12.3, 1.02),
        (92.1, 45.0, 3.45),
        (140.2, 89.5, 8.12),
        (88.0, 14.1, 0.95)
    ]
    
    for t, p, q in test_data:
        res = analyst.ingest_telemetry(t, p, q)
        logger.info(f"Telemetry Analysis Result: {res}")
        
    report = analyst.generate_report()
    logger.info(f"Final Mill Diagnostic Report: {report}")
