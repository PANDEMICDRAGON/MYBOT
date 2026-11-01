"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude
Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Transducer

Implements real-time harmonic analysis, phase quadrature decomposition, and torque ripple
prediction for high-load commercial roller mills operating in Nairobi industrial zones.
"""

import math
import time
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillHarmonicTransducer")


class RollerMillHarmonicTransducer:
    """
    Analyzes torque ripple harmonics, computes quadrature phase shifts, and predicts
    mechanical resonance vectors for commercial milling machinery.
    """

    def __init__(self, mill_id: str, base_rpm: float = 1450.0):
        self.mill_id = mill_id
        self.base_rpm = base_rpm
        self.harmonic_buffer: List[Dict[str, float]] = []
        logger.info(f"Initialized RollerMillHarmonicTransducer for {{self.mill_id}} at {{self.base_rpm}} RPM.")

    def sample_torque_signal(self, raw_torque_samples: List[float]) -> Dict[str, Any]:
        """
        Processes raw torque waveform samples, extracting harmonic amplitude and phase quadrature.
        """
        if not raw_torque_samples:
            raise ValueError("Raw torque samples cannot be empty.")

        n = len(raw_torque_samples)
        mean_torque = sum(raw_torque_samples) / n
        
        # Compute fundamental and secondary harmonic components using discrete quadrature approximation
        cos_sum = sum(val * math.cos(2 * math.pi * i / n) for i, val in enumerate(raw_torque_samples))
        sin_sum = sum(val * math.sin(2 * math.pi * i / n) for i, val in enumerate(raw_torque_samples))
        
        amplitude = 2.0 * math.sqrt(cos_sum**2 + sin_sum**2) / n
        phase_rad = math.atan2(sin_sum, cos_sum)
        phase_deg = math.degrees(phase_rad)

        interferometer_index = amplitude / (abs(mean_torque) + 1e-6)

        reading = {
            "timestamp": time.time(),
            "mean_torque": mean_torque,
            "harmonic_amplitude": amplitude,
            "phase_quadrature_deg": phase_deg,
            "interferometer_index": interferometer_index
        }

        self.harmonic_buffer.append(reading)
        if len(self.harmonic_buffer) > 1000:
            self.harmonic_buffer.pop(0)

        return reading

    def predict_resonance_risk(self) -> Dict[str, Any]:
        """
        Predicts impending mechanical resonance or roller contact fatigue based on harmonic trends.
        """
        if len(self.harmonic_buffer) < 5:
            return {"status": "insufficient_data", "risk_score": 0.0}

        recent = self.harmonic_buffer[-5:]
        avg_amplitude = sum(r["harmonic_amplitude"] for r in recent) / 5.0
        avg_index = sum(r["interferometer_index"] for r in recent) / 5.0

        risk_score = min(100.0, avg_index * 50.0 + (avg_amplitude * 10.0))
        mitigation_action = "NONE"

        if risk_score > 75.0:
            mitigation_action = "EMERGENCY_DRIVE_SYNCHRONIZATION_AND_SPEED_DAMPENING"
            logger.warning(f"[{self.mill_id}] CRITICAL RESONANCE RISK DETECTED! Score: {{risk_score:.2f}}")
        elif risk_score > 45.0:
            mitigation_action = "DYNAMIC_PHASE_QUADRATURE_MODULATION"
            logger.info(f"[{self.mill_id}] Elevated harmonic ripple. Applying phase modulation.")

        return {
            "mill_id": self.mill_id,
            "risk_score": risk_score,
            "average_harmonic_amplitude": avg_amplitude,
            "interferometer_index": avg_index,
            "mitigation_action": mitigation_action
        }


if __name__ == "__main__":
    transducer = RollerMillHarmonicTransducer(mill_id="NAIROBI_UNGA_MILL_04")
    # Simulate a noisy torque signal with harmonic variations
    simulated_samples = [100.0 + 5.0 * math.sin(i * 0.2) + 2.0 * math.cos(i * 0.4) for i in range(64)]
    reading = transducer.sample_torque_signal(simulated_samples)
    logger.info(f"Sample Reading: {{reading}}")
    risk_assessment = transducer.predict_resonance_risk()
    logger.info(f"Risk Assessment: {{risk_assessment}}")
