"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Micrometer Synapse Harmonic Pulse Correlation Vibration Audit Synchronizer v3

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
Description: Production-grade module for real-time harmonic correlation between high-precision roller gap micrometers and vibration sensors in commercial milling plants.
"""

import math
import statistics
import time
from typing import Dict, List, Optional, Tuple


class RollerGapHarmonicSynchronizer:
    """Synchronizes roller gap telemetry with harmonic vibration pulse data to prevent mill wear."""

    def __init__(self, mill_id: str, nominal_gap_mm: float = 0.15, tolerance_mm: float = 0.02):
        self.mill_id = mill_id
        self.nominal_gap_mm = nominal_gap_mm
        self.tolerance_mm = tolerance_mm
        self.telemetry_buffer: List[Dict[str, float]] = []
        self.anomaly_count = 0

    def ingest_sensor_reading(self, current_gap_mm: float, vibration_amplitude_g: float, harmonic_frequency_hz: float) -> Dict[str, any]:
        timestamp = time.time()
        gap_delta = current_gap_mm - self.nominal_gap_mm
        
        # Calculate harmonic resonance index
        resonance_index = abs(gap_delta) * vibration_amplitude_g * (harmonic_frequency_hz / 50.0)
        
        status = "NOMINAL"
        if abs(gap_delta) > self.tolerance_mm or resonance_index > 0.5:
            status = "SYNAPSE_DRIFT_DETECTED"
            self.anomaly_count += 1

        reading = {
            "timestamp": timestamp,
            "current_gap_mm": current_gap_mm,
            "gap_delta": gap_delta,
            "vibration_amplitude_g": vibration_amplitude_g,
            "harmonic_frequency_hz": harmonic_frequency_hz,
            "resonance_index": resonance_index,
            "status": status
        }
        
        self.telemetry_buffer.append(reading)
        if len(self.telemetry_buffer) > 1000:
            self.telemetry_buffer.pop(0)
            
        return reading

    def generate_audit_report(self) -> Dict[str, any]:
        if not self.telemetry_buffer:
            return {"status": "NO_DATA", "mill_id": self.mill_id}

        gaps = [r["current_gap_mm"] for r in self.telemetry_buffer]
        vibrations = [r["vibration_amplitude_g"] for r in self.telemetry_buffer]
        resonances = [r["resonance_index"] for r in self.telemetry_buffer]

        return {
            "mill_id": self.mill_id,
            "total_samples": len(self.telemetry_buffer),
            "mean_gap_mm": statistics.mean(gaps),
            "stdev_gap_mm": statistics.stdev(gaps) if len(gaps) > 1 else 0.0,
            "mean_vibration_g": statistics.mean(vibrations),
            "max_resonance_index": max(resonances),
            "anomaly_count": self.anomaly_count,
            "health_score": max(0.0, 100.0 - (self.anomaly_count * 5.0))
        }


if __name__ == "__main__":
    print("Initializing RollerGapHarmonicSynchronizer for Nairobi Mill Alpha...")
    sync = RollerGapHarmonicSynchronizer(mill_id="NRB_MILL_ALPHA_01", nominal_gap_mm=0.12)
    
    # Simulate normal and anomalous runs
    test_data = [
        (0.121, 0.05, 50.0),
        (0.122, 0.06, 50.1),
        (0.148, 0.42, 75.5),  # Anomaly
        (0.120, 0.04, 50.0),
    ];
    
    for gap, vib, freq in test_data:
        res = sync.ingest_sensor_reading(gap, vib, freq)
        print(f"Ingested: Gap={gap}mm, Vib={vib}g, Status={res['status']}, Resonance={res['resonance_index']:.4f}")
        
    report = sync.generate_audit_report()
    print("Final Audit Report:", report)
