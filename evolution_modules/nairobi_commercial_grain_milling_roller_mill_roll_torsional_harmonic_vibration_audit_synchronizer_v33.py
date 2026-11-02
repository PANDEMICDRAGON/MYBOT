"""Nairobi Commercial Grain Milling Roller Mill Roll Torsional Harmonic Vibration Audit Synchronizer v33.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides high-frequency torsional harmonic vibration analysis and real-time synchronization for commercial roller mills in Nairobi grain processing facilities.
"""

import math
import time
import statistics
from typing import Dict, List, Any, Optional


class RollerMillTorsionalSynchronizer:
    """Audits and synchronizes torsional harmonic vibrations across roller mill rolls."""

    def __init__(self, mill_id: str, baseline_rpm: float = 1200.0, harmonic_threshold: float = 0.85):
        self.mill_id = mill_id
        self.baseline_rpm = baseline_rpm
        self.harmonic_threshold = harmonic_threshold
        self.audit_history: List[Dict[str, Any]] = []

    def sample_vibration_sensors(self, raw_readings: List[float]) -> Dict[str, Any]:
        """Process raw accelerometer/torsional sensor data and calculate harmonic index."""
        if not raw_readings:
            raise ValueError("Empty vibration readings provided.")

        mean_val = statistics.mean(raw_readings)
        stdev_val = statistics.stdev(raw_readings) if len(raw_readings) > 1 else 0.0
        peak_val = max(raw_readings)
        
        # Compute synthetic harmonic distortion index (SHDI)
        shdi = min(1.0, (stdev_val / (abs(mean_val) + 1e-6)) * (peak_val / (self.baseline_rpm / 60.0)))
        
        status = "OPTIMAL"
        adjustment_factor = 1.0
        
        if shdi > self.harmonic_threshold:
            status = "CRITICAL_HARMONIC_DEVIATION"
            # Calculate corrective counter-torque phase shift adjustment
            adjustment_factor = max(0.90, min(1.10, 1.0 - (shdi - self.harmonic_threshold)))

        audit_entry = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "mean_vibration": mean_val,
            "peak_vibration": peak_val,
            "shdi": shdi,
            "status": status,
            "adjustment_factor": adjustment_factor
        }
        self.audit_history.append(audit_entry)
        return audit_entry

    def get_synchronization_summary(self) -> Dict[str, Any]:
        """Summarize all historical audits for telemetry broadcast."""
        if not self.audit_history:
            return {"total_audits": 0, "average_shdi": 0.0}

        shdis = [entry["shdi"] for entry in self.audit_history]
        return {
            "total_audits": len(self.audit_history),
            "average_shdi": statistics.mean(shdis),
            "max_shdi": max(shdis),
            "last_status": self.audit_history[-1]["status"]
        }


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Roll Torsional Harmonic Vibration Audit Synchronizer v33...")
    sync = RollerMillTorsionalSynchronizer(mill_id="NAIROBI_MILL_ALPHA_01")
    simulated_readings = [0.12, 0.15, 0.45, 0.89, 0.22, 0.18, 0.77, 0.31]
    result = sync.sample_vibration_sensors(simulated_readings)
    print(f"Audit Result: {result}")
    summary = sync.get_synchronization_summary()
    print(f"Synchronization Summary: {summary}")
    print("Execution completed successfully.")
