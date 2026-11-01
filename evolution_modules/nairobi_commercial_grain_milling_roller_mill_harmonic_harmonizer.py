"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Harmonic Amplitude Phase Quadrature Resolver Interferometer Correlator Estimator Predictor Synchronizer Harmonizer
Designed for real-time industrial milling telemetry, mechanical harmonic suppression, and predictive torque synchronization.
"""

import math
import time
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RollerMillHarmonicHarmonizer")


class RollerMillHarmonicHarmonizer:
    """
    Monitors and synchronizes quadrature resolver interferometer signals and torque ripple harmonics
    for commercial grain roller mills in Nairobi industrial zones.
    """

    def __init__(self, mill_id: str, baseline_frequency_hz: float = 50.0):
        self.mill_id = mill_id
        self.baseline_frequency_hz = baseline_frequency_hz
        self.harmonic_buffer: List[float] = []
        self.phase_quadrature_history: List[Dict[str, float]] = []
        logger.info(f"Initialized RollerMillHarmonicHarmonizer for {{self.mill_id}} at {{self.baseline_frequency_hz}}Hz")

    def ingest_resolver_signal(self, sine_wave: float, cosine_wave: float, timestamp: Optional[float] = None) -> Dict[str, Any]:
        """
        Ingests raw sine and cosine quadrature resolver signals, calculating instantaneous phase and amplitude.
        """
        ts = timestamp or time.time()
        amplitude = math.sqrt(sine_wave**2 + cosine_wave**2)
        phase_rad = math.atan2(sine_wave, cosine_wave)
        phase_deg = math.degrees(phase_rad) % 360.0

        record = {"timestamp": ts, "amplitude": amplitude, "phase_deg": phase_deg}
        self.phase_quadrature_history.append(record)

        if len(self.phase_quadrature_history) > 1000:
            self.phase_quadrature_history.pop(0)

        return record

    def correlate_torque_ripple(self, torque_samples: List[float]) -> Dict[str, Any]:
        """
        Correlates torque ripple harmonics against the baseline frequency to predict potential bearing misalignment or roller chatter.
        """
        if not torque_samples:
            return {"status": "error", "message": "Empty torque sample set."}

        mean_torque = sum(torque_samples) / len(torque_samples)
        variance = sum((t - mean_torque) ** 2 for t in torque_samples) / len(torque_samples)
        std_dev = math.sqrt(variance)

        # Harmonic distortion estimation
        peak_ripple = max(abs(t - mean_torque) for t in torque_samples)
        harmonic_distortion_index = (peak_ripple / (mean_torque + 1e-6)) * 100.0

        synchronization_correction_factor = 1.0 - min(harmonic_distortion_index / 100.0, 0.5)

        result = {
            "mill_id": self.mill_id,
            "mean_torque": mean_torque,
            "torque_std_dev": std_dev,
            "peak_ripple": peak_ripple,
            "harmonic_distortion_index_pct": harmonic_distortion_index,
            "synchronization_correction_factor": synchronization_correction_factor,
            "status": "optimized" if harmonic_distortion_index < 15.0 else "warning_high_ripple"
        }

        logger.info(f"Roller mill {{self.mill_id}} torque correlation completed. HDI: {{harmonic_distortion_index:.2f}}%")
        return result

    def execute_synchronization_sweep(self) -> Dict[str, Any]:
        """
        Executes a full synchronization sweep across all buffered resolver and torque telemetry.
        """
        if not self.phase_quadrature_history:
            return {"status": "insufficient_data"}

        latest_amp = self.phase_quadrature_history[-1]["amplitude"]
        avg_amp = sum(r["amplitude"] for r in self.phase_quadrature_history) / len(self.phase_quadrature_history)
        amplitude_drift = abs(latest_amp - avg_amp)

        return {
            "mill_id": self.mill_id,
            "average_resolver_amplitude": avg_amp,
            "amplitude_drift": amplitude_drift,
            "synchronization_status": "locked" if amplitude_drift < 0.5 else "re-calibrating"
        }


if __name__ == "__main__":
    harmonizer = RollerMillHarmonicHarmonizer(mill_id="NAI-MILL-09")
    # Test resolver ingestion
    sig = harmonizer.ingest_resolver_signal(0.707, 0.707)
    print("Resolver Signal Test:", sig)

    # Test torque correlation
    mock_torques = [102.5, 105.1, 98.2, 103.4, 106.8, 97.9, 104.2]
    corr = harmonizer.correlate_torque_ripple(mock_torques)
    print("Torque Correlation Test:", corr)

    # Test synchronization sweep
    sweep = harmonizer.execute_synchronization_sweep()
    print("Synchronization Sweep Test:", sweep)
