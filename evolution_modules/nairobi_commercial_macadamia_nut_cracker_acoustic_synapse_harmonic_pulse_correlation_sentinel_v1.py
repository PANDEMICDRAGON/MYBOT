"""Nairobi Commercial Macadamia Nut Cracker Acoustic Synapse Harmonic Pulse Correlation Sentinel V1."""

import os
import sys
import time
import math
import logging
import json
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [MacadamiaAcousticSentinel]: %(message)s')
logger = logging.getLogger("MacadamiaAcousticSentinel")

class MacadamiaAcousticSentinel:
    """
    Monitors acoustic emission and vibration harmonic pulses from commercial macadamia nut
    cracking machines in industrial facilities across Nairobi, detecting anvil wear and structural anomalies.
    """
    
    def __init__(self, machine_id: str, baseline_frequency_hz: float = 1250.0, anomaly_threshold: float = 0.85):
        self.machine_id = machine_id
        self.baseline_frequency_hz = baseline_frequency_hz
        self.anomaly_threshold = anomaly_threshold
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized MacadamiaAcousticSentinel for machine {machine_id} (Baseline: {baseline_frequency_hz} Hz)")
        
    def ingest_acoustic_pulse(self, sample_id: int, dominant_frequency: float, harmonic_amplitude: float, vibration_rms: float) -> Dict[str, Any]:
        """
        Ingests real-time acoustic sensor data, computes harmonic correlation index, and flags anomalies.
        """
        freq_deviation = abs(dominant_frequency - self.baseline_frequency_hz) / self.baseline_frequency_hz
        harmonic_score = min(1.0, harmonic_amplitude / 100.0)
        vibration_score = min(1.0, vibration_rms / 10.0)
        
        # Composite harmonic pulse correlation index
        correlation_index = max(0.0, 1.0 - (freq_deviation * 0.4 + harmonic_score * 0.3 + vibration_score * 0.3))
        
        is_anomaly = correlation_index < self.anomaly_threshold
        
        telemetry = {
            "sample_id": sample_id,
            "timestamp": time.time(),
            "machine_id": self.machine_id,
            "dominant_frequency": dominant_frequency,
            "harmonic_amplitude": harmonic_amplitude,
            "vibration_rms": vibration_rms,
            "correlation_index": round(correlation_index, 4),
            "is_anomaly": is_anomaly
        }
        
        self.telemetry_history.append(telemetry)
        if is_anomaly:
            logger.warning(f"ANOMALY DETECTED on {self.machine_id}: Correlation Index {correlation_index:.2f} below threshold {self.anomaly_threshold}")
        else:
            logger.info(f"Sample {sample_id} verified. Correlation Index: {correlation_index:.2f}")
            
        return telemetry
        
    def generate_audit_report(self) -> Dict[str, Any]:
        """Generates a comprehensive diagnostic audit report for operator review."""
        total_samples = len(self.telemetry_history)
        if total_samples == 0:
            return {"machine_id": self.machine_id, "status": "NO_DATA"}
            
        anomalies = [t for t in self.telemetry_history if t["is_anomaly"]]
        avg_correlation = sum(t["correlation_index"] for t in self.telemetry_history) / total_samples
        
        report = {
            "machine_id": self.machine_id,
            "total_samples_analyzed": total_samples,
            "total_anomalies_detected": len(anomalies),
            "average_correlation_index": round(avg_correlation, 4),
            "operational_health_status": "CRITICAL_ATTENTION_REQUIRED" if len(anomalies) > (total_samples * 0.1) else "OPTIMAL"
        }
        logger.info(f"Audit Report for {self.machine_id}: Status -> {report['operational_health_status']}")
        return report

if __name__ == "__main__":
    logger.info("Executing MacadamiaAcousticSentinel verification harness...")
    sentinel = MacadamiaAcousticSentinel(machine_id="MAC-CRACKER-NRB-01", baseline_frequency_hz=1250.0)
    
    # Simulate normal and anomalous runs
    sentinel.ingest_acoustic_pulse(1, 1252.0, 45.2, 2.1)
    sentinel.ingest_acoustic_pulse(2, 1248.5, 46.0, 2.0)
    sentinel.ingest_acoustic_pulse(3, 1380.0, 88.5, 8.4)  # Anomalous shock
    
    report = sentinel.generate_audit_report()
    print(json.dumps(report, indent=2))
