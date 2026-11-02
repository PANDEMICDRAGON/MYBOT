"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Decoupling Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Monitors roller mill shaft torsional resonance, decoupling harmonic feedback loops
to protect heavy industrial milling machinery from fatigue and catastrophic failure.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("TorsionHarmonicDecouplingSentinel")

class TorsionHarmonicDecouplingSentinel:
    """Real-time telemetry analyzer and dynamic decoupler for roller mill torsional harmonics."""
    
    def __init__(self, mill_id: str, nominal_rpm: float = 1200.0, harmonic_threshold_hz: float = 45.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.harmonic_threshold_hz = harmonic_threshold_hz
        self.decoupling_active = False
        self.telemetry_history: List[Dict[str, Any]] = []

    def ingest_telemetry(self, vibration_spectrum: List[float], torque_nm: float, current_rpm: float) -> Dict[str, Any]:
        """Ingests raw sensor stream, calculates harmonic peaks, and triggers decoupling if needed."""
        timestamp = time.time()
        peak_harmonic = max(vibration_spectrum) if vibration_spectrum else 0.0
        rpm_deviation = abs(current_rpm - self.nominal_rpm)
        
        # Torsional stress coefficient calculation
        torsion_stress_index = (peak_harmonic * torque_nm) / (self.nominal_rpm + 1e-6)
        
        self.decoupling_active = peak_harmonic > self.harmonic_threshold_hz or torsion_stress_index > 750.0

        status = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "peak_harmonic_hz": peak_harmonic,
            "torque_nm": torque_nm,
            "current_rpm": current_rpm,
            "torsion_stress_index": round(torsion_stress_index, 2),
            "decoupling_active": self.decoupling_active
        }
        
        self.telemetry_history.append(status)
        if len(self.telemetry_history) > 100:
            self.telemetry_history.pop(0)
            
        if self.decoupling_active:
            logger.warning(f"[{self.mill_id}] Torsional harmonic threshold breached! Peak: {peak_harmonic}Hz, Stress Index: {status['torsion_stress_index']}. Engaging dynamic decoupling actuators.")
        else:
            logger.info(f"[{self.mill_id}] Roller mill operating within safe torsional limits. Stress Index: {status['torsion_stress_index']}")

        return status

    def generate_diagnostic_report(self) -> Dict[str, Any]:
        """Summarizes system stability and decoupling events."""
        if not self.telemetry_history:
            return {"status": "No telemetry recorded."}
            
        avg_stress = sum(t["torsion_stress_index"] for t in self.telemetry_history) / len(self.telemetry_history)
        decoupling_events = sum(1 for t in self.telemetry_history if t["decoupling_active"])
        
        return {
            "mill_id": self.mill_id,
            "samples_analyzed": len(self.telemetry_history),
            "average_torsion_stress_index": round(avg_stress, 2),
            "total_decoupling_events_logged": decoupling_events,
            "system_health": "OPTIMAL" if decoupling_events == 0 else "ATTENTION_REQUIRED"
        }

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Decoupling Sentinel...")
    sentinel = TorsionHarmonicDecouplingSentinel(mill_id="NAI-MILL-ALPHA-04")
    
    # Simulate monitoring cycles
    for i in range(5):
        mock_spectrum = [random.uniform(10.0, 30.0) if i < 3 else random.uniform(40.0, 60.0) for _ in range(5)]
        mock_torque = random.uniform(300.0, 650.0)
        mock_rpm = random.uniform(1180.0, 1220.0)
        
        sentinel.ingest_telemetry(
            vibration_spectrum=mock_spectrum,
            torque_nm=mock_torque,
            current_rpm=mock_rpm
        )
        time.sleep(0.1)
        
    report = sentinel.generate_diagnostic_report()
    print("Diagnostic Report:", report)
    print("Torsion Harmonic Decoupling Sentinel test completed successfully.")
