"""Nairobi Commercial Grain Milling Roller Gap Micrometer Synapse Harmonic Pulse Correlation Vibration Audit Synchronizer V27.

Provides real-time telemetry ingestion, harmonic pulse correlation, and gap adjustment recommendations for commercial grain milling roller assemblies.
Designed for high-reliability automated industrial grain processing plants in Nairobi, Kenya.
"""

import math
import time
import statistics
from typing import Dict, List, Any, Optional


class RollerGapMicrometerSynapseSynchronizer:
    """Correlates roller gap micrometers with vibration sensors using harmonic pulse analysis."""

    def __init__(self, mill_id: str, target_gap_microns: float = 250.0, tolerance_microns: float = 5.0):
        self.mill_id = mill_id
        self.target_gap_microns = target_gap_microns
        self.tolerance_microns = tolerance_microns
        self.telemetry_history: List[Dict[str, Any]] = []

    def ingest_sensor_reading(self, gap_microns: float, vibration_amplitude_g: float, harmonic_frequency_hz: float) -> Dict[str, Any]:
        """Ingests sensor telemetry, computes harmonic pulse correlation, and audits health."""
        timestamp = time.time()
        gap_deviation = gap_microns - self.target_gap_microns
        
        # Compute harmonic synapse weight based on vibration and frequency signature
        pulse_correlation_score = math.exp(-abs(gap_deviation) / (self.tolerance_microns * 2.0)) \
                                  * (1.0 / (1.0 + vibration_amplitude_g * (harmonic_frequency_hz / 100.0)))
        
        status = "OPTIMAL"
        if abs(gap_deviation) > self.tolerance_microns or vibration_amplitude_g > 2.5:
            status = "WARNING"
        if abs(gap_deviation) > (self.tolerance_microns * 2.0) or vibration_amplitude_g > 5.0:
            status = "CRITICAL_ADJUSTMENT_REQUIRED"

        reading = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "gap_microns": gap_microns,
            "gap_deviation": gap_deviation,
            "vibration_amplitude_g": vibration_amplitude_g,
            "harmonic_frequency_hz": harmonic_frequency_hz,
            "pulse_correlation_score": round(pulse_correlation_score, 4),
            "status": status
        }

        self.telemetry_history.append(reading)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return reading

    def audit_performance(self) -> Dict[str, Any]:
        """Audits accumulated telemetry history and returns aggregate health metrics."""
        if not self.telemetry_history:
            return {"mill_id": self.mill_id, "status": "NO_DATA"}

        gaps = [r["gap_microns"] for r in self.telemetry_history]
        vibrations = [r["vibration_amplitude_g"] for r in self.telemetry_history]
        scores = [r["pulse_correlation_score"] for r in self.telemetry_history]

        return {
            "mill_id": self.mill_id,
            "samples_audited": len(self.telemetry_history),
            "mean_gap_microns": round(statistics.mean(gaps), 2),
            "mean_vibration_g": round(statistics.mean(vibrations), 4),
            "mean_pulse_correlation": round(statistics.mean(scores), 4),
            "system_health_index": round(statistics.mean(scores) * 100.0, 2)
        }


if __name__ == "__main__":
    synapse = RollerGapMicrometerSynapseSynchronizer(mill_id="NAIROBI_MILL_INDUSTRIAL_01")
    
    # Simulate normal and slight anomaly runs
    test_readings = [
        (250.2, 0.42, 60.0),
        (251.5, 0.85, 60.2),
        (258.0, 3.10, 120.5),
        (250.1, 0.38, 60.0)
    ]

    for gap, vib, freq in test_readings:
        res = synapse.ingest_sensor_reading(gap, vib, freq)
        print(f"Telemetry Audit -> Gap: {res['gap_microns']}um | Status: {res['status']} | Correlation: {res['pulse_correlation_score']}")

    audit = synapse.audit_performance()
    print(f"Final Mill Audit Summary: {audit}")
