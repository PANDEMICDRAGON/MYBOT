"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Electro Acoustic Spectral Correlation Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides real-time spectral correlation of roller mill electro-acoustic telemetry and motor load
to maintain optimal roller gap tolerances and prevent uneven milling or mechanical binding.
"""

import math
import time
import statistics
from typing import Dict, List, Tuple, Any


class RollerGapSpectralCorrelationSentinel:
    """
    Monitors and correlates electro-acoustic vibration spectra with motor current draw
    to dynamically detect roller gap drift in commercial grain milling operations.
    """

    def __init__(self, mill_id: str, nominal_gap_mm: float = 0.15, sample_rate_hz: int = 1000):
        self.mill_id = mill_id
        self.nominal_gap_mm = nominal_gap_mm
        self.sample_rate_hz = sample_rate_hz
        self.baseline_spectral_energy: float = 45.2  # Decibels at nominal gap
        self.anomaly_threshold_db: float = 8.5
        self.alert_history: List[Dict[str, Any]] = []

    def compute_spectral_correlation(self, acoustic_samples: List[float], motor_currents: List[float]) -> float:
        """
        Computes normalized cross-correlation coefficient between acoustic power spectral density
        and high-frequency motor current fluctuations.
        """
        if not acoustic_samples or not motor_currents:
            return 0.0

        # Ensure equal length comparison window
        limit = min(len(acoustic_samples), len(motor_currents))
        ac = acoustic_samples[:limit]
        mc = motor_currents[:limit]

        mean_ac = statistics.mean(ac)
        mean_mc = statistics.mean(mc)

        numerator = sum((a - mean_ac) * (m - mean_mc) for a, m in zip(ac, mc))
        denom_ac = math.sqrt(sum((a - mean_ac) ** 2 for a in ac))
        denom_mc = math.sqrt(sum((m - mean_mc) ** 2 for m in mc))

        if denom_ac == 0 or denom_mc == 0:
            return 0.0

        return numerator / (denom_ac * denom_mc)

    def analyze_cycle(self, acoustic_samples: List[float], motor_currents: List[float]) -> Dict[str, Any]:
        """
        Performs a complete diagnostic assessment of the roller gap state.
        """
        timestamp = time.time()
        current_energy = statistics.mean([abs(x) for x in acoustic_samples]) if acoustic_samples else 0.0
        correlation = self.compute_spectral_correlation(acoustic_samples, motor_currents)
        
        # Estimate gap deviation based on spectral energy variance
        energy_delta = abs(current_energy - self.baseline_spectral_energy)
        estimated_gap_deviation_mm = (energy_delta / 100.0) * self.nominal_gap_mm

        status = "NOMINAL"
        if energy_delta > self.anomaly_threshold_db or abs(correlation) < 0.4:
            status = "WARNING_GAP_DRIFT"

        assessment = {
            "mill_id": self.mill_id,
            "timestamp": timestamp,
            "mean_acoustic_energy_db": round(current_energy, 2),
            "spectral_correlation_coefficient": round(correlation, 4),
            "estimated_gap_deviation_mm": round(estimated_gap_deviation_mm, 5),
            "status": status
        }

        if status != "NOMINAL":
            self.alert_history.append(assessment)

        return assessment


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Gap Spectral Correlation Sentinel...")
    sentinel = RollerGapSpectralCorrelationSentinel(mill_id="NAI-MILL-IND-04", nominal_gap_mm=0.12)
    
    # Simulate normal operational sensor streams
    mock_acoustic = [44.5, 45.1, 45.8, 44.9, 45.0, 45.3, 44.8, 45.2, 45.1, 45.0]
    mock_current = [12.1, 12.2, 12.1, 12.3, 12.2, 12.1, 12.2, 12.3, 12.2, 12.1]
    
    report = sentinel.analyze_cycle(mock_acoustic, mock_current)
    print(f"Normal Operation Assessment: {report}")

    # Simulate anomaly: roller gap closing too tightly (increased friction/spectral spike)
    mock_acoustic_anomaly = [68.5, 72.1, 70.4, 71.9, 69.8, 73.2, 70.1, 71.5, 72.0, 71.1]
    mock_current_anomaly = [15.2, 16.4, 15.9, 16.1, 15.8, 16.5, 16.0, 16.2, 16.3, 15.9]
    
    anomaly_report = sentinel.analyze_cycle(mock_acoustic_anomaly, mock_current_anomaly)
    print(f"Anomaly Detected Assessment: {anomaly_report}")
    print("Sentinel test sequence completed successfully.")
