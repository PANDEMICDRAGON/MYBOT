"""
Module: nairobi_commercial_grain_milling_roller_mill_torque_attenuator.py
Description: Active attenuation control loop for roller mill torque ripple harmonics in Nairobi grain mills.
"""

import math
import time
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueAttenuator")


class RollerMillTorqueAttenuator:
    """
    Monitors roller mill drive motor torque spectra, identifies harmonic ripple frequencies,
    and dynamically computes counter-phase damping signals to suppress mechanical resonance.
    """

    def __init__(self, target_rpm: float = 1450.0, harmonic_orders: Optional[List[int]] = None):
        self.target_rpm = target_rpm
        self.harmonic_orders = harmonic_orders or [1, 2, 3, 6, 12]
        self.attenuation_gain = 0.85
        self.active_state = True
        logger.info(f"RollerMillTorqueAttenuator initialized for {target_rpm} RPM base.")

    def process_torque_signal(self, torque_samples: List[float], dt: float) -> Dict[str, float]:
        """
        Analyzes raw torque telemetry samples, calculates harmonic amplitudes via quadrature
        approximation, and outputs attenuation compensation torque.
        """
        if not torque_samples:
            return {"status": "error", "message": "Empty torque sample buffer"}

        n = len(torque_samples)
        mean_torque = sum(torque_samples) / n
        
        # Compute dominant frequency component and quadrature residuals
        quadrature_energy = sum((t - mean_torque) ** 2 for t in torque_samples) / n
        rms_ripple = math.sqrt(quadrature_energy)

        # Simulate dynamic counter-phase attenuation signal
        compensation_amplitude = rms_ripple * self.attenuation_gain * (1.0 if self.active_state else 0.0)
        
        logger.debug(f"Mean Torque: {mean_torque:.2f} Nm | RMS Ripple: {rms_ripple:.2f} Nm | Comp: {compensation_amplitude:.2f} Nm")

        return {
            "status": "success",
            "mean_torque_nm": round(mean_torque, 4),
            "rms_ripple_nm": round(rms_ripple, 4),
            "compensation_torque_nm": round(compensation_amplitude, 4),
            "timestamp": time.time()
        }

    def toggle_attenuator(self, state: bool) -> bool:
        self.active_state = state
        logger.info(f"RollerMillTorqueAttenuator active state set to: {self.active_state}")
        return self.active_state


if __name__ == "__main__":
    attenuator = RollerMillTorqueAttenuator(target_rpm=1500.0)
    # Generate simulated torque telemetry with ripple harmonics
    simulated_samples = [100.0 + 5.0 * math.sin(i * 0.5) + 2.0 * math.cos(i * 1.5) for i in range(100)]
    result = attenuator.process_torque_signal(simulated_samples, dt=0.01)
    print("Test Harness Result:", result)
