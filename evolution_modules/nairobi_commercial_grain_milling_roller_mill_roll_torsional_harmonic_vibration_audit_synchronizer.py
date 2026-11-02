"""Nairobi Commercial Grain Milling Roller Mill Roll Torsional Harmonic Vibration Audit Synchronizer."""

import ast
import json
import logging
import math
import random
import time
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("TorsionalVibrationSynchronizer")

class TorsionalHarmonicAuditSynchronizer:
    """Audits and synchronizes torsional harmonic vibrations on commercial grain mill roller shafts."""

    def __init__(self, mill_id: str, roll_diameter_mm: float = 250.0, target_rpm: float = 550.0):
        self.mill_id = mill_id
        self.roll_diameter_mm = roll_diameter_mm
        self.target_rpm = target_rpm
        self.audit_log: List[Dict[str, Any]] = []

    def measure_torsional_resonance(self, raw_vibration_hz: List[float]) -> Dict[str, Any]:
        """Calculates torsional harmonic distortion and stress anomalies from raw sensor spectra."""
        if not raw_vibration_hz:
            return {"status": "error", "message": "No sensor telemetry provided."}

        mean_freq = sum(raw_vibration_hz) / len(raw_vibration_hz)
        variance = sum((f - mean_freq) ** 2 for f in raw_vibration_hz) / len(raw_vibration_hz)
        std_dev = math.sqrt(variance)
        
        # Harmonic index calculation relative to base rotational frequency (RPM / 60)
        base_rot_freq = self.target_rpm / 60.0
        harmonic_distortion_index = std_dev / (base_rot_freq + 1e-6)

        status = "OPTIMAL"
        if harmonic_distortion_index > 0.45:
            status = "CRITICAL_TORSIONAL_STRESS"
        elif harmonic_distortion_index > 0.25:
            status = "ELEVATED_HARMONIC_DRIFT"

        audit_entry = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "mean_frequency_hz": mean_freq,
            "torsional_std_dev": std_dev,
            "harmonic_distortion_index": harmonic_distortion_index,
            "status": status
        }
        self.audit_log.append(audit_entry)
        return audit_entry

    def calibrate_roll_synchronization(self, distortion_index: float) -> Dict[str, Any]:
        """Computes phase correction offset to mitigate torsional resonance."""
        correction_phase_degrees = 0.0
        if distortion_index > 0.25:
            # Dynamic phase shift compensation vector
            correction_phase_degrees = (distortion_index * 45.0) % 360.0
        
        return {
            "mill_id": self.mill_id,
            "correction_applied": correction_phase_degrees > 0.0,
            "phase_offset_degrees": round(correction_phase_degrees, 3),
            "message": f"Applied torsional synchronization offset of {correction_phase_degrees:.2f} degrees." if correction_phase_degrees > 0.0 else "Rollers in harmonic equilibrium."
        }

    def export_audit_report(self) -> str:
        """Serializes audit records to JSON."""
        return json.dumps(self.audit_log, indent=2)

if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Roll Torsional Harmonic Vibration Audit Synchronizer Test Harness...")
    
    synchronizer = TorsionalHarmonicAuditSynchronizer(mill_id="NAI_MILL_BLOCK_4_ROLL_A")
    
    # Simulate vibrating frequency readings from accelerometers mounted on roll bearing housings
    simulated_readings = [9.16, 9.22, 14.50, 9.18, 18.75, 9.15]
    
    audit_result = synchronizer.measure_torsional_resonance(simulated_readings)
    logger.info(f"Audit Result: {audit_result}")
    
    sync_result = synchronizer.calibrate_roll_synchronization(audit_result["harmonic_distortion_index"])
    logger.info(f"Synchronization Result: {sync_result}")
    
    # Validate code cleanliness under ast.parse
    code_string = open(__file__, "r", encoding="utf-8").read()
    parsed_ast = ast.parse(code_string)
    logger.info(f"AST compilation check passed successfully: {len(parsed_ast.body)} top-level nodes verified.")
