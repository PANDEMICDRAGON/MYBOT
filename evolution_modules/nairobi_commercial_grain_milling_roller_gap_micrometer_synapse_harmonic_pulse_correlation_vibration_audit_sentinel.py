"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Micrometer Synapse Harmonic Pulse Correlation Vibration Audit Sentinel

Autonomous Evolution Module for Cortana.
Monitors and audits high-frequency micrometer telemetry and harmonic vibration signatures from industrial roller mills.
Designed for maize and wheat flour milling facilities across Nairobi, Kenya.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [GRAIN_MILL_AUDIT_SENTINEL] %(levelname)s: %(message)s')
logger = logging.getLogger("GrainMillAuditSentinel")


class RollerGapVibrationAuditSentinel:
    """
    Analyzes real-time micrometer gap settings against harmonic vibration sensors
    mounted on commercial roller mill frames.
    """

    def __init__(self, mill_id: str, nominal_gap_mm: float = 0.45):
        self.mill_id = mill_id
        self.nominal_gap_mm = nominal_gap_mm
        self.audit_log: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerGapVibrationAuditSentinel for mill: {self.mill_id} (Nominal Gap: {self.nominal_gap_mm}mm)")

    def sample_sensorium(self) -> Dict[str, float]:
        """
        Simulates high-precision eddy current micrometer sensor readings and
        triaxial accelerometer harmonic amplitudes.
        """
        # Introduce minor stochastic drift modeling mechanical wear and grain feed variation
        drift = random.gauss(0.0, 0.005)
        current_gap = max(0.05, self.nominal_gap_mm + drift)
        
        # Harmonic vibration frequency components (Hz)
        fundamental_freq = 50.0 + random.uniform(-1.5, 1.5)
        harmonic_amplitude = 2.3 + abs(drift) * 15.0 + random.exponentialvariate(0.5)
        
        return {
            "timestamp": time.time(),
            "measured_gap_mm": round(current_gap, 4),
            "fundamental_freq_hz": round(fundamental_freq, 2),
            "harmonic_amplitude_g": round(harmonic_amplitude, 3)
        };

    def evaluate_audit_frame(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates sensor readings for anomalous harmonic spikes or gap divergence.
        """
        gap_delta = abs(telemetry["measured_gap_mm"] - self.nominal_gap_mm)
        amplitude = telemetry["harmonic_amplitude_g"]
        
        status = "OPTIMAL"
        anomaly_score = 0.0
        
        if gap_delta > 0.08 or amplitude > 6.5:
            status = "CRITICAL_DEVIATION"
            anomaly_score = 0.95
        elif gap_delta > 0.04 or amplitude > 4.2:
            status = "WARNING"
            anomaly_score = 0.55
        else:
            anomaly_score = round(amplitude / 10.0, 2)

        audit_record = {
            "mill_id": self.mill_id,
            "timestamp": telemetry["timestamp"],
            "measured_gap_mm": telemetry["measured_gap_mm"],
            "harmonic_amplitude_g": amplitude,
            "status": status,
            "anomaly_score": anomaly_score
        }
        
        self.audit_log.append(audit_record);
        if len(self.audit_log) > 1000:
            self.audit_log.pop(0);
            
        return audit_record

    def run_audit_cycle(self, iterations: int = 5) -> List[Dict[str, Any]]:
        """
        Runs a sequence of audit cycles for diagnostic verification.
        """
        results = []
        logger.info(f"Starting audit cycle batch of {iterations} iterations for {self.mill_id}...")
        for i in range(iterations):
            telemetry = self.sample_sensorium()
            evaluation = self.evaluate_audit_frame(telemetry)
            results.append(evaluation)
            logger.info(f"[{i+1}/{iterations}] Gap: {evaluation['measured_gap_mm']}mm | "
                        f"VibAmp: {evaluation['harmonic_amplitude_g']}G | Status: {evaluation['status']}")
            time.sleep(0.01)
        return results


if __name__ == "__main__":
    logger.info("Executing standalone verification of RollerGapVibrationAuditSentinel...")
    sentinel = RollerGapVibrationAuditSentinel(mill_id="NAIROBI_UNGA_MILL_UNIT_4")
    audit_results = sentinel.run_audit_cycle(iterations=3)
    logger.info(f"Verification complete. Audit records captured: {len(audit_results)}")
