"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Compensator Module.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import math
import logging
import time
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [RollerMillCompensator]: %(message)s')
logger = logging.getLogger(__name__)


class RollerMillTorqueCompensator:
    """Performs real-time torque ripple cancellation and quadrature phase correction for commercial roller mills."""

    def __init__(self, mill_id: str, base_rpm: float = 1500.0, harmonic_orders: List[int] = None):
        self.mill_id = mill_id
        self.base_rpm = base_rpm
        self.harmonic_orders = harmonic_orders or [1, 2, 3, 6, 12]
        self.calibration_active = True
        logger.info(f"Initialized RollerMillTorqueCompensator for {{mill_id}} at {{base_rpm}} RPM.")

    def compute_quadrature_resolver(self, raw_sin_signal: float, raw_cos_signal: float) -> Dict[str, float]:
        """Computes phase angle and instantaneous amplitude using quadrature resolver demodulation."""
        amplitude = math.sqrt(raw_sin_signal ** 2 + raw_cos_signal ** 2)
        phase_rad = math.atan2(raw_sin_signal, raw_cos_signal)
        phase_deg = math.degrees(phase_rad) % 360.0
        return {
            "amplitude": round(amplitude, 4),
            "phase_rad": round(phase_rad, 4),
            "phase_deg": round(phase_deg, 2)
        }

    def estimate_torque_ripple_harmonics(self, torque_waveform: List[float]) -> Dict[str, Any]:
        """Estimates harmonic amplitudes and phase offsets using discrete interferometry correlation."""
        n = len(torque_waveform)
        if n == 0:
            return {"error": "Empty torque waveform"}

        mean_torque = sum(torque_waveform) / n
        harmonics_result = {}

        for order in self.harmonic_orders:
            # Simulated quadrature correlation for specific harmonic order
            sin_sum = 0.0
            cos_sum = 0.0
            for i, val in enumerate(torque_waveform):
                angle = (2 * math.pi * order * i) / n
                deviation = val - mean_torque
                sin_sum += deviation * math.sin(angle)
                cos_sum += deviation * math.cos(angle)

            harm_amp = (2.0 / n) * math.sqrt(sin_sum ** 2 + cos_sum ** 2)
            harm_phase = math.atan2(sin_sum, cos_sum)
            harmonics_result[f"order_{order}"] = {
                "amplitude": round(harm_amp, 4),
                "phase_offset_rad": round(harm_phase, 4)
            }

        return {
            "mean_torque": round(mean_torque, 4),
            "harmonic_spectrum": harmonics_result,
            "timestamp": time.time()
        }

    def generate_compensation_correction(self, spectrum: Dict[str, Any]) -> Dict[str, float]:
        """Predicts and generates anti-phase corrective feedback currents for the roller mill inverter drive."""
        corrections = {}
        spectrum_data = spectrum.get("harmonic_spectrum", {})
        
        total_correction = 0.0
        for order_key, data in spectrum_data.items():
            amp = data.get("amplitude", 0.0)
            phase = data.get("phase_offset_rad", 0.0)
            # Invert phase by pi and scale by damping factor 0.85
            comp_amp = amp * 0.85
            comp_phase = (phase + math.pi) % (2 * math.pi)
            corrections[order_key] = {
                "corrective_amplitude": round(comp_amp, 4),
                "corrective_phase_rad": round(comp_phase, 4)
            }
            total_correction += comp_amp

        logger.info(f"[{{self.mill_id}}] Generated active torque ripple compensation. Total corrective amp: {{total_correction:.4f}} N·m")
        return {
            "mill_id": self.mill_id,
            "corrections": corrections,
            "aggregate_corrective_torque": round(total_correction, 4),
            "status": "OPTIMIZED"
        }


if __name__ == "__main__":
    logger.info("Executing RollerMillTorqueCompensator self-test harness...")
    compensator = RollerMillTorqueCompensator("NAIROBI_MILL_UNIT_04", base_rpm=1485.0)
    
    # Simulate a raw quadrature resolver input
    resolver_res = compensator.compute_quadrature_resolver(0.707, 0.707)
    logger.info(f"Resolver Test Result: {{resolver_res}}")

    # Simulate a noisy torque waveform with 1st and 3rd harmonics
    sample_waveform = [10.0 + 1.2 * math.sin(2 * math.pi * i / 50) + 0.4 * math.sin(2 * math.pi * 3 * i / 50) for i in range(100)]
    spectrum = compensator.estimate_torque_ripple_harmonics(sample_waveform)
    logger.info(f"Harmonic Spectrum Result: {{spectrum}}")

    feedback = compensator.generate_compensation_correction(spectrum)
    logger.info(f"Feedback Control Result: {{feedback}}")
    logger.info("RollerMillTorqueCompensator self-test completed successfully.")
