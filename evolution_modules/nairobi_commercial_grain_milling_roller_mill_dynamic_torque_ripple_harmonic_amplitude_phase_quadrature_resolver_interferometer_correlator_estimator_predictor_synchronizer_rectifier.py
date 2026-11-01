"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Rectifier Module."""

import math
import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("RollerMillHarmonicRectifier")


class RollerMillHarmonicRectifier:
    """Performs real-time quadrature resolver interferometry and harmonic rectification on roller mill torque telemetry."""

    def __init__(self, sample_rate_hz: float = 1000.0, harmonic_order: int = 5):
        self.sample_rate_hz = sample_rate_hz
        self.harmonic_order = harmonic_order
        self.telemetry_history: List[Dict[str, float]] = []
        logger.info("Initialized RollerMillHarmonicRectifier with sample rate %.1f Hz, harmonic order %d", sample_rate_hz, harmonic_order)

    def process_telemetry_frame(self, raw_torque_nm: float, phase_angle_rad: float) -> Dict[str, Any]:
        """Process an incoming stream of torque and phase measurements."""
        timestamp = time.time()
        quadrature_i = raw_torque_nm * math.cos(phase_angle_rad)
        quadrature_q = raw_torque_nm * math.sin(phase_angle_rad)
        
        # Interferometer correlation estimation
        amplitude_estimate = math.sqrt(quadrature_i**2 + quadrature_q**2)
        harmonic_correction = amplitude_estimate * (1.0 / (1.0 + float(self.harmonic_order)))
        rectified_torque = raw_torque_nm - harmonic_correction

        frame = {
            "timestamp": timestamp,
            "raw_torque_nm": raw_torque_nm,
            "phase_angle_rad": phase_angle_rad,
            "quadrature_i": quadrature_i,
            "quadrature_q": quadrature_q,
            "amplitude_estimate": amplitude_estimate,
            "rectified_torque": rectified_torque
        }

        self.telemetry_history.append(frame)
        if len(self.telemetry_history) > 100:
            self.telemetry_history.pop(0)

        return frame

    def get_system_diagnostics(self) -> Dict[str, Any]:
        """Returns aggregate health and synchronization metrics for the roller mill."""
        if not self.telemetry_history:
            return {"status": "IDLE", "mean_rectified_torque": 0.0}

        rectified_values = [f["rectified_torque"] for f in self.telemetry_history]
        mean_torque = sum(rectified_values) / len(rectified_values)
        max_torque = max(rectified_values)
        min_torque = min(rectified_values)

        return {
            "status": "SYNCHRONIZED_AND_RECTIFIED",
            "samples_processed": len(self.telemetry_history),
            "mean_rectified_torque": mean_torque,
            "peak_rectified_torque": max_torque,
            "min_rectified_torque": min_torque
        }


if __name__ == "__main__":
    rectifier = RollerMillHarmonicRectifier()
    logger.info("Executing test harness for RollerMillHarmonicRectifier...")
    for i in range(10):
        torque = 150.0 + 15.0 * math.sin(i * 0.5)
        phase = i * 0.1
        result = rectifier.process_telemetry_frame(torque, phase)
        logger.info("Frame %d processed: Rectified Torque = %.2f Nm", i, result["rectified_torque"])
    
    diagnostics = rectifier.get_system_diagnostics()
    logger.info("Diagnostics Result: %s", diagnostics)
