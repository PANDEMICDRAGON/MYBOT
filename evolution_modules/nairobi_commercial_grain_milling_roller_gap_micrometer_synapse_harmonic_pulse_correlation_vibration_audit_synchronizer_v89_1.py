import sys
import os
import time
import math
import json
import logging
import threading
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("GrainMillingHarmonicAuditV89")

class RollerGapVibrationAuditor:
    """
    Performs real-time harmonic pulse correlation between roller gap micrometers
    and mechanical vibration sensors in commercial grain milling operations in Nairobi.
    """
    def __init__(self, mill_id: str = "NAIROBI_MILL_ALPHA_01") -> None:
        self.mill_id = mill_id
        self._lock = threading.Lock()
        self._active = False
        self.audit_log: List[Dict[str, Any]] = []
        self.resonance_threshold = 0.85

    def start_audit_loop(self) -> None:
        with self._lock:
            self._active = True
        logger.info(f"Initiated Roller Gap Harmonic Pulse Correlation for mill: {self.mill_id}")

    def stop_audit_loop(self) -> None:
        with self._lock:
            self._active = False
        logger.info(f"Terminated Roller Gap Harmonic Pulse Correlation for mill: {self.mill_id}")

    def evaluate_pulse(self, gap_microns: float, vibration_frequency_hz: float, amplitude_g: float) -> Dict[str, Any]:
        """
        Correlates gap adjustment precision with vibration harmonic distortion.
        """
        # Calculate synthetic harmonic correlation index
        expected_vibration = gap_microns * 0.125
        deviation = abs(vibration_frequency_hz - expected_vibration)
        correlation_score = max(0.0, 1.0 - (deviation / (expected_vibration + 1e-6)))
        
        status = "OPTIMAL"
        if correlation_score < self.resonance_threshold or amplitude_g > 4.5:
            status = "WARNING_RESONANCE_ANOMALY"

        record = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "gap_microns": gap_microns,
            "vibration_frequency_hz": vibration_frequency_hz,
            "amplitude_g": amplitude_g,
            "correlation_score": round(correlation_score, 4),
            "status": status
        }

        with self._lock:
            self.audit_log.append(record)
            if len(self.audit_log) > 1000:
                self.audit_log.pop(0)

        return record

    def get_audit_summary(self) -> Dict[str, Any]:
        with self._lock:
            total_records = len(self.audit_log)
            if total_records == 0:
                return {"mill_id": self.mill_id, "status": "NO_DATA"}
            
            avg_correlation = sum(r["correlation_score"] for r in self.audit_log) / total_records
            anomalies = sum(1 for r in self.audit_log if r["status"] != "OPTIMAL")

        return {
            "mill_id": self.mill_id,
            "total_audited_pulses": total_records,
            "average_correlation": round(avg_correlation, 4),
            "detected_anomalies": anomalies,
            "system_integrity": "SECURE" if anomalies == 0 else "ATTENTION_REQUIRED"
        }

if __name__ == "__main__":
    auditor = RollerGapVibrationAuditor("NAIROBI_CENTRAL_MILL_02")
    auditor.start_audit_loop()
    
    # Simulate feed samples
    sample = auditor.evaluate_pulse(250.0, 31.2, 1.2)
    print(json.dumps(sample, indent=2))
    
    summary = auditor.get_audit_summary()
    print(json.dumps(summary, indent=2))
    auditor.stop_audit_loop()
