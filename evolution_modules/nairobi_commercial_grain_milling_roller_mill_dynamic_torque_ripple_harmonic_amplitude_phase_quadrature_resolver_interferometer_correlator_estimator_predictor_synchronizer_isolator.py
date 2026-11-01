"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Isolator

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides advanced digital signal processing, quadrature phase resolution, harmonic interferometry, and predictive torque ripple isolation for industrial roller mills.
"""

import math
import cmath
import statistics
import logging
from typing import Dict, List, Tuple, Any

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [TORSIONAL_ISOLATOR] %(levelname)s: %(message)s')
logger = logging.getLogger("TorsionalIsolator")

class TorsionalHarmonicInterferometer:
    """
    Measures and correlates torque ripple harmonics using quadrature phase resolution
    and interferometric signal analysis.
    """
    def __init__(self, base_frequency_hz: float = 50.0, resolution_factor: int = 4):
        self.base_frequency_hz = base_frequency_hz
        self.resolution_factor = resolution_factor
        self.phase_quadrature_matrix: List[complex] = []

    def ingest_signal(self, torque_samples: List[float]) -> Dict[str, Any]:
        """Transform raw torque samples into quadrature components and compute harmonic amplitudes."""
        if not torque_samples:
            return {"status": "error", "message": "Empty torque sample buffer"}

        n = len(torque_samples)
        complex_signals = []
        for i, val in enumerate(torque_samples):
            angle = 2.0 * math.pi * self.base_frequency_hz * (i / n) * self.resolution_factor
            # Form quadrature complex phasor (I + jQ)
            phasor = val * cmath.rect(1.0, angle)
            complex_signals.append(phasor)

        self.phase_quadrature_matrix = complex_signals
        mean_phasor = sum(complex_signals) / n
        amplitude = abs(mean_phasor)
        phase = cmath.phase(mean_phasor)

        logger.info(f"Harmonic Interferometer Analysis: Amplitude={amplitude:.4f} Nm, Phase={phase:.4f} rad")
        return {
            "status": "success",
            "sample_count": n,
            "harmonic_amplitude": amplitude,
            "phase_radians": phase,
            "quadrature_vector_magnitude": abs(mean_phasor)
        }


class TorqueRipplePredictor:
    """
    Predicts upcoming torsional resonance spikes using historical quadrature data.
    """ 
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.amplitude_history: List[float] = []

    def update(self, amplitude: float) -> float:
        self.amplitude_history.append(amplitude)
        if len(self.amplitude_history) > self.window_size:
            self.amplitude_history.pop(0)
        
        if len(self.amplitude_history) < 2:
            return amplitude

        # Simple linear extrapolation prediction of next amplitude
        trend = self.amplitude_history[-1] - self.amplitude_history[-2]
        predicted = max(0.0, self.amplitude_history[-1] + trend)
        return predicted


class RollerMillTorsionalIsolator:
    """
    Orchestrates the resolver interferometer, correlates phase jitter, and
    triggers protective isolation routines for Nairobi industrial roller mills.
    """
    def __init__(self, threshold_nm: float = 15.0):
        self.threshold_nm = threshold_nm
        self.interferometer = TorsionalHarmonicInterferometer()
        self.predictor = TorqueRipplePredictor()
        self.isolation_engaged = False

    def evaluate_roller_dynamics(self, torque_samples: List[float]) -> Dict[str, Any]:
        analysis = self.interferometer.ingest_signal(torque_samples)
        if analysis["status"] != "success":
            return analysis

        current_amp = analysis["harmonic_amplitude"]
        predicted_amp = self.predictor.update(current_amp)

        action = "STABLE"
        if predicted_amp > self.threshold_nm or current_amp > self.threshold_nm:
            self.isolation_engaged = True
            action = "ISOLATE_DRIVE_MOTOR_HARMONIC_CASCADE"
            logger.warning(f"Torsional harmonic threshold breached! Current: {current_amp:.2f} Nm, Predicted: {predicted_amp:.2f} Nm. Action: {action}")
        else:
            self.isolation_engaged = False
            logger.info(f"Roller mill operation nominal. Current: {current_amp:.2f} Nm, Predicted: {predicted_amp:.2f} Nm.")

        return {
            "isolation_engaged": self.isolation_engaged,
            "current_amplitude_nm": current_amp,
            "predicted_amplitude_nm": predicted_amp,
            "threshold_nm": self.threshold_nm,
            "action_recommended": action
        }


if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Roller Mill Torsional Isolator Test Harness...")
    isolator = RollerMillTorsionalIsolator(threshold_nm=12.0)
    
    # Simulate normal and turbulent torque ripple waveforms
    normal_torque = [10.0 + math.sin(i * 0.5) * 2.0 for i in range(50)]
    turbulent_torque = [10.0 + (i % 5) * 4.5 + math.sin(i) * 6.0 for i in range(50)]

    logger.info("--- Testing Normal Operating Profile ---")
    res_normal = isolator.evaluate_roller_dynamics(normal_torque)
    print(res_normal)

    logger.info("--- Testing High-Ripple Harmonic Cascade Profile ---")
    res_turbulent = isolator.evaluate_roller_dynamics(turbulent_torque)
    print(res_turbulent)
    logger.info("Test harness execution complete.")
