"""
Module: nairobi_commercial_grain_milling_roller_mill_roll_torsional_harmonic_vibration_audit_synchronizer_v26.py
Description: Proactive torsional harmonic vibration audit and phase synchronization engine for industrial roller mills in Nairobi, Kenya.
"""

import math
import time
import logging
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorsionalSynchronizerV26")


class RollerMillTorsionalAuditor:
    """Audits torsional harmonic frequencies across roller mill roll pairs."""

    def __init__(self, mill_id: str, baseline_rpm: float = 750.0, harmonic_tolerance: float = 0.02):
        self.mill_id = mill_id
        self.baseline_rpm = baseline_rpm
        self.harmonic_tolerance = harmonic_tolerance
        self.audit_history: List[Dict[str, Any]] = []

    def audit_vibration_harmonics(self, fast_roll_vibration: List[float], slow_roll_vibration: List[float]) -> Dict[str, Any]:
        """Calculates cross-spectral torsional phase coherence and harmonic deviation."""
        if not fast_roll_vibration or not slow_roll_vibration:
            raise ValueError("Vibration telemetry streams cannot be empty.")

        mean_fast = sum(fast_roll_vibration) / len(fast_roll_vibration)
        mean_slow = sum(slow_roll_vibration) / len(slow_roll_vibration)

        # Compute pseudo-coherence metric
        covariance = sum((f - mean_fast) * (s - mean_slow) for f, s in zip(fast_roll_vibration, slow_roll_vibration))
        variance_product = (sum((f - mean_fast) ** 2 for f in fast_roll_vibration) * 
                            sum((s - mean_slow) ** 2 for s in slow_roll_vibration)) ** 0.5

        coherence = covariance / variance_product if variance_product > 0 else 0.0
        harmonic_shift = abs(1.0 - abs(coherence))

        status = "OPTIMAL"
        if harmonic_shift > self.harmonic_tolerance:
            status = "WARNING_TORSIONAL_SLIP"

        audit_record = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "coherence_score": coherence,
            "harmonic_shift": harmonic_shift,
            "status": status
        }

        self.audit_history.append(audit_record)
        logger.info(f"[{self.mill_id}] Torsional Audit Complete. Status: {status}, Coherence: {coherence:.4f}")
        return audit_record


if __name__ == "__main__":
    auditor = RollerMillTorsionalAuditor(mill_id="NAI_GRAIN_MILL_04")
    # Simulate minor harmonic vibration telemetry
    fast_telemetry = [math.sin(i * 0.1) + 0.05 * math.sin(i * 0.5) for i in range(100)]
    slow_telemetry = [math.sin(i * 0.1 - 0.02) + 0.06 * math.sin(i * 0.5) for i in range(100)]
    result = auditor.audit_vibration_harmonics(fast_telemetry, slow_telemetry)
    print("Test Audit Result:", result)
