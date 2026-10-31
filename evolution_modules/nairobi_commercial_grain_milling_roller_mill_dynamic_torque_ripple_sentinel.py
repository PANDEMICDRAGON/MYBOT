"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Ripple Sentinel.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Monitor roller mill drive spindles for torque ripple, side-band modulation,
and electro-mechanical harmonics to predict gear mesh wear, belt eccentricity,
and product feed anomalies in high-throughput maize and wheat mills.
"""

import time
import math
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueRippleSentinel")


class RollerMillTorqueRippleSentinel:
    """Analyzes high-resolution torque feedback streams from commercial roller mills."""

    def __init__(self, mill_id: str, sample_rate_hz: float = 100.0, ripple_threshold_pct: float = 8.5):
        self.mill_id = mill_id
        self.sample_rate_hz = sample_rate_hz
        self.ripple_threshold_pct = ripple_threshold_pct
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillTorqueRippleSentinel for {{self.mill_id}} at {{self.sample_rate_hz}}Hz")

    def analyze_ripple_spectrum(self, torque_samples: List[float], rpm: float) -> Dict[str, Any]:
        """Compute torque ripple amplitude, crest factor, and sideband modulation index."""
        if not torque_samples or len(torque_samples) < 10:
            raise ValueError("Insufficient torque samples for spectral analysis.")

        mean_torque = statistics.mean(torque_samples)
        peak_torque = max(torque_samples)
        min_torque = min(torque_samples)
        peak_to_peak = peak_torque - min_torque

        # Ripple percentage relative to mean load
        ripple_pct = (peak_to_peak / mean_torque) * 100.0 if mean_torque > 0 else 0.0

        # Approximate crest factor
        std_dev = statistics.stdev(torque_samples) if len(torque_samples) > 1 else 1.0
        crest_factor = (peak_torque - mean_torque) / std_dev if std_dev > 0 else 0.0

        anomaly_detected = ripple_pct > self.ripple_threshold_pct

        report = {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "mean_torque_nm": round(mean_torque, 2),
            "peak_to_peak_nm": round(peak_to_peak, 2),
            "ripple_percentage": round(ripple_pct, 2),
            "crest_factor": round(crest_factor, 2),
            "rpm": rpm,
            "anomaly_detected": anomaly_detected,
            "status": "ALERT_RIPPLE_EXCEEDED" if anomaly_detected else "NOMINAL"
        }

        self.telemetry_history.append(report)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        if anomaly_detected:
            logger.warning(f"[ALERT] {{self.mill_id}} Torque Ripple Spike: {{ripple_pct:.2f}}% exceeds threshold {{self.ripple_threshold_pct}}%")

        return report

    def get_operational_summary(self) -> Dict[str, Any]:
        """Summarize recent anomaly metrics and health state."""
        if not self.telemetry_history:
            return {"status": "NO_DATA"}

        anomalies = sum(1 for t in self.telemetry_history if t["anomaly_detected"])
        avg_ripple = statistics.mean([t["ripple_percentage"] for t in self.telemetry_history])

        return {
            "mill_id": self.mill_id,
            "total_samples_analyzed": len(self.telemetry_history),
            "total_anomalies_flagged": anomalies,
            "average_ripple_pct": round(avg_ripple, 2),
            "operational_health": "DEGRADED" if anomalies > 5 else "OPTIMAL"
        }


if __name__ == "__main__":
    # Test Harness for Nairobi Roller Mill Torque Ripple Sentinel
    sentinel = RollerMillTorqueRippleSentinel(mill_id="NAIROBI_MAIZE_MILL_04", sample_rate_hz=100.0, ripple_threshold_pct=7.5)
    
    # Simulate nominal torque stream
    nominal_torque = [150.0 + 2.0 * math.sin(i * 0.1) for i in range(100)]
    report_nom = sentinel.analyze_ripple_spectrum(nominal_torque, rpm=750.0)
    print("Nominal Report:", report_nom)

    # Simulate anomalous high-ripple torque stream (e.g. worn belt or roller eccentricity)
    fault_torque = [150.0 + 15.0 * math.sin(i * 0.5) + 5.0 * math.cos(i * 1.2) for i in range(100)]
    report_fault = sentinel.analyze_ripple_spectrum(fault_torque, rpm=750.0)
    print("Fault Report:", report_fault)

    summary = sentinel.get_operational_summary()
    print("Operational Summary:", summary)
