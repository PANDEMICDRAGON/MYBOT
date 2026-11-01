"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Regulator Module."""

import math
import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueRegulator")


class RollerMillTorqueRippleRegulator:
    """Performs real-time quadrature resolution, phase tracking, and harmonic torque ripple compensation."""

    def __init__(self, sample_rate_hz: float = 1000.0, nominal_rpm: float = 1500.0):
        self.sample_rate_hz = sample_rate_hz
        self.nominal_rpm = nominal_rpm
        self.phase_angle = 0.0
        self.harmonic_buffer: List[float] = []
        self.is_synchronized = False
        logger.info("Initialized RollerMillTorqueRippleRegulator at %.1f Hz nominal RPM: %.1f", sample_rate_hz, nominal_rpm)

    def process_telemetry(self, raw_torque_nm: float, vibration_amplitude_g: float) -> Dict[str, Any]:
        """Process live torque telemetry and compute compensation vector."""
        dt = 1.0 / self.sample_rate_hz
        omega = (2.0 * math.pi * self.nominal_rpm) / 60.0
        self.phase_angle = (self.phase_angle + omega * dt) % (2.0 * math.pi)

        # Quadrature estimation
        quad_i = raw_torque_nm * math.cos(self.phase_angle)
        quad_q = raw_torque_nm * math.sin(self.phase_angle)
        magnitude = math.sqrt(quad_i**2 + quad_q**2)

        self.harmonic_buffer.append(magnitude)
        if len(self.harmonic_buffer) > 100:
            self.harmonic_buffer.pop(0)

        avg_magnitude = sum(self.harmonic_buffer) / len(self.harmonic_buffer)
        ripple_variance = abs(magnitude - avg_magnitude)

        # Synchronization assessment
        self.is_synchronized = ripple_variance < (avg_magnitude * 0.15)

        compensation_signal = -0.5 * quad_q if not self.is_synchronized else 0.0

        return {
            "timestamp": time.time(),
            "quadrature_i": round(quad_i, 4),
            "quadrature_q": round(quad_q, 4),
            "harmonic_magnitude": round(magnitude, 4),
            "ripple_variance": round(ripple_variance, 4),
            "is_synchronized": self.is_synchronized,
            "compensation_signal": round(compensation_signal, 4),
            "vibration_g": vibration_amplitude_g
        }


if __name__ == "__main__":
    regulator = RollerMillTorqueRippleRegulator()
    sample_torque = 125.4
    sample_vib = 0.042
    result = regulator.process_telemetry(sample_torque, sample_vib)
    logger.info("Test execution output: %s", result)
