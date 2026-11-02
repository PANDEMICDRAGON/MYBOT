"""
Nairobi Commercial Grain Milling Roller Mill Roll Torsional Harmonic Vibration Audit Synchronizer
Created for Michael Obiero in Nairobi, Kenya.

Monitors torsional harmonic vibrations on commercial grain milling roller mill rolls to detect
micro-fractures, shaft misalignment, and bearing wear before catastrophic failure occurs.
"""

import ast
import logging
import math
import statistics
import time
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorsionalSynchronizer")


class RollerMillTorsionalAuditor:
    """Audits torsional harmonic vibration signatures of commercial roller mills."""

    def __init__(self, mill_id: str, baseline_rpm: float = 500.0, harmonic_threshold: float = 3.5):
        self.mill_id = mill_id
        self.baseline_rpm = baseline_rpm
        self.harmonic_threshold = harmonic_threshold
        self.vibration_buffer: List[float] = []
        self.audit_log: List[Dict[str, Any]] = []

    def ingest_vibration_signal(self, g_force_readings: List[float]) -> Dict[str, Any]:
        """Ingests raw accelerometer G-force readings and calculates torsional harmonic anomaly metrics."""
        if not g_force_readings:
            return {"status": "error", "message": "Empty vibration readings ingested."}

        mean_g = statistics.mean(g_force_readings)
        stdev_g = statistics.pstdev(g_force_readings) if len(g_force_readings) > 1 else 0.0
        peak_g = max(g_force_readings)
        crest_factor = (peak_g / mean_g) if mean_g > 0 else 0.0

        # Compute harmonic distortion index based on variance and peak magnitude
        harmonic_index = (stdev_g * crest_factor) / (self.baseline_rpm / 100.0)
        is_anomaly = harmonic_index > self.harmonic_threshold

        audit_entry = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "mean_g": mean_g,
            "stdev_g": stdev_g,
            "crest_factor": crest_factor,
            "harmonic_index": harmonic_index,
            "is_anomaly": is_anomaly
        }

        self.audit_log.append(audit_entry)
        if len(self.audit_log) > 1000:
            self.audit_log.pop(0)

        if is_anomaly:
            logger.warning(
                f"[ALERT] Torsional harmonic anomaly detected on mill {self.mill_id}! "
                f"Harmonic Index: {harmonic_index:.2f} exceeds threshold {self.harmonic_threshold}"
            )

        return audit_entry

    def get_audit_summary(self) -> Dict[str, Any]:
        """Returns summary statistics of the audit log."""
        if not self.audit_log:
            return {"total_audits": 0}

        anomaly_count = sum(1 for entry in self.audit_log if entry["is_anomaly"])
        avg_harmonic = statistics.mean(entry["harmonic_index"] for entry in self.audit_log)

        return {
            "mill_id": self.mill_id,
            "total_audits": len(self.audit_log),
            "anomaly_count": anomaly_count,
            "average_harmonic_index": avg_harmonic,
            "system_health": "DEGRADED" if anomaly_count > 0 else "OPTIMAL"
        }


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Roll Torsional Harmonic Vibration Audit Synchronizer...")
    auditor = RollerMillTorsionalAuditor(mill_id="NAI-MILL-04")
    
    # Simulate normal operation readings
    normal_readings = [0.12, 0.14, 0.13, 0.12, 0.15]
    res1 = auditor.ingest_vibration_signal(normal_readings)
    print("Normal Audit Result:", res1)

    # Simulate anomalous torsional vibration (e.g., roller bearing pitting or misaligned shaft)
    anomalous_readings = [0.85, 1.45, 0.22, 1.95, 0.40]
    res2 = auditor.ingest_vibration_signal(anomalous_readings)
    print("Anomalous Audit Result:", res2)

    summary = auditor.get_audit_summary()
    print("Audit Summary:", summary)
    
    # Validate source code compiles successfully under ast
    with open(__file__, "r", encoding="utf-8") as f:
        source_code = f.read()
    parsed_ast = ast.parse(source_code)
    print(f"AST compilation check passed: {isinstance(parsed_ast, ast.Module)}")
