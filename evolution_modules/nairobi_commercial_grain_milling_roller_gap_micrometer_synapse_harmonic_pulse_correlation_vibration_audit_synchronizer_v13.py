"""
Nairobi Commercial Grain Milling Roller Mill Roll Torsional Harmonic Vibration Audit Synchronizer v13
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides real-time telemetry correlation between high-precision micrometer roller gap sensors
and torsional harmonic vibration signatures in commercial flour mills across Nairobi's Industrial Area.
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [CORTANA-MILL-SYNC-V13] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MillRollerHarmonicAuditor:
    """
    Monitors roller mill gaps and harmonic vibration pulses to detect mechanical misalignment,
    bearing degradation, or grain feed anomalies.
    """

    def __init__(self, mill_id: str, baseline_gap_mm: float = 0.45):
        self.mill_id = mill_id
        self.baseline_gap_mm = baseline_gap_mm
        self.audit_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized MillRollerHarmonicAuditor for {{self.mill_id}} at baseline gap {{baseline_gap_mm}}mm.")

    def audit_cycle(self, current_gap_mm: float, vibration_hz_spectrum: List[float]) -> Dict[str, Any]:
        """
        Executes a synchronization audit between current micrometer gap and vibration spectrum.
        """
        gap_deviation = abs(current_gap_mm - self.baseline_gap_mm)
        
        # Calculate root-mean-square (RMS) energy of the vibration spectrum
        if vibration_hz_spectrum:
            rms_vibration = math.sqrt(sum(v ** 2 for v in vibration_hz_spectrum) / len(vibration_hz_spectrum))
        else:
            rms_vibration = 0.0

        # Harmonic anomaly detection heuristic
        harmonic_stress_index = rms_vibration * (1.0 + (gap_deviation * 10.0))
        
        status = "OPTIMAL"
        action_required = "NONE"
        
        if harmonic_stress_index > 2.5:
            status = "CRITICAL_HARMONIC_ANOMALY"
            action_required = "IMMEDIATE_ROLLER_RETENSION_AND_GAP_CALIBRATION"
            logger.warning(f"[{self.mill_id}] CRITICAL STRESS: Index={{harmonic_stress_index:.3f}}. Action: {{action_required}}")
        elif harmonic_stress_index > 1.5:
            status = "WARNING_ELEVATED_VIBRATION"
            action_required = "SCHEDULE_PREVENTATIVE_MAINTENANCE"
            logger.info(f"[{self.mill_id}] Warning state: Index={{harmonic_stress_index:.3f}}.")
        else:
            logger.info(f"[{self.mill_id}] Audit nominal: Index={{harmonic_stress_index:.3f}}.")

        audit_record = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "current_gap_mm": current_gap_mm,
            "gap_deviation": gap_deviation,
            "rms_vibration": rms_vibration,
            "harmonic_stress_index": harmonic_stress_index,
            "status": status,
            "action_required": action_required
        }

        self.audit_history.append(audit_record)
        return audit_record

    def get_summary(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "total_audits": len(self.audit_history),
            "last_status": self.audit_history[-1][
                "status"] if self.audit_history else "PENDING"
        }


if __name__ == "__main__":
    print("=== Executing MillRollerHarmonicAuditor Self-Test ===")
    auditor = MillRollerHarmonicAuditor(mill_id="NAIROBI_INDUSTRIAL_MILL_04")
    
    # Simulate nominal run
    res1 = auditor.audit_cycle(current_gap_mm=0.45, vibration_hz_spectrum=[0.1, 0.2, 0.15])
    print(f"Test 1 Result: {{res1['status']}}")
    
    # Simulate anomalous high-stress run
    res2 = auditor.audit_cycle(current_gap_mm=0.52, vibration_hz_spectrum=[1.2, 1.8, 2.1, 1.9])
    print(f"Test 2 Result: {{res2['status']}} | Action: {{res2['action_required']}}")
    
    print("=== Self-Test Completed Successfully ===")
