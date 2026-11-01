"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Decoder

Designed for real-time telemetry processing of industrial roller mill spindles in Nairobi grain mills.
Extracts quadrature phase components, interferometer fringe shifts, and high-frequency torque anomalies.
"""

import math
import time
import logging
import statistics
from typing import Dict, List, Tuple, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillDecoder")

class RollerMillDecoderException(Exception):
    """Custom exception for roller mill quadrature decoding anomalies."""
    pass

class RollerMillQuadratureDecoder:
    """
    Decodes quadrature resolver signals and interferometer fringe patterns from commercial roller mill drives.
    """
    def __init__(self, mill_id: str, sample_rate_hz: float = 10000.0):
        self.mill_id = mill_id
        self.sample_rate_hz = sample_rate_hz
        self.phase_history: List[float] = []
        self.amplitude_history: List[float] = []
        logger.info(f"Initialized RollerMillQuadratureDecoder for mill {mill_id} at {sample_rate_hz} Hz")

    def decode_signals(self, sine_wave: List[float], cosine_wave: List[float], interferometer_fringe: List[float]) -> Dict[str, Any]:
        """
        Processes raw sine/cosine resolver feeds and interferometer fringe shifts to compute instantaneous phase angle,
        amplitude envelope, and harmonic torque ripple correlation.
        """
        if len(sine_wave) != len(cosine_wave) or len(sine_wave) != len(interferometer_fringe):
            raise RollerMillDecoderException("Signal array dimensions do not match for quadrature resolution.")
        
        if not sine_wave:
            raise RollerMillDecoderException("Empty signal arrays provided.")

        decoded_phases = []
        decoded_amplitudes = []
        interferometer_corrections = []

        for s, c, fringe in zip(sine_wave, cosine_wave, interferometer_fringe):
            # Compute phase via arctan2
            phase = math.atan2(s, c)
            # Compute envelope amplitude
            amp = math.sqrt(s**2 + c**2)
            # Apply interferometer optical fringe correction multiplier
            corrected_phase = phase + (fringe * 0.001)
            
            decoded_phases.append(corrected_phase)
            decoded_amplitudes.append(amp)
            interferometer_corrections.append(fringe)

        mean_amp = statistics.mean(decoded_amplitudes)
        phase_jitter = statistics.pstdev(decoded_phases) if len(decoded_phases) > 1 else 0.0
        
        self.phase_history.extend(decoded_phases[-100:])
        self.amplitude_history.extend(decoded_amplitudes[-100:])

        # Keep history bounded
        if len(self.phase_history) > 1000:
            self.phase_history = self.phase_history[-1000:]
        if len(self.amplitude_history) > 1000:
            self.amplitude_history = self.amplitude_history[-1000:]

        anomaly_detected = phase_jitter > 0.15 or mean_amp < 0.5

        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "mean_amplitude": mean_amp,
            "phase_jitter_radians": phase_jitter,
            "anomaly_detected": anomaly_detected,
            "status": "CRITICAL_ATTENTION_REQUIRED" if anomaly_detected else "OPTIMAL"
        }

    def estimate_torque_ripple(self) -> float:
        """Estimates current dynamic torque ripple harmonic distortion from recent amplitudes."""
        if len(self.amplitude_history) < 10:
            return 0.0
        return statistics.pstdev(self.amplitude_history) / (statistics.mean(self.amplitude_history) + 1e-9)

if __name__ == "__main__":
    decoder = RollerMillDecoderEngineer = RollerMillQuadratureDecoder(mill_id="NAI_MILL_04_UGALI")
    # Simulate raw resolver signals
    import random
    s_wave = [math.sin(i * 0.1) + random.uniform(-0.02, 0.02) for i in range(200)]
    c_wave = [math.cos(i * 0.1) + random.uniform(-0.02, 0.02) for i in range(200)]
    f_wave = [random.gauss(0, 1) for _ in range(200)]
    
    result = decoder.decode_signals(s_wave, c_wave, f_wave)
    ripple = decoder.estimate_torque_ripple()
    logger.info(f"Test Harness Execution Complete. Result: {result}, Torque Ripple Index: {ripple:.4f}")
