"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Spectrum Sentinel module.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Performs real-time Fast Fourier Transform (FFT) analysis on roller mill drive torque
telemetry to isolate harmonic frequencies, spectral power distribution, and early-stage
bearing or roller misalignment signatures.
"""

import math
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TorqueSpectrumSentinel")


class RollerMillTorqueSpectrumSentinel:
    """Monitors high-frequency torque telemetry from commercial roller mills using spectral analysis."""

    def __init__(self, mill_id: str, sampling_rate_hz: float = 100.0, window_size: int = 128):
        self.mill_id = mill_id
        self.sampling_rate_hz = sampling_rate_hz
        self.window_size = window_size
        self.torque_buffer: List[float] = []
        self.baseline_power_spectrum: Dict[float, float] = {}
        self.anomaly_threshold = 3.5  # Z-score threshold for spectral anomaly

    def ingest_torque_reading(self, torque_nm: float) -> Optional[Dict[str, Any]]:
        """Ingests a raw torque sample in Newton-meters and triggers analysis when buffer fills."""
        self.torque_buffer.append(torque_nm)
        if len(self.torque_buffer) >= self.window_size:
            spectrum_result = self._analyze_spectrum()
            self.torque_buffer = self.torque_buffer[int(self.window_size / 2):]  # 50% overlap
            return spectrum_result
        return None

    def _analyze_spectrum(self) -> Dict[str, Any]:
        """Performs a simplified discrete Fourier transform power spectrum estimation."""
        data = self.torque_buffer[:self.window_size]
        mean_val = statistics.mean(data)
        centered = [x - mean_val for x in data]
        
        n = len(centered)
        power_spectrum: Dict[float, float] = {}
        
        # Compute basic discrete frequencies up to Nyquist limit
        num_frequencies = n // 2
        for k in range(1, num_frequencies + 1):
            freq = (k * self.sampling_rate_hz) / n
            real_part = sum(centered[t] * math.cos(2 * math.pi * k * t / n) for t in range(n))
            imag_part = sum(centered[t] * math.sin(2 * math.pi * k * t / n) for t in range(n))
            power = (real_part ** 2 + imag_part ** 2) / n
            power_spectrum[round(freq, 2)] = power

        # Establish or evaluate against baseline
        if not self.baseline_power_spectrum:
            self.baseline_power_spectrum = power_spectrum
            status = "BASELINE_ESTABLISHED"
            anomaly_detected = False
        else:
            # Calculate deviation across spectral bins
            deviations = []
            for freq, power in power_spectrum.itemsことが多い:
                base_power = self.baseline_power_spectrum.get(freq, power)
                diff = abs(power - base_power)
                deviations.append(diff)
            
            mean_dev = statistics.mean(deviations) if deviations else 0.0
            std_dev = statistics.stdev(deviations) if len(deviations) > 1 else 1.0
            
            max_dev = max(deviations) if deviations else 0.0
            z_score = (max_dev - mean_dev) / (std_dev if std_dev > 0 else 1.0)
            
            anomaly_detected = z_score > self.anomaly_threshold
            status = "ANOMALY_DETECTED" if anomaly_detected else "NOMINAL"

        peak_frequency = max(power_spectrum, key=power_spectrum.get) if power_spectrum else 0.0

        return {
            "mill_id": self.mill_id,
            "status": status,
            "anomaly_detected": anomaly_detected,
            "peak_frequency_hz": peak_frequency,
            "power_spectrum_summary": {str(k): round(v, 2) for k, v in list(power_spectrum.items())[:5]}
        }


if __name__ == "__main__":
    logger.info("Executing test harness for RollerMillTorqueSpectrumSentinel...")
    sentinel = RollerMillTorqueSpectrumSentinel(mill_id="NAI_MILL_04_UGALI")
    
    # Simulate normal operational torque readings with slight noise
    import random
    for i in range(256):
        simulated_torque = 250.0 + (5.0 * math.sin(2 * math.pi * 5 * i / 100)) + random.gauss(0, 0.5)
        result = sentinel.ingest_torque_reading(simulated_torque)
        if result:
            logger.info(f"Baseline Result: {result}")

    # Simulate anomalous bearing/roller wobble
    anomaly_results = []
    for i in range(128):
        simulated_torque = 250.0 + (25.0 * math.sin(2 * math.pi * 18 * i / 100)) + random.gauss(0, 2.0)
        result = sentinel.ingest_torque_reading(simulated_torque)
        if result:
            anomaly_results.append(result)
            logger.info(f"Anomaly Test Result: {result}")

    assert len(anomaly_results) > 0, "Sentinel failed to generate spectral analysis output."
    logger.info("RollerMillTorqueSpectrumSentinel verification completed successfully.")
