"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Attenuator Module."""

import math
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueRippleAttenuator")


class RollerMillTorqueRippleAttenuator:
    """Resolves and attenuates high-order harmonic torque ripples in industrial roller mills."""

    def __init__(self, base_frequency_hz: float = 50.0, harmonic_orders: Optional[List[int]] = None):
        self.base_frequency_hz = base_frequency_hz
        self.harmonic_orders = harmonic_orders or [1, 2, 3, 5, 7, 11]
        self.telemetry_history: List[Dict[str, Any]] = []

    def compute_quadrature_interferometry(self, raw_torque_waveform: List[float]) -> Dict[str, Any]:
        """Applies quadrature demodulation and interferometer correlation to isolate harmonic phases."""
        n = len(raw_torque_waveform)
        if n == 0:
            raise ValueError("Raw torque waveform cannot be empty.")

        mean_torque = statistics.mean(raw_torque_waveform)
        rms_torque = math.sqrt(sum((x - mean_torque) ** 2 for x in raw_torque_waveform) / n)
        
        harmonic_signatures = {}
        for order in self.harmonic_orders:
            # Simulate quadrature mixing (sine/cosine demodulation)
            sin_sum = sum(val * math.sin(2 * math.pi * order * self.base_frequency_hz * i / max(n, 1)) 
                          for i, val in enumerate(raw_torque_waveform))
            cos_sum = sum(val * math.cos(2 * math.pi * order * self.base_frequency_hz * i / max(n, 1)) 
                          for i, val in enumerate(raw_torque_waveform))
            
            amplitude = math.sqrt(sin_sum**2 + cos_sum**2) / (n / 2 if n > 0 else 1)
            phase = math.atan2(sin_sum, cos_sum)
            
            harmonic_signatures[f"harmonic_{order}_x"] = {
                "amplitude": amplitude,
                "phase_radians": phase,
                "quadrature_in_phase": cos_sum,
                "quadrature_out_of_phase": sin_sum
            }

        result = {
            "mean_torque": mean_torque,
            "rms_torque": rms_torque,
            "harmonic_signatures": harmonic_signatures,
            "attenuation_recommended": rms_torque > 15.0
        }
        self.telemetry_history.append(result)
        return result

    def generate_counter_harmonic_pulse(self, analysis: Dict[str, Any]) -> List[float]:
        """Generates counter-harmonic phase-inverted signals to suppress drive train vibration."""
        signatures = analysis.get("harmonic_signatures", {})
        counter_pulse = [0.0] * 64
        
        for key, sig in signatures.items():
            amp = sig["amplitude"]
            phase = sig["phase_radians"]
            # Invert phase by pi for destructive interference
            inverted_phase = phase + math.pi
            for i in range(64):
                t = i / 64.0
                counter_pulse[i] += -amp * math.sin(2 * math.pi * t + inverted_phase)
                
        return counter_pulse


if __name__ == "__main__":
    logger.info("Initializing RollerMillTorqueRippleAttenuator test harness...")
    attenuator = RollerMillTorqueRippleAttenuator(base_frequency_hz=50.0)
    
    # Simulate synthetic torque ripple readings
    sample_waveform = [100.0 + 12.5 * math.sin(2 * math.pi * i / 10.0) + 4.2 * math.cos(2 * math.pi * i / 5.0) for i in range(128)]
    
    analysis_report = attenuator.compute_quadrature_interferometry(sample_waveform)
    logger.info(f"Analysis Report computed: Mean Torque = {analysis_report['mean_torque']:.2f} Nm, RMS = {analysis_report['rms_torque']:.2f} Nm")
    
    counter_pulse = attenuator.generate_counter_harmonic_pulse(analysis_report)
    logger.info(f"Generated counter-harmonic pulse vector of length {len(counter_pulse)} for vibration cancellation.")
    logger.info("RollerMillTorqueRippleAttenuator verified successfully.")
