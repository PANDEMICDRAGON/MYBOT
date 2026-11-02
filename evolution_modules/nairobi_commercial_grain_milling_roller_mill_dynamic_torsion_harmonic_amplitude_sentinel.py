"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Amplitude Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import logging
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RollerMillDynamicTorsionSentinel")

class RollerMillTorsionSentinel:
    """
    Monitors dynamic torsional harmonic amplitudes on commercial roller mill shafts,
    predicts resonance fatigue, and engages dynamic counter-oscillation dampers.
    """
    def __init__(self, mill_id: str, nominal_rpm: float = 1200.0, warning_threshold_deg: float = 1.5):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.warning_threshold_deg = warning_threshold_deg
        self.telemetry_buffer: List[Dict[str, Any]] = []
        self.active_dampening_engaged = False
        logger.info(f"Initialized RollerMillTorsionSentinel for mill {mill_id} at {nominal_rpm} RPM.")

    def ingest_torsion_telemetry(self, timestamp: float, angular_twist_degrees: float, motor_current_amps: float) -> Dict[str, Any]:
        """
        Ingests real-time torsional sensor feed and evaluates harmonic integrity.
        """
        deviation = abs(angular_twist_degrees)
        status = "NOMINAL"
        action_taken = "NONE"

        if deviation > self.warning_threshold_deg:
            status = "WARNING"
            self.active_dampening_engaged = True
            action_taken = "ENGAGE_DYNAMIC_COUNTER_TORQUE"
            logger.warning(f"[{self.mill_id}] Torsional harmonic spike detected: {angular_twist_degrees:.3f}° twist!")
        else:
            if self.active_dampening_engaged and deviation < (self.warning_threshold_deg * 0.5):
                self.active_dampening_engaged = False
                action_taken = "DISENGAGE_DAMPERS_RETURN_TO_NOMINAL"
                logger.info(f"[{self.mill_id}] Torsion normalized. Dampers disengaged.")

        telemetry_point = {
            "timestamp": timestamp,
            "twist_deg": angular_twist_degrees,
            "current_amps": motor_current_amps,
            "status": status,
            "dampened": self.active_dampening_engaged
        }
        self.telemetry_buffer.append(telemetry_point)
        if len(self.telemetry_buffer) > 1000:
            self.telemetry_buffer.pop(0)

        return {
            "mill_id": self.mill_id,
            "status": status,
            "action_taken": action_taken,
            "dampener_active": self.active_dampening_engaged
        }

    def generate_harmonic_report(self) -> Dict[str, Any]:
        """
        Summarizes structural harmonic health.
        """
        if not self.telemetry_buffer:
            return {"error": "No telemetry recorded."}

        twists = [p["twist_deg"] for p in self.telemetry_buffer]
        max_twist = max(twists)
        avg_twist = sum(twists) / len(twists)

        return {
            "mill_id": self.mill_id,
            "samples_analyzed": len(self.telemetry_buffer),
            "max_twist_deg": max_twist,
            "average_twist_deg": avg_twist,
            "structural_integrity_score": max(0.0, 100.0 - (max_twist / self.warning_threshold_deg) * 50.0)
        }

if __name__ == "__main__":
    sentinel = RollerMillTorsionSentinel(mill_id="NAI-MILL-04", nominal_rpm=1250.0, warning_threshold_deg=1.2)
    
    # Test normal operations
    res1 = sentinel.ingest_torsion_telemetry(time.time(), 0.4, 45.2)
    print("Test 1:", res1)
    
    # Test harmonic spike triggering dampeners
    res2 = sentinel.ingest_torsion_telemetry(time.time(), 1.6, 78.9)
    print("Test 2:", res2)
    
    # Report
    print("Diagnostic Report:", sentinel.generate_harmonic_report())
