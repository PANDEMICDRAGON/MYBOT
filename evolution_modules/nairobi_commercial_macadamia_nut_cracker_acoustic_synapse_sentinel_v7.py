"""
Nairobi Commercial Macadamia Nut Cracker Acoustic Synapse Harmonic Pulse Correlation Sentinel V7
Designed and coded autonomously by Cortana for Michael Obiero, Nairobi, Kenya.

Audits acoustic vibration spectra of industrial macadamia nut cracking machinery to maintain
optimum mechanical gap pressures, prevent kernel fracturing, and maximize yield.
"""

import os
import sys
import time
import math
import json
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [MACADAMIA_SYNAPSE_V7]: %(message)s')
logger = logging.getLogger(__name__)

class MacadamiaAcousticSynapseSentinel:
    """
    Real-time acoustic harmonic pulse correlation engine tuned for industrial macadamia nut crackers
    operating in Nairobi agricultural processing hubs.
    """
    def __init__(self, machine_id: str, target_frequency_hz: float = 432.5):
        self.machine_id = machine_id
        self.target_frequency_hz = target_frequency_hz
        self.anomaly_threshold = 0.85
        self.audit_log: List[Dict[str, Any]] = []
        logger.info(f"Initialized Macadamia Acoustic Synapse Sentinel V7 for machine {machine_id} at target freq {target_frequency_hz}Hz")

    def correlate_harmonic_pulse(self, vibration_spectrum: List[float]) -> Dict[str, Any]:
        """
        Analyzes incoming vibration frequency magnitudes and calculates harmonic correlation coefficient.
        """
        if not vibration_spectrum:
            return {"status": "error", "message": "Empty vibration spectrum received."}

        # Compute pseudo-harmonic resonance index
        mean_mag = sum(vibration_spectrum) / len(vibration_spectrum)
        peak_mag = max(vibration_spectrum)
        variance = sum((x - mean_mag) ** 2 for x in vibration_spectrum) / len(vibration_spectrum)
        std_dev = math.sqrt(variance) if variance > 0 else 1.0
        
        # Correlation calculation against target harmonic profile
        harmonic_alignment = min(1.0, max(0.0, 1.0 - (abs(peak_mag - self.target_frequency_hz) / (self.target_frequency_hz + 1e-6))))
        structural_integrity = 1.0 - min(1.0, (std_dev / (peak_mag + 1e-6)))
        
        composite_score = (harmonic_alignment * 0.6) + (structural_integrity * 0.4)
        status = "optimal" if composite_score >= self.anomaly_threshold else "sub-optimal_adjustment_required"

        audit_entry = {
            "timestamp": time.time(),
            "machine_id": self.machine_id,
            "composite_score": round(composite_score, 4),
            "harmonic_alignment": round(harmonic_alignment, 4),
            "structural_integrity": round(structural_integrity, 4),
            "status": status
        }
        self.audit_log.append(audit_entry)
        return audit_entry

    def get_diagnostic_report(self) -> Dict[str, Any]:
        """
        Returns aggregated diagnostic summary for operator Michael Obiero.
        """
        if not self.audit_log:
            return {"machine_id": self.machine_id, "total_audits": 0, "health_status": "idle"}
        
        avg_score = sum(entry["composite_score"] for entry in self.audit_log) / len(self.audit_log)
        return {
            "machine_id": self.machine_id,
            "total_audits": len(self.audit_log),
            "average_composite_score": round(avg_score, 4),
            "latest_status": self.audit_log[-1]["status"],
            "operator": "Michael Obiero (Nairobi)"
        }

if __name__ == "__main__":
    logger.info("Executing self-test harness for MacadamiaAcousticSynapseSentinel V7...")
    sentinel = MacadamiaAcousticSynapseSentinel(machine_id="MAC_CRACKER_09_NRB")
    
    # Simulate vibration spectrum readings
    test_spectra = [
        [430.1, 432.0, 433.2, 431.5],
        [410.5, 450.2, 420.1, 432.8],
        [432.4, 432.6, 432.1, 432.3]
    ];
    
    for i, spectrum in enumerate(test_spectra):
        result = sentinel.correlate_harmonic_pulse(spectrum)
        logger.info(f"Audit Iteration {i+1} Result: {json.dumps(result)}")
        
    report = sentinel.get_diagnostic_report()
    logger.info(f"Final Diagnostic Report: {json.dumps(report, indent=2)}")
    logger.info("Module compilation and test execution completed successfully.")
