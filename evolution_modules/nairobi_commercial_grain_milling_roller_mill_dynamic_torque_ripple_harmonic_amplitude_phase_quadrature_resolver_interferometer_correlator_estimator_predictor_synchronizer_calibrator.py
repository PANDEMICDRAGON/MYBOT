"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude
Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Calibrator Module

Designed for high-precision industrial roller mill telemetry analysis in Nairobi, Kenya.
Provides real-time harmonic distortion estimation, phase quadrature demodulation, and predictive torque compensation.
"""

import math
import time
import logging
from typing import Dict, List, Tuple, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillCalibrator")

class RollerMillCalibrator:
    """
    Evaluates quadrature resolver signals and harmonic amplitudes from roller mill drives
    to ensure mechanical resonance stability and prevent catastrophic drive failure.
    """
    
    def __init__(self, mill_id: str, nominal_rpm: float = 1450.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.calibration_history: List[Dict[str, Any]] = []

    def process_resolver_telemetry(self, sine_wave: List[float], cosine_wave: List[float]) -> Dict[str, Any]:
        """
        Performs phase quadrature resolution and harmonic distortion estimation
        from raw sine and cosine interferometer telemetry streams.
        """
        if len(sine_wave) != len(cosine_wave) or not sine_wave:
            raise ValueError("Resolver telemetry streams must be of equal non-zero length.")
        
        resolved_angles = []
        torque_ripple_sum = 0.0
        
        for s, c in zip(sine_wave, cosine_wave):
            angle = math.atan2(s, c)
            resolved_angles.append(angle)
            # Calculate instantaneous quadrature magnitude deviation
            magnitude = math.sqrt(s**2 + c**2)
            ripple = abs(1.0 - magnitude)
            torque_ripple_sum += ripple
            
        mean_ripple = torque_ripple_sum / len(sine_wave)
        phase_jitter = self._calculate_phase_jitter(resolved_angles)
        
        assessment = {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "mean_torque_ripple": mean_ripple,
            "phase_jitter_rad": phase_jitter,
            "harmonic_distortion_index": mean_ripple * phase_jitter * 100.0,
            "status": "OPTIMIZED" if mean_ripple < 0.05 else "ATTENTION_REQUIRED"
        }
        
        self.calibration_history.append(assessment)
        logger.info(f"[{self.mill_id}] Calibration processed. Ripple: {mean_ripple:.5f}, Status: {assessment['status']}")
        return assessment

    def _calculate_phase_jitter(self, angles: List[float]) -> float:
        """Calculates standard deviation of angular velocity increments as phase jitter."""
        if len(angles) < 2:
            return 0.0
        diffs = [angles[i] - angles[i-1] for i in range(1, len(angles))]
        mean_diff = sum(diffs) / len(diffs)
        variance = sum((d - mean_diff) ** 2 for d in diffs) / len(diffs)
        return math.sqrt(variance)

    def get_calibration_summary(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "total_inspections": len(self.calibration_history),
            "latest_telemetry": self.calibration_history[-1] if self.calibration_history else None
        }

if __name__ == "__main__":
    calibrator = RollerMillCalibrator(mill_id="NAI_MILL_ALPHA_01")
    # Simulate quadrature feedback
    sim_sine = [math.sin(i * 0.1) + 0.02 * math.sin(i * 0.5) for i in range(100)]
    sim_cosine = [math.cos(i * 0.1) + 0.02 * math.cos(i * 0.5) for i in range(100)]
    result = calibrator.process_resolver_telemetry(sim_sine, sim_cosine)
    print("Test Execution Successful:", result)
