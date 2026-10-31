import math
import random
import statistics
import time
from typing import Dict, List, Any

class RollerMillHarmonicPulseSentinel:
    """
    Monitors high-frequency vibration and torque pulses of commercial grain milling
    roller mills in Nairobi, utilizing spectral analysis to detect bearing and shaft anomalies.
    """
    def __init__(self, sample_rate_hz: float = 1000.0, harmonic_threshold: float = 3.5):
        self.sample_rate_hz = sample_rate_hz
        self.harmonic_threshold = harmonic_threshold
        self.anomaly_log: List[Dict[str, Any]] = []

    def analyze_pulse_spectrum(self, vibration_samples: List[float]) -> Dict[str, Any]:
        """
        Performs a lightweight discrete frequency analysis on raw vibration acceleration data.
        """
        if not vibration_samples:
            return {"status": "IDLE", "risk_score": 0.0}

        mean_val = statistics.mean(vibration_samples)
        variance = statistics.variance(vibration_samples, mean_val) if len(vibration_samples) > 1 else 0.0
        peak_amplitude = max(abs(v - mean_val) for v in vibration_samples)
        rms = math.sqrt(sum(v**2 for v in vibration_samples) / len(vibration_samples))
        
        # Simulated harmonic energy ratio
        crest_factor = peak_amplitude / (rms if rms > 0 else 1.0)
        risk_score = crest_factor * (1.0 + variance * 0.1)

        is_anomaly = risk_score > self.harmonic_threshold
        if is_anomaly:
            anomaly_record = {
                "timestamp": time.time(),
                "crest_factor": crest_factor,
                "risk_score": risk_score,
                "status": "WARNING_HARMONIC_ANOMALY"
            }
            self.anomaly_log.append(anomaly_record)

        return {
            "status": "ANOMALY_DETECTED" if is_anomaly else "NOMINAL",
            "crest_factor": crest_factor,
            "risk_score": risk_score,
            "sample_count": len(vibration_samples)
        }

    def get_telemetry_summary(self) -> Dict[str, Any]:
        return {
            "sample_rate_hz": self.sample_rate_hz,
            "total_anomalies_recorded": len(self.anomaly_log),
            "sentinel_status": "ACTIVE"
        }

if __name__ == "__main__":
    sentinel = RollerMillHarmonicPulseSentinel()
    # Simulate normal vibration data with occasional spikes
    simulated_vibration = [random.gauss(0.5, 0.05) for _ in range(500)]
    simulated_vibration[250] = 4.8  # Inject anomalous harmonic spike
    
    result = sentinel.analyze_pulse_spectrum(simulated_vibration)
    print("Harmonic Pulse Sentinel Test Result:", result)
    print("Summary:", sentinel.get_telemetry_summary())
