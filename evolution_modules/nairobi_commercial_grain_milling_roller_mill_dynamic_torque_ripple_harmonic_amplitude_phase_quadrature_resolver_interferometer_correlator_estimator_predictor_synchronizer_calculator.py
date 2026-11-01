"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Calculator

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import math
import statistics
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillHarmonicCalculator")

class RollerMillTorqueCalculator:
    """
    Computes quadrature resolver interference harmonics and predicts torque ripple corrections
    for industrial roller mills in Nairobi grain processing facilities.
    """
    def __init__(self, sample_rate_hz: float = 1000.0):
        self.sample_rate_hz = sample_rate_hz
        self.calibration_history: List[Dict[str, float]] = []

    def calculate_quadrature_interference(self, sine_wave: List[float], cosine_wave: List[float]) -> Dict[str, float]:
        """
        Calculates phase quadrature offset and interference amplitude between resolver signals.
        """
        if not sine_wave or not cosine_wave or len(sine_wave) != len(cosine_wave):
            raise ValueError("Invalid or mismatched resolver waveform buffers.")
        
        dot_product = sum(s * c for s, c in zip(sine_wave, cosine_wave))
        norm_s = math.sqrt(sum(s**2 for s in sine_wave))
        norm_c = math.sqrt(sum(c**2 for c in cosine_wave))
        
        if norm_s == 0.0 or norm_c == 0.0:
            phase_error_rad = 0.0
        else:
            cos_theta = max(-1.0, min(1.0, dot_product / (norm_s * norm_c)))
            phase_error_rad = math.acos(cos_theta) - (math.pi / 2.0)

        amplitude_ratio = norm_s / norm_c if norm_c != 0 else 1.0
        
        return {
            "phase_error_radians": phase_error_rad,
            "phase_error_degrees": math.degrees(phase_error_rad),
            "amplitude_imbalance_ratio": amplitude_ratio,
            "interferometer_correlation": dot_product / (norm_s * norm_c) if (norm_s * norm_c) != 0 else 0.0
        }

    def estimate_torque_ripple(self, harmonic_amplitudes: List[float], base_torque_nm: float) -> Dict[str, Any]:
        """
        Estimates overall harmonic distortion and peak torque ripple on the roller shaft.
        """
        if not harmonic_amplitudes:
            return {"thd_percentage": 0.0, "peak_ripple_nm": 0.0, "predicted_compensation_nm": 0.0}

        sum_sq_harmonics = sum(h**2 for h in harmonic_amplitudes)
        fundamental = harmonic_amplitudes[0] if harmonic_amplitudes else 1.0
        thd = (math.sqrt(sum_sq_harmonics) / fundamental) * 100.0 if fundamental != 0 else 0.0
        peak_ripple = max(harmonic_amplitudes) if harmonic_amplitudes else 0.0
        
        predicted_compensation = -0.5 * peak_ripple * math.sin(math.radians(thd))
        
        result = {
            "base_torque_nm": base_torque_nm,
            "thd_percentage": thd,
            "peak_ripple_nm": peak_ripple,
            "predicted_compensation_nm": predicted_compensation
        }
        self.calibration_history.append(result)
        return result

if __name__ == "__main__":
    logger.info("Initializing Roller Mill Harmonic Calculator Test Harness...")
    calc = RollerMillTorqueCalculator(sample_rate_hz=1000.0)
    
    # Generate dummy sine/cosine resolver waveforms
    t = [i * 0.01 for i in range(100)]
    sin_buf = [math.sin(x) for x in t]
    cos_buf = [math.cos(x + 0.05) for x in t] # slight phase deviation
    
    quad_result = calc.calculate_quadrature_interference(sin_buf, cos_buf)
    logger.info(f"Quadrature Analysis Result: {quad_result}")
    
    harmonics = [45.2, 12.1, 4.3, 1.8]
    torque_result = calc.estimate_torque_ripple(harmonics, base_torque_nm=250.0)
    logger.info(f"Torque Ripple Estimation: {torque_result}")
    logger.info("Test harness executed successfully.")
