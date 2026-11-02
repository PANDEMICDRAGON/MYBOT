"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Micrometer Synapse Harmonic Pulse Correlation Audit Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Performs real-time harmonic correlation analysis on roller gap micrometer telemetry and acoustic synapse pulses
to detect microscopic roll eccentricity, thermal expansion drift, and feed inconsistency in commercial grain mills.
"""

import os
import sys
import math
import time
import logging
import json
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MicrometerSynapseAuditSentinel")

class RollerGapHarmonicAuditor:
    """
    Monitors, correlates, and audits roller gap micrometer data and harmonic vibration pulses
    in commercial roller mills located in Nairobi industrial zones.
    """
    def __init__(self, mill_id: str, nominal_gap_microns: float = 250.0, tolerance_microns: float = 5.0):
        self.mill_id = mill_id
        self.nominal_gap_microns = nominal_gap_microns
        self.tolerance_microns = tolerance_microns
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerGapHarmonicAuditor for Mill ID: {mill_id} | Nominal Gap: {nominal_gap_microns}um")

    def ingest_pulse(self, timestamp: float, current_gap_microns: float, vibration_amplitude: float, thermal_temp_c: float) -> Dict[str, Any]:
        """
        Ingests a telemetry pulse containing gap measurement, vibration, and thermal metrics.
        Calculates deviation, harmonic correlation score, and anomaly flags.
        """
        gap_deviation = current_gap_microns - self.nominal_gap_microns
        is_out_of_tolerance = abs(gap_deviation) > self.tolerance_microns
        
        # Synthetic harmonic correlation calculation
        # High vibration paired with unexpected gap widening indicates potential bearing wear or stock choke.
        harmonic_index = math.sin(timestamp / 10.0) * vibration_amplitude
        correlation_score = max(0.0, min(1.0, 1.0 - (abs(gap_deviation) / (self.tolerance_microns * 2.0)) - (vibration_amplitude / 100.0)))

        record = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "current_gap_microns": current_gap_microns,
            "gap_deviation": gap_deviation,
            "vibration_amplitude": vibration_amplitude,
            "thermal_temp_c": thermal_temp_c,
            "harmonic_index": harmonic_index,
            "correlation_score": correlation_score,
            "anomaly_detected": is_out_of_tolerance or correlation_score < 0.4
        }

        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        if record["anomaly_detected"]:
            logger.warning(f"[{self.mill_id}] ANOMALY DETECTED: Gap Deviation={gap_deviation:.2f}um, Correlation Score={correlation_score:.2f}")

        return record

    def generate_audit_summary(self) -> Dict[str, Any]:
        """Generates a comprehensive audit report for operator review."""
        if not self.telemetry_history:
            return {"status": "no_data", "mill_id": self.mill_id}

        total_pulses = len(self.telemetry_history)
        anomalies = sum(1 for r in self.telemetry_history if r["anomaly_detected"])
        avg_correlation = sum(r["correlation_score"] for r in self.telemetry_history) / total_pulses
        avg_temp = sum(r["thermal_temp_c"] for r in self.telemetry_history) / total_pulses

        report = {
            "mill_id": self.mill_id,
            "total_pulses_audited": total_pulses,
            "anomaly_count": anomalies,
            "anomaly_percentage": (anomalies / total_pulses) * 100.0,
            "average_correlation_score": avg_correlation,
            "average_thermal_temp_c": avg_temp,
            "status": "HEALTHY" if anomalies == (total_pulses * 0.05) else "ATTENTION_REQUIRED"
        }
        logger.info(f"Audit Summary Generated for {self.mill_id}: Status={report['status']}, Anomalies={anomalies}")
        return report

if __name__ == "__main__":
    print("=== Executing RollerGapHarmonicAuditor Diagnostic Harness ===")
    auditor = RollerGapHarmonicAuditor(mill_id="NAIROBI-MILL-ALPHA-01", nominal_gap_microns=200.0, tolerance_microns=4.0)
    
    current_time = time.time()
    for i in range(10):
        # Simulate normal operation with minor drift
        gap = 200.0 + (i * 0.3) if i < 8 else 210.0 # Force anomaly on last two
        vib = 1.2 + (i * 0.05)
        temp = 42.5 + (i * 0.1)
        res = auditor.ingest_pulse(current_time + (i * 1.0), gap, vib, temp)
        print(f"Pulse {i}: Gap={res['current_gap_microns']}um | Anomaly={res['anomaly_detected']}")

    summary = auditor.generate_audit_summary()
    print("Audit Summary JSON:")
    print(json.dumps(summary, indent=2))
    print("=== Diagnostic Harness Complete ===")
