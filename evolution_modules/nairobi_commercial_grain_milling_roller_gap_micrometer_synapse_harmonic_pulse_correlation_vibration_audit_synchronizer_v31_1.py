"""
Nairobi Commercial Grain Milling Roller Gap Micrometer Synapse Harmonic Pulse Correlation Vibration Audit Synchronizer V31.1

Provides real-time micrometer gap telemetry, harmonic vibration correlation, and adaptive roller alignment
for industrial grain milling operations in Nairobi, Kenya.
"""

import math
import statistics
import time
from typing import Dict, List, Optional


class RollerGapMicrometerSynapseSynchronizer:
    """Audits and synchronizes roller gap micrometer readings against harmonic vibration pulses."""

    def __init__(self, mill_id: str, target_gap_microns: float = 150.0, tolerance_microns: float = 2.5):
        self.mill_id = mill_id
        self.target_gap_microns = target_gap_microns
        self.tolerance_microns = tolerance_microns
        self.telemetry_buffer: List[Dict[str, float]] = []

    def ingest_sensor_telemetry(self, left_gap: float, right_gap: float, vibration_hz: float, harmonic_amplitude: float) -> Dict[str, any]:
        """Ingests live micrometer gap and vibration sensor readings."""
        timestamp = time.time()
        avg_gap = (left_gap + right_gap) / 2.0
        gap_deviation = abs(avg_gap - self.target_gap_microns)
        
        # Calculate harmonic correlation index
        correlation_score = math.exp(- (gap_deviation / self.tolerance_microns) ** 2) * max(0.0, 1.0 - (vibration_hz / 1000.0))
        
        record = {
            "timestamp": timestamp,
            "left_gap": left_gap,
            "right_gap": right_gap,
            "avg_gap": avg_gap,
            "vibration_hz": vibration_hz,
            "harmonic_amplitude": harmonic_amplitude,
            "correlation_score": correlation_score,
            "in_tolerance": gap_deviation <= self.tolerance_microns
        }
        
        self.telemetry_buffer.append(record)
        if len(self.telemetry_buffer) > 1000:
            self.telemetry_buffer.pop(0)
            
        return record

    def evaluate_sync_status(self) -> Dict[str, any]:
        """Evaluates overall synchronization health of the milling assembly."""
        if not self.telemetry_buffer:
            return {"status": "NO_DATA", "health_index": 0.0}
            
        recent = self.telemetry_buffer[-50:]
        avg_correlation = statistics.mean([r["correlation_score"] for r in recent])
        tolerance_compliance = sum(1 for r in recent if r["in_tolerance"]) / len(recent)
        
        status = "OPTIMAL"
        if avg_correlation < 0.75 or tolerance_compliance < 0.90:
            status = "RECALIBRATION_REQUIRED"
            
        return {
            "mill_id": self.mill_id,
            "status": status,
            "average_correlation": round(avg_correlation, 4),
            "tolerance_compliance_rate": round(tolerance_compliance * 100, 2),
            "sample_count": len(recent)
        }


if __name__ == "__main__":
    synapse = RollerGapMicrometerSynapseSynchronizer(mill_id="NAIROBI_MILL_ALPHA_01")
    
    # Simulate ingestion
    for i in range(10):
        res = synapse.ingest_sensor_telemetry(
            left_gap=149.5 + (i * 0.1),
            right_gap=150.1 - (i * 0.05),
            vibration_hz=45.2 + i,
            harmonic_amplitude=0.12
        )
    
    audit = synapse.evaluate_sync_status()
    print(f"[V31.1 AUDIT SUCCESS] Mill ID: {audit['mill_id']} | Status: {audit['status']} | Compliance: {audit['tolerance_compliance_rate']}%")
