"""Nairobi Commercial Grain Milling Roller Mill Roll Torsional Harmonic Vibration Audit Synchronizer v2."""

import logging
import time
import math
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TorsionalHarmonicSynchronizerV2")

class TorsionalHarmonicSynchronizerV2:
    """Audits and synchronizes torsional harmonic vibrations in commercial roller mills."""
    
    def __init__(self, mill_id: str, baseline_rpm: float = 750.0):
        self.mill_id = mill_id
        self.baseline_rpm = baseline_rpm
        self.resonance_threshold = 3.5  # Spectral kurtosis threshold
        self.audit_log: List[Dict[str, Any]] = []

    def measure_torsion(self, raw_vibration_signal: List[float]) -> Dict[str, Any]:
        """Analyze raw vibration signal for torsional harmonic anomalies."""
        if not raw_vibration_signal:
            return {"status": "error", "message": "Empty signal received."}
        
        mean_val = sum(raw_vibration_signal) / len(raw_vibration_signal)
        variance = sum((x - mean_val) ** 2 for x in raw_vibration_signal) / len(raw_vibration_signal)
        std_dev = math.sqrt(variance) if variance > 0 else 1e-6
        
        # Compute fourth standardized moment (kurtosis)
        fourth_moment = sum((x - mean_val) ** 4 for x in raw_vibration_signal) / len(raw_vibration_signal)
        kurtosis = fourth_moment / (std_dev ** 4)
        
        torsion_stress_index = kurtosis * (self.baseline_rpm / 750.0)
        anomaly_detected = torsion_stress_index > self.resonance_threshold
        
        audit_entry = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "kurtosis": kurtosis,
            "torsion_stress_index": torsion_stress_index,
            "anomaly_detected": anomaly_detected
        }
        self.audit_log.append(audit_entry)
        
        if anomaly_detected:
            logger.warning(f"[TORSION ALERT] Mill {self.mill_id} exhibiting torsional harmonic anomaly! Stress Index: {torsion_stress_index:.2f}")
        else:
            logger.info(f"[TORSION OK] Mill {self.mill_id} operating within nominal parameters. Stress Index: {torsion_stress_index:.2f}")
            
        return audit_entry

    def get_audit_summary(self) -> Dict[str, Any]:
        total_audits = len(self.audit_log)
        anomalies = sum(1 for entry in self.audit_log if entry["anomaly_detected"])
        return {
            "mill_id": self.mill_id,
            "total_audits": total_audits,
            "total_anomalies": anomalies,
            "health_score": max(0.0, 100.0 - (anomalies / max(1, total_audits) * 100.0))
        }

if __name__ == "__main__":
    synchronizer = TorsionalHarmonicSynchronizerV2("NAIROBI_ROLLER_MILL_ALPHA_01")
    # Simulate normal vibration signals followed by a resonant spike
    normal_signal = [0.1, -0.1, 0.05, -0.05, 0.08, -0.08, 0.02]
    resonant_signal = [1.2, -1.5, 3.4, -4.1, 2.9, -3.2, 5.0, -4.8]
    
    synchronizer.measure_torsion(normal_signal)
    synchronizer.measure_torsion(resonant_signal)
    print(synchronizer.get_audit_summary())
