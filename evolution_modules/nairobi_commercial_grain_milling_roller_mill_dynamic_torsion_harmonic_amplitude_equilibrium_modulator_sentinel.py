"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Amplitude Equilibrium Modulator Sentinel

Detects, analyzes, and mitigates torsional harmonic vibrations and amplitude fluctuations
in heavy commercial roller mill shafts processing maize and wheat in Nairobi, Kenya.
"""

import math
import time
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorsionModulator")


class RollerMillTorsionModulator:
    """
    Monitors torsional stress telemetry from industrial roller mills, computes harmonic
    amplitude equilibrium, and adjusts dynamic damping parameters to prevent mechanical fatigue.
    """

    def __init__(self, mill_id: str, baseline_rpm: float = 750.0, harmonic_threshold: float = 4.5):
        self.mill_id = mill_id
        self.baseline_rpm = baseline_rpm
        self.harmonic_threshold = harmonic_threshold
        self.telemetry_history: List[Dict[str, Any]] = []
        self.equilibrium_state = "OPTIMAL"

    def ingest_vibration_data(self, rpm: float, torsional_amplitude: float, frequency_hz: float) -> Dict[str, Any]:
        """
        Ingests real-time telemetry from roller mill drive-end and non-drive-end sensors.
        """
        timestamp = time.time()
        deviation = abs(rpm - self.baseline_rpm)
        harmonic_stress = torsional_amplitude * (frequency_hz / 50.0)

        status = "NORMAL"
        action_required = False
        damping_adjustment = 0.0

        if harmonic_stress > self.harmonic_threshold:
            status = "CRITICAL_RESONANCE"
            action_required = True
            # Calculate counter-torsional damping modulation offset
            damping_adjustment = round((harmonic_stress - self.harmonic_threshold) * 1.85, 3)
            self.equilibrium_state = "MODULATING"
        else:
            self.equilibrium_state = "OPTIMAL"

        telemetry_packet = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "rpm": rpm,
            "torsional_amplitude": torsional_amplitude,
            "frequency_hz": frequency_hz,
            "harmonic_stress": harmonic_stress,
            "status": status,
            "action_required": action_required,
            "damping_adjustment": damping_adjustment
        }

        self.telemetry_history.append(telemetry_packet)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return telemetry_packet

    def run_diagnostics(self) -> Dict[str, Any]:
        """
        Runs structural integrity and harmonic equilibrium diagnostics.
        """
        if not self.telemetry_history:
            return {"status": "NO_DATA", "health_score": 100.0}

        recent = self.telemetry_history[-1]
        health_score = max(0.0, 100.0 - (recent["harmonic_stress"] * 10.0))
        
        return {
            "mill_id": self.mill_id,
            "equilibrium_state": self.equilibrium_state,
            "health_score": round(health_score, 2),
            "last_harmonic_stress": recent["harmonic_stress"],
            "total_samples_analyzed": len(self.telemetry_history)
        }


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Amplitude Equilibrium Modulator Sentinel...")
    sentinel = RollerMillTorsionModulator(mill_id="NAI-MILL-IND-04")
    
    # Simulate normal operation
    packet_norm = sentinel.ingest_vibration_data(rpm=749.5, torsional_amplitude=1.2, frequency_hz=48.5)
    print(f"Telemetry (Normal): {packet_norm}")
    
    # Simulate resonant surge event
    packet_surge = sentinel.ingest_vibration_data(rpm=785.0, torsional_amplitude=3.8, frequency_hz=62.0)
    print(f"Telemetry (Surge): {packet_surge}")
    
    diagnostics = sentinel.run_diagnostics()
    print(f"Diagnostics Report: {diagnostics}")
    print("Roller mill dynamic torsion equilibrium sentinel operational.")
