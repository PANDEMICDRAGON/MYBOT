"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Equalizer

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Provides real-time quadrature signal interferometry, harmonic phase-locked loop synchronization, and active torque ripple equalization for industrial roller mills.
"""

import math
import time
import logging
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueEqualizer")


class RollerMillTorqueEqualizer:
    """Advanced DSP engine for roller mill torque ripple cancellation and harmonic synchronization."""

    def __init__(self, sample_rate_hz: float = 1000.0, base_roll_rpm: float = 650.0):
        self.sample_rate_hz = sample_rate_hz
        self.base_roll_rpm = base_roll_rpm
        self.fundamental_freq = base_roll_rpm / 60.0
        self.phase_quadrature_state = 0.0
        self.harmonic_coefficients: Dict[int, float] = {1: 0.85, 2: 0.42, 3: 0.18, 5: 0.09}
        self.equalization_gain = 1.0
        logger.info(f"Initialized Torque Equalizer: {base_roll_rpm} RPM ({self.fundamental_freq:.2f} Hz)")

    def process_interferometer_sample(self, raw_torque_signal: float, harmonic_order: int = 1) -> Tuple[float, float, float]:
        """Process raw torque resolver readings through quadrature phase interferometry."""
        dt = 1.0 / self.sample_rate_hz
        omega = 2.0 * math.pi * self.fundamental_freq * harmonic_order
        
        self.phase_quadrature_state = (self.phase_quadrature_state + omega * dt) % (2.0 * math.pi)
        
        # Quadrature mixing (I/Q demodulation)
        i_component = raw_torque_signal * math.cos(self.phase_quadrature_state)
        q_component = raw_torque_signal * math.sin(self.phase_quadrature_state)
        
        amplitude = math.sqrt(i_component**2 + q_component**2) * 2.0
        phase_angle = math.atan2(q_component, i_component)
        
        # Active equalization correction factor
        coef = self.harmonic_coefficients.get(harmonic_order, 0.05)
        correction = -1.0 * amplitude * coef * self.equalization_gain * math.cos(self.phase_quadrature_state + phase_angle)
        
        stabilized_torque = raw_torque_signal + correction
        return stabilized_torque, amplitude, phase_angle

    def calibrate_equalizer(self, vibration_feedback: float) -> None:
        """Auto-tune equalization gain based on downstream milling vibration feedback."""
        if vibration_feedback > 5.0:
            self.equalization_gain = min(2.0, self.equalization_gain * 1.05)
            logger.warning(f"High vibration detected ({vibration_feedback} mm/s). Increasing equalization gain to {self.equalization_gain:.3f}")
        elif vibration_feedback < 1.0:
            self.equalization_gain = max(0.5, self.equalization_gain * 0.98)
            logger.info(f"Optimal vibration state. Fine-tuning gain to {self.equalization_gain:.3f}")

    def generate_telemetry_report(self) -> Dict[str, any]:
        """Generate comprehensive telemetry report for Cortana central monitoring."""
        return {
            "timestamp": time.time(),
            "base_roll_rpm": self.base_roll_rpm,
            "fundamental_freq_hz": self.fundamental_freq,
            "phase_quadrature_state_rad": self.phase_quadrature_state,
            "equalization_gain": self.equalization_gain,
            "harmonic_model_orders": list(self.harmonic_coefficients.keys()),
            "operator": "Michael Obiero",
            "location": "Nairobi, Kenya"
        }


if __name__ == "__main__":
    print("[EXEC] Running RollerMillTorqueEqualizer test harness...")
    equalizer = RollerMillTorqueEqualizer(sample_rate_hz=500.0, base_roll_rpm=700.0)
    
    # Simulate 10 iterations of raw torque ripple input
    for step in range(10):
        simulated_torque = 45.0 + 12.0 * math.sin(step * 0.5)
        stable_torque, amp, phase = equalizer.process_interferometer_sample(simulated_torque, harmonic_order=2)
        print(f"Step {step}: Raw={simulated_torque:.2f}Nm | Stable={stable_torque:.2f}Nm | Amp={amp:.2f} | Phase={phase:.2f}rad")
        equalizer.calibrate_equalizer(vibration_feedback=2.5)
        
    report = equalizer.generate_telemetry_report()
    print("[SUCCESS] Telemetry Report:", report)
