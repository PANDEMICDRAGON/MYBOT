import math
import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueHarmonicAmplificationSentinel")

class RollerMillTorqueHarmonicAmplificationSentinel:
    """
    Monitors and suppresses harmonic torsional amplification in commercial grain milling roller mills.
    Protects drive shafts, gearboxes, and fluted rolls from catastrophic resonance in Nairobi mills.
    """
    def __init__(self, mill_id: str, rated_torque_nm: float = 1200.0, harmonic_threshold_hz: float = 65.0):
        self.mill_id = mill_id
        self.rated_torque_nm = rated_torque_nm
        self.harmonic_threshold_hz = harmonic_threshold_hz
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"[INIT] RollerMillTorqueHarmonicAmplificationSentinel active for mill: {mill_id}")

    def analyze_torque_waveform(self, torque_samples: List[float], sampling_rate_hz: float) -> Dict[str, Any]:
        """
        Analyzes torque signal samples to detect harmonic peaks and torsional oscillation risks.
        """
        if not torque_samples:
            return {"status": "error", "message": "Empty torque sample set."}

        peak_torque = max(torque_samples)
        mean_torque = sum(torque_samples) / len(torque_samples)
        torque_ripple_ratio = (peak_torque - mean_torque) / (mean_torque if mean_torque > 0 else 1.0)

        # FFT approximation for dominant harmonic frequency
        n = len(torque_samples)
        frequencies = [i * (sampling_rate_hz / n) for i in range(n // 2)]
        fft_magnitudes = [abs(sum(t * math.cos(2 * math.pi * i * j / n) for j, t in enumerate(torque_samples))) / n for i in range(n // 2)]
        
        max_mag = 0.0
        dominant_freq = 0.0
        for f, m in zip(frequencies, fft_magnitudes):
            if m > max_mag and f > 1.0:  # Ignore DC component
                max_mag = m
                dominant_freq = f

        harmonic_violation = dominant_freq >= self.harmonic_threshold_hz or torque_ripple_ratio > 0.35
        
        report = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "peak_torque_nm": peak_torque,
            "mean_torque_nm": mean_torque,
            "torque_ripple_ratio": round(torque_ripple_ratio, 4),
            "dominant_frequency_hz": round(dominant_freq, 2),
            "harmonic_violation": harmonic_violation,
            "mitigation_action": "APPLY_DYNAMIC_DAMPENING_TORQUE_INVERTER" if harmonic_violation else "NOMINAL"
        }

        self.telemetry_history.append(report)
        if harmonic_violation:
            logger.warning(f"[WARNING] Harmonic amplification anomaly detected on {self.mill_id}! Freq: {dominant_freq}Hz, Ripple: {torque_ripple_ratio}")
        else:
            logger.info(f"[INFO] {self.mill_id} torque harmonics within nominal bounds.")

        return report

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "total_samples_analyzed": len(self.telemetry_history),
            "rated_torque_nm": self.rated_torque_nm,
            "harmonic_threshold_hz": self.harmonic_threshold_hz
        }

if __name__ == "__main__":
    sentinel = RollerMillTorqueHarmonicAmplificationSentinel(mill_id="NAIROBI_MILL_ALPHA_04")
    # Simulate smooth vs resonant torque samples
    nominal_samples = [1150.0 + 20.0 * math.sin(i * 0.1) for i in range(128)]
    resonant_samples = [1200.0 + 450.0 * math.sin(i * 1.5) + 200.0 * math.cos(i * 3.0) for i in range(128)]
    
    print("--- Testing Nominal Torque Waveform ---")
    print(sentinel.analyze_torque_waveform(nominal_samples, 256.0))
    
    print("--- Testing Resonant Torsional Waveform ---")
    print(sentinel.analyze_torque_waveform(resonant_samples, 256.0))
    print(sentinel.get_diagnostics())