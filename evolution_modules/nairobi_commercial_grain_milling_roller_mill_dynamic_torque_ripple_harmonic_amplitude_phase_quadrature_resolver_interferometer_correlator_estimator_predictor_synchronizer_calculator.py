"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Calculator

Designed for precision telemetry processing, phase quadrature alignment, and harmonic torque ripple analysis in Nairobi commercial roller mills.
"""

import math
import time
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillHarmonicCalculator")


class RollerMillHarmonicCalculator:
    """
    Computes phase quadrature alignment, harmonic amplitudes, and torque ripple
    interferometer predictions for industrial roller mills operating in Nairobi.
    """

    def __init__(self, mill_id: str, base_frequency_hz: float = 50.0):
        self.mill_id = mill_id
        self.base_frequency_hz = base_frequency_hz
        self.telemetry_buffer: List[Dict[str, float]] = []

    def ingest_resolver_data(self, timestamp: float, quadrature_sin: float, quadrature_cos: float, torque_nm: float) -> Dict[str, Any]:
        """
        Ingests raw sinusoidal/cosinusoidal resolver signals and torque measurements.
        """
        phase_rad = math.atan2(quadrature_sin, quadrature_cos)
        amplitude = math.sqrt(quadrature_sin**2 + quadrature_cos**2)
        
        record = {
            "timestamp": timestamp,
            "phase_rad": phase_rad,
            "amplitude": amplitude,
            "torque_nm": torque_nm
        }
        self.telemetry_buffer.append(record)
        if len(self.telemetry_buffer) > 1000:
            self.telemetry_buffer.pop(0)
            
        return record

    def calculate_harmonic_profile(self) -> Dict[str, float]:
        """
        Calculates the harmonic amplitude and phase quadrature variance over the telemetry buffer.
        """
        if not self.telemetry_buffer:
            return {"status": "insufficient_data"}
            
        torques = [r["torque_nm"] for r in self.telemetry_buffer]
        mean_torque = sum(torques) / len(torques)
        
        # Compute pseudo-RMS torque ripple
        variance = sum((t - mean_torque) ** 2 for t in torques) / len(torques)
        torque_ripple_rms = math.sqrt(variance)
        
        # Harmonic distortion proxy
        harmonic_amplitude = torque_ripple_rms / (abs(mean_torque) + 1e-6)
        
        return {
            "mill_id": self.mill_id,
            "mean_torque_nm": mean_torque,
            "torque_ripple_rms": torque_ripple_rms,
            "harmonic_amplitude": harmonic_amplitude,
            "sample_count": len(self.telemetry_buffer)
        }

    def predict_synchronization(self, lead_time_sec: float = 1.0) -> Dict[str, Any]:
        """
        Predicts future phase quadrature drift and torque synchronization stability.
        """
        profile = self.calculate_harmonic_profile()
        if profile.get("status") == "insufficient_data":
            return {"prediction": "pending"}
            
        instability_index = profile["harmonic_amplitude"] * lead_time_sec * self.base_frequency_hz
        sync_status = "STABLE" if instability_index < 0.25 else "ATTENTION_REQUIRED"
        
        return {
            "mill_id": self.mill_id,
            "lead_time_sec": lead_time_sec,
            "instability_index": instability_index,
            "sync_status": sync_status
        }


if __name__ == "__main__":
    logger.info("Initializing RollerMillHarmonicCalculator test harness for Nairobi operation...")
    calc = RollerMillHarmonicCalculator(mill_id="NAIROBI_MILL_ALPHA_01")
    
    # Simulate incoming resolver and torque telemetry
    current_time = time.time()
    for i in range(50):
        t = current_time + i * 0.1
        sin_val = math.sin(2 * math.pi * 50 * t) + 0.05 * math.sin(2 * math.pi * 150 * t)
        cos_val = math.cos(2 * math.pi * 50 * t) + 0.05 * math.cos(2 * math.pi * 150 * t)
        torque = 250.0 + 12.5 * math.sin(2 * math.pi * 10 * t)
        calc.ingest_resolver_data(t, sin_val, cos_val, torque)
        
    profile = calc.calculate_harmonic_profile()
    logger.info(f"Harmonic Profile Result: {profile}")
    
    prediction = calc.predict_synchronization(lead_time_sec=2.0)
    logger.info(f"Synchronization Prediction Result: {prediction}")
    logger.info("RollerMillHarmonicCalculator execution completed successfully.")
