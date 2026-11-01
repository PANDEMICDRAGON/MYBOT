"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude
Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Evaluator

Implements real-time analysis of roller mill drive spindles using quadrature phase-locked loop
interferometry, harmonic distortion estimation, and torque ripple prediction to protect industrial
grain milling equipment in Nairobi, Kenya.
"""

import math
import random
import time
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueEvaluator")

class RollerMillTorqueRippleEvaluator:
    """
    Evaluates dynamic torque ripple harmonics, phase quadrature signals, and interferometer
    feedback loops for high-speed commercial grain milling roller mills.
    """
    def __init__(self, mill_id: str, nominal_rpm: float = 1200.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.sampling_rate_hz = 1000.0
        self.harmonic_orders = [1, 2, 3, 6, 12]
        logger.info(f"Initialized Torque Ripple Evaluator for Mill {self.mill_id} at {nominal_rpm} RPM.")

    def acquire_quadrature_samples(self, duration_sec: float = 0.1) -> Dict[str, List[float]]:
        """
        Simulates high-frequency quadrature encoder and resolver interferometer feeds.
        """
        num_samples = int(self.sampling_rate_hz * duration_sec)
        sin_wave = []
        cos_wave = []
        torque_ripple = []
        
        base_freq = (self.nominal_rpm / 60.0) * 2.0 * math.pi
        for i in range(num_samples):
            t = i / self.sampling_rate_hz
            phase = base_freq * t
            # Introduce simulated harmonic noise and minor mechanical jitter
            noise = random.gauss(0, 0.02)
            harmonic_distortion = 0.05 * math.sin(6 * phase) + 0.02 * math.cos(12 * phase)
            
            s = math.sin(phase) + noise
            c = math.cos(phase) + noise
            tr = 100.0 + 15.0 * math.sin(3 * phase + 0.5) + harmonic_distortion * 50.0 + (noise * 10)
            
            sin_wave.append(s)
            cos_wave.append(c)
            torque_ripple.append(tr)

        return {
            "sin": sin_wave,
            "cos": cos_wave,
            "torque_ripple": torque_ripple
        }

    def compute_harmonic_amplitude_phase(self, torque_signal: List[float]) -> Dict[str, Any]:
        """
        Computes harmonic amplitudes and phase angles via discrete quadrature correlation.
        """
        n = len(torque_signal)
        if n == 0:
            return {"status": "error", "message": "Empty signal payload."}

        mean_val = sum(torque_signal) / n
        results = {}

        for order in self.harmonic_orders:
            real_part = 0.0
            imag_part = 0.0
            for i, val in enumerate(torque_signal):
                angle = (2.0 * math.pi * order * i) / n
                dev = val - mean_val
                real_part += dev * math.cos(angle)
                imag_part += dev * math.sin(angle)

            amplitude = (2.0 / n) * math.sqrt(real_part**2 + imag_part**2)
            phase_rad = math.atan2(-imag_part, real_part)
            results[f"harmonic_{order}_amplitude"] = round(amplitude, 4)
            results[f"harmonic_{order}_phase_deg"] = round(math.degrees(phase_rad), 2)

        results["mean_torque"] = round(mean_val, 2)
        results["status"] = "nominal"
        return results

    def evaluate_and_synchronize(self) -> Dict[str, Any]:
        """
        Executes full acquisition, interferometer correlation, harmonic extraction,
        and predictive synchronization check.
        """
        raw_data = self.acquire_quadrature_samples(0.1)
        analysis = self.compute_harmonic_amplitude_phase(raw_data["torque_ripple"])
        
        # Check threshold safety for primary harmonic anomaly
        primary_amp = analysis.get("harmonic_3_amplitude", 0.0)
        safety_status = "SECURE"
        action = "NONE"
        
        if primary_amp > 18.0:
            safety_status = "WARNING"
            action = "DAMPEN_INVERTER_FEED_RATE"
        elif primary_amp > 25.0:
            safety_status = "CRITICAL"
            action = "EMERGENCY_ROLLER_DECOUPLE"

        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "safety_status": safety_status,
            "recommended_action": action,
            "analysis": analysis
        }

if __name__ == "__main__":
    evaluator = RollerMillTorqueRippleEvaluator("MILL-NRB-04", 1200.0)
    report = evaluator.evaluate_and_synchronize()
    logger.info(f"Evaluation Complete: {report}")
