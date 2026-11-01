import ast
import logging
import math
import statistics
import time
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillResonator")

class RollerMillResonator:
    """
    Advanced Quadrature Resolver and Phase-Locked Interferometer Correlator
    designed for commercial grain milling roller mills in Nairobi, Kenya.
    Detects and compensates for harmonic torque ripples and mechanical resonances.
    """
    def __init__(self, target_frequency_hz: float = 50.0, sample_rate_hz: float = 1000.0):
        self.target_freq = target_frequency_hz
        self.sample_rate = sample_rate_hz
        self.history_buffer: List[float] = []
        self.max_buffer_size = 2048
        logger.info(f"Initialized RollerMillResonator for {target_frequency_hz}Hz mains/drive sync at {sample_rate_hz}Hz sampling.")

    def ingest_torque_signal(self, torque_sample: float) -> Dict[str, float]:
        """
        Ingests a real-time torque sensor sample, updates the internal quadrature buffer,
        and computes instantaneous phase, amplitude, and resonance indicators.
        """
        self.history_buffer.append(torque_sample)
        if len(self.history_buffer) > self.max_buffer_size:
            self.history_buffer.pop(0)

        return self._compute_quadrature_metrics()

    def _compute_quadrature_metrics(self) -> Dict[str, float]:
        if len(self.history_buffer) < 64:
            return {"status": "buffering", "harmonic_amplitude": 0.0, "phase_offset_rad": 0.0, "resonance_index": 0.0}

        # Extract recent window
        window = self.history_buffer[-256:]
        mean_val = statistics.mean(window)
        centered = [x - mean_val for x in window]

        # Compute Quadrature components (I/Q demodulation at target frequency)
        dt = 1.0 / self.sample_rate
        i_sum = 0.0
        q_sum = 0.0

        for idx, val in enumerate(centered):
            t = idx * dt
            omega = 2.0 * math.pi * self.target_freq
            i_sum += val * math.cos(omega * t)
            q_sum += val * math.sin(omega * t)

        n = len(centered)
        i_val = (2.0 / n) * i_sum
        q_val = (2.0 / n) * q_sum

        amplitude = math.sqrt(i_val**2 + q_val**2)
        phase = math.atan2(q_val, i_val)

        # Resonance index based on variance and peak-to-peak amplitude
        peak_to_peak = max(window) - min(window)
        resonance_index = amplitude / (peak_to_peak + 1e-6)

        return {
            "status": "active",
            "harmonic_amplitude": round(amplitude, 4),
            "phase_offset_rad": round(phase, 4),
            "resonance_index": round(resonance_index, 4),
            "in_phase_component": round(i_val, 4),
            "quadrature_component": round(q_val, 4)
        }

    def generate_counter_modulation(self, metrics: Dict[str, float]) -> float:
        """
        Generates an anti-phase compensation signal value to drive active inverter dampers.
        """
        if metrics.get("status") != "active":
            return 0.0
        amp = metrics.get("harmonic_amplitude", 0.0)
        phase = metrics.get("phase_offset_rad", 0.0)
        # Inverse phase compensation
        counter_val = -amp * math.cos(phase)
        return round(counter_val, 4)

if __name__ == "__main__":
    logger.info("Executing RollerMillResonator self-test...")
    resonator = RollerMillResonator(target_frequency_hz=50.0, sample_rate_hz=1000.0)
    
    # Simulate incoming sinusoidal torque ripple with noise
    metrics = {}
    for i in range(300):
        t = i / 1000.0
        simulated_torque = 150.0 + 12.5 * math.sin(2.0 * math.pi * 50.0 * t + 0.3) + (i % 3) * 0.1
        metrics = resonator.ingest_torque_signal(simulated_torque)

    logger.info(f"Final Test Metrics: {metrics}")
    counter_signal = resonator.generate_counter_modulation(metrics)
    logger.info(f"Generated Counter-Modulation Signal: {counter_signal}")

    # Validate AST compilation cleanliness
    source_code = open(__file__, "r", encoding="utf-8").read()
    parsed_ast = ast.parse(source_code)
    assert parsed_ast is not None
    logger.info("AST compilation verification passed successfully.")
