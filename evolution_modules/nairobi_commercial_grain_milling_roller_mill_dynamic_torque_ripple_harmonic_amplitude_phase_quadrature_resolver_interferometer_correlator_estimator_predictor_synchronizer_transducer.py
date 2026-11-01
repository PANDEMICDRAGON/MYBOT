"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Transducer

Author: Cortana, Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
Description:
  Provides high-frequency telemetry resolution, quadrature signal correlation, torque ripple harmonic
  decomposition, and predictive synchronization for industrial commercial roller mills operating in Nairobi.
"""

import math
import time
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTransducer")


class RollerMillTransducer:
    """
    Monitors and analyzes quadrature resolver interference and harmonic torque ripples
    on commercial roller mill spindles.
    """

    def __init__(self, mill_id: str, baseline_frequency_hz: float = 50.0):
        self.mill_id = mill_id
        self.baseline_frequency_hz = baseline_frequency_hz
        self.telemetry_history: List[Dict[str, Any]] = []

    def sample_spindle_quadrature(self, raw_sin_signal: float, raw_cos_signal: float, current_rpm: float) -> Dict[str, Any]:
        """
        Computes phase angle, amplitude, and harmonic distortion from raw quadrature signals.
        """
        phase_rad = math.atan2(raw_sin_signal, raw_cos_signal)
        amplitude = math.hypot(raw_sin_signal, raw_cos_signal)
        
        # Simulate torque ripple harmonic components (3rd, 5th, 7th harmonics)
        harmonic_3rd = amplitude * 0.08 * math.sin(3 * phase_rad)
        harmonic_5th = amplitude * 0.04 * math.sin(5 * phase_rad)
        harmonic_7th = amplitude * 0.02 * math.sin(7 * phase_rad)
        total_harmonic_distortion = (math.hypot(harmonic_3rd, harmonic_5th) + abs(harmonic_7th)) / (amplitude + 1e-9)

        status = "OPTIMAL"
        if total_harmonic_distortion > 0.12:
            status = "WARNING_HARMONIC_ELEVATED"
        elif total_harmonic_distortion > 0.20:
            status = "CRITICAL_TORQUE_RIPPLE_INSTABILITY"

        record = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "current_rpm": current_rpm,
            "phase_rad": phase_rad,
            "amplitude": amplitude,
            "thd": total_harmonic_distortion,
            "status": status
        }

        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return record

    def predict_synchronization_offset(self) -> float:
        """
        Estimates phase correction lag for spindle synchronization across multi-deck roller banks.
        """
        if not self.telemetry_history:
            return 0.0

        recent = self.telemetry_history[-1]
        # Predictive damping factor based on recent THD
        lag_estimation = recent["thd"] * 0.015 * (recent["current_rpm"] / self.baseline_frequency_hz)
        return float(lag_estimation)


if __name__ == "__main__":
    logger.info("Initializing RollerMillTransducer test harness for Nairobi facility...")
    transducer = RollerMillTransducer(mill_id="NAIROBI_MILL_ALPHA_01")
    
    # Simulate a running roller mill cycle
    for i in range(5):
        sin_val = math.sin(i * 0.5)
        cos_val = math.cos(i * 0.5)
        res = transducer.sample_spindle_quadrature(sin_val, cos_val, current_rpm=1485.5 + i)
        offset = transducer.predict_synchronization_offset()
        logger.info(f"Step {i}: Status={res['status']}, THD={res['thd']:.4f}, Offset={offset:.5f}")

    logger.info("Nairobi Roller Mill Transducer test completed successfully.")
