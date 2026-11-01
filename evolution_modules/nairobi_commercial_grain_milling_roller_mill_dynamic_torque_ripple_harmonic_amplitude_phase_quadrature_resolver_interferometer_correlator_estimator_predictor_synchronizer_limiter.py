"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude
Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Limiter

Provides advanced real-time digital signal processing, quadrature phase interferometry,
and adaptive limiter control for high-torque commercial roller mill drives in Nairobi grain mills.
"""

import math
import logging
import statistics
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueLimiter")


class RollerMillTorqueLimiter:
    """
    Monitors, correlates, and limits dynamic torque ripple harmonics on commercial roller mill drives.
    """

    def __init__(self, baseline_frequency_hz: float = 50.0, harmonic_limit_threshold: float = 0.85):
        self.baseline_frequency_hz = baseline_frequency_hz
        self.harmonic_limit_threshold = harmonic_limit_threshold
        self.telemetry_history: List[Dict[str, float]] = []

    def process_interferometer_sample(self, timestamp: float, raw_torque_nm: float, phase_angle_rad: float) -> Dict[str, float]:
        """
        Processes incoming quadrature resolver interferometer telemetry samples.
        Calculates harmonic amplitude, phase distortion, and applies active limiting algorithms.
        """
        # Quadrature component extraction
        quad_in_phase = raw_torque_nm * math.cos(phase_angle_rad)
        quad_out_phase = raw_torque_nm * math.sin(phase_angle_rad)
        amplitude = math.sqrt(quad_in_phase**2 + quad_out_phase**2)

        # Estimate harmonic ripple ratio
        mean_amplitude = statistics.mean([t["amplitude"] for t in self.telemetry_history]) if self.telemetry_history else amplitude
        ripple_ratio = amplitude / (mean_amplitude + 1e-6)

        # Active limitation factor
        limiter_gain = 1.0
        if ripple_ratio > self.harmonic_limit_threshold:
            limiter_gain = self.harmonic_limit_threshold / ripple_ratio
            logger.warning(
                f"[TORQUE LIMITER ALERT] Harmonic ripple ratio {ripple_ratio:.3f} exceeded threshold {self.harmonic_limit_threshold}. "
                f"Applying dynamic limiter gain: {limiter_gain:.3f}"
            )

        regulated_torque = raw_torque_nm * limiter_gain

        record = {
            "timestamp": timestamp,
            "raw_torque": raw_torque_nm,
            "amplitude": amplitude,
            "ripple_ratio": ripple_ratio,
            "limiter_gain": limiter_gain,
            "regulated_torque": regulated_torque
        }

        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return record

    def get_system_diagnostics(self) -> Dict[str, float]:
        """Returns aggregate diagnostics for the roller mill torque subsystem."""
        if not self.telemetry_history:
            return {"status": "IDLE", "max_ripple": 0.0, "mean_regulated_torque": 0.0}

        max_ripple = max(t["ripple_ratio"] for t in self.telemetry_history)
        mean_torque = statistics.mean(t["regulated_torque"] for t in self.telemetry_history)

        return {
            "status": "ACTIVE_REGULATED",
            "max_ripple": max_ripple,
            "mean_regulated_torque": mean_torque,
            "sample_count": len(self.telemetry_history)
        }


if __name__ == "__main__":
    limiter = RollerMillTorqueLimiter()
    logger.info("Initializing RollerMillTorqueLimiter test sequence...")
    
    # Simulate baseline and spike samples
    test_samples = [
        (1.0, 250.0, 0.1),
        (2.0, 255.0, 0.2),
        (3.0, 420.0, 1.5),  # High torque ripple spike
        (4.0, 248.0, 0.15)
    ]

    for ts, torque, phase in test_samples:
        res = limiter.process_interferometer_sample(ts, torque, phase)
        logger.info(f"Sample {ts}s: Regulated Torque = {res['regulated_torque']:.2f} Nm, Gain = {res['limiter_gain']:.2f}")

    diag = limiter.get_system_diagnostics()
    logger.info(f"Diagnostics Summary: {diag}")
