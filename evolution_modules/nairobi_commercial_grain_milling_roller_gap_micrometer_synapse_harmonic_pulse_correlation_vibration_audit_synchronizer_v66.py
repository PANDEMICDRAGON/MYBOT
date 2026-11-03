"""Nairobi Commercial Flour Mill Roller Gap Micrometer Synapse Harmonic Pulse Correlation Vibration Audit Synchronizer V66.1

Designed for real-time industrial milling telemetry correlation in Nairobi, Kenya.
Monitors roller gaps, harmonic vibration pulses, and micrometer tolerances to guarantee
maximum flour extraction efficiency and equipment longevity for Michael Obiero's infrastructure.
"""

import os
import sys
import time
import math
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [RollerGapSynapseV66]: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RollerSensorMetrics:
    mill_id: str
    roller_stage: int
    gap_microns: float
    vibration_hz: float
    harmonic_amplitude: float
    motor_current_amps: float
    temperature_c: float
    timestamp: float = field(default_factory=time.time)

@dataclass
class SynapseAuditReport:
    mill_id: str
    status: str
    correlation_score: float
    anomaly_detected: bool
    recommended_gap_adjustment_microns: float
    audit_notes: List[str]
    timestamp: float = field(default_factory=time.time)

class RollerGapSynapseAuditor:
    """Performs real-time synaptic correlation of mill roller gaps and harmonic vibration telemetry."""

    def __init__(self, mill_id: str, target_gap_microns: float = 150.0, max_vibration_hz: float = 120.0):
        self.mill_id = mill_id
        self.target_gap_microns = target_gap_microns
        self.max_vibration_hz = max_vibration_hz
        self.telemetry_buffer: List[RollerSensorMetrics] = []
        logger.info(f"Initialized RollerGapSynapseAuditor for mill {mill_id} targeting {target_gap_microns}µm gap.")

    def ingest_metrics(self, metrics: RollerSensorMetrics) -> SynapseAuditReport:
        """Ingests incoming sensor metrics, calculates harmonic pulse correlation, and flags anomalies."""
        self.telemetry_buffer.append(metrics)
        if len(self.telemetry_buffer) > 1000:
            self.telemetry_buffer.pop(0)

        notes = []
        anomaly = False
        
        # Gap deviation analysis
        gap_delta = metrics.gap_microns - self.target_gap_microns
        if abs(gap_delta) > 25.0:
            anomaly = True
            notes.append(f"Significant gap deviation detected: {gap_delta:+.2f}µm from target.")

        # Vibration harmonic check
        if metrics.vibration_hz > self.max_vibration_hz:
            anomaly = True
            notes.append(f"High vibration frequency detected: {metrics.vibration_hz}Hz exceeds limit of {self.max_vibration_hz}Hz.")

        # Harmonic pulse correlation calculation (simulated wavelet/fft correlation)
        correlation_score = max(0.0, 1.0 - (abs(gap_delta) / 100.0) - (metrics.vibration_hz / (self.max_vibration_hz * 2)))
        if correlation_score < 0.70:
            anomaly = True
            notes.append(f"Low harmonic pulse correlation score: {correlation_score:.3f}. Inspect roller bearings.")

        # Recommended adjustment
        adjustment = -gap_delta * 0.5 if anomaly else 0.0

        status = "WARNING_ANOMALY_DETECTED" if anomaly else "OPTIMAL_SYNCHRONIZED"
        if anomaly:
            logger.warning(f"[{self.mill_id}] Audit anomaly: {notes}")
        else:
            logger.info(f"[{self.mill_id}] Audit normal. Correlation score: {correlation_score:.3f}")

        return SynapseAuditReport(
            mill_id=self.mill_id,
            status=status,
            correlation_score=correlation_score,
            anomaly_detected=anomaly,
            recommended_gap_adjustment_microns=adjustment,
            audit_notes=notes
        )

    def export_audit_log(self, filepath: str) -> None:
        """Exports internal telemetry buffer to JSON for offline compliance and auditing."""
        data = [asdict(m) for m in self.telemetry_buffer]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Exported {len(data)} telemetry records to {filepath}")

if __name__ == '__main__':
    print("=== Executing Nairobi Roller Gap Micrometer Synapse Harmonic Pulse Correlation Test Harness ===")
    auditor = RollerGapSynapseAuditor(mill_id="NAIROBI_MILL_ALPHA_01", target_gap_microns=140.0, max_vibration_hz=110.0)
    
    # Simulate normal reading
    metric_normal = RollerSensorMetrics(
        mill_id="NAIROBI_MILL_ALPHA_01",
        roller_stage=1,
        gap_microns=141.2,
        vibration_hz=45.5,
        harmonic_amplitude=0.12,
        motor_current_amps=32.4,
        temperature_c=42.1
    );
    report_normal = auditor.ingest_metrics(metric_normal)
    print("Normal Report:", asdict(report_normal))

    # Simulate anomalous reading
    metric_anomaly = RollerSensorMetrics(
        mill_id="NAIROBI_MILL_ALPHA_01",
        roller_stage=1,
        gap_microns=110.0,
        vibration_hz=128.5,
        harmonic_amplitude=0.89,
        motor_current_amps=58.2,
        temperature_c=68.7
    );
    report_anomaly = auditor.ingest_metrics(metric_anomaly)
    print("Anomaly Report:", asdict(report_anomaly))
    print("=== Test Harness Completed Successfully ===")
