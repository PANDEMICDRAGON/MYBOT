"""Nairobi Commercial Grain Milling Roller Mill Roll Torsional Harmonic Vibration Audit Synchronizer v3.

Provides real-time telemetry processing, harmonic anomaly detection, and automated mitigation
protocols for industrial grain roller mills operating in Nairobi, Kenya.
"""

import ast
import json
import logging
import math
import statistics
import time
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("RollerTorsionalHarmonicAuditSyncV3")


class RollerTorsionalHarmonicAuditSynchronizerV3:
    """Advanced torsional vibration auditor and harmonic synchronizer for roller mills."""

    def __init__(self, mill_id: str, baseline_hz: float = 50.0, tolerance_pct: float = 5.0):
        self.mill_id = mill_id
        self.baseline_hz = baseline_hz
        self.tolerance_pct = tolerance_pct
        self.vibration_buffer: List[float] = []
        self.audit_log: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerTorsionalHarmonicAuditSynchronizerV3 for mill: {mill_id}")

    def ingest_vibration_sample(self, frequency_hz: float, amplitude_mm_s: float, temperature_c: float) -> Dict[str, Any]:
        """Ingests a real-time vibration sample, analyzes harmonic deviation, and returns health status."""
        timestamp = time.time()
        self.vibration_buffer.append(frequency_hz)
        if len(self.vibration_buffer) > 100:
            self.vibration_buffer.pop(0)

        deviation = abs(frequency_hz - self.baseline_hz) / self.baseline_hz * 100.0
        is_anomalous = deviation > self.tolerance_pct or amplitude_mm_s > 4.5 or temperature_c > 85.0

        status = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "frequency_hz": frequency_hz,
            "amplitude_mm_s": amplitude_mm_s,
            "temperature_c": temperature_c,
            "deviation_pct": round(deviation, 2),
            "anomalous": is_anomalous,
            "action_required": "SLOW_ROLL_FEED" if is_anomalous else "NORMAL_OPERATION"
        }

        self.audit_log.append(status)
        if is_anomalous:
            logger.warning(f"[{self.mill_id}] Torsional harmonic anomaly detected! Deviation: {deviation:.2f}%, Amp: {amplitude_mm_s} mm/s, Temp: {temperature_c}C")
        return status

    def compute_harmonic_entropy(self) -> float:
        """Computes rolling frequency variance/entropy to detect micro-fractures in roll shafts."""
        if len(self.vibration_buffer) < 5:
            return 0.0
        return float(statistics.pstdev(self.vibration_buffer))

    def export_audit_summary(self) -> str:
        """Exports comprehensive audit telemetry as a structured JSON string."""
        summary = {
            "mill_id": self.mill_id,
            "samples_processed": len(self.audit_log),
            "harmonic_entropy": round(self.compute_harmonic_entropy(), 4),
            "last_status": self.audit_log[-1] if self.audit_log else None
        }
        return json.dumps(summary, indent=2)


if __name__ == "__main__":
    print("Executing self-test for RollerTorsionalHarmonicAuditSynchronizerV3...")
    synchronizer = RollerTorsionalHarmonicAuditSynchronizerV3(mill_id="NAI_UGALI_MILL_04")
    
    # Simulate normal and anomalous telemetry
    sample1 = synchronizer.ingest_vibration_sample(frequency_hz=50.2, amplitude_mm_s=1.2, temperature_c=62.5)
    sample2 = synchronizer.ingest_vibration_sample(frequency_hz=58.9, amplitude_mm_s=5.1, temperature_c=88.0)
    
    assert sample1["anomalous"] is False, "Sample 1 should be normal"
    assert sample2["anomalous"] is True, "Sample 2 should be flagged as anomalous"
    
    print(synchronizer.export_audit_summary())
    print("Self-test completed successfully. Code compiles and executes cleanly.")
