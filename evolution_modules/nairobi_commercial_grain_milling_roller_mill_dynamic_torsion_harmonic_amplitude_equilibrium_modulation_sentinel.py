"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Amplitude Equilibrium Modulation Sentinel

Architected to monitor, analyze, and modulate high-frequency torsional oscillations, harmonic amplitudes,
and drive-shaft torque equilibria in industrial roller mills operating across Nairobi milling facilities.
"""

import ast
import logging
import math
import random
import time
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillHarmonicSentinel")


class RollerMillTorsionModulator:
    """Monitors harmonic amplitude and applies equilibrium modulation to roller mill drive shafts."""

    def __init__(self, mill_id: str, nominal_rpm: float = 1200.0, harmonic_threshold: float = 4.5):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.harmonic_threshold = harmonic_threshold
        self.active_modulation_state = False
        self.torsion_history: List[float] = []

    def ingest_telemetry(self, current_rpm: float, torque_nm: float, vibration_mm_s: float) -> Dict[str, any]:
        """Ingests telemetry data and calculates harmonic deviation and torsional stress."""
        rpm_deviation = abs(current_rpm - self.nominal_rpm)
        # Calculate synthetic harmonic amplitude index based on vibration and torque ripple
        harmonic_index = (vibration_mm_s * 1.5) + (torque_nm * 0.02) + (rpm_deviation * 0.05)
        
        self.torsion_history.append(harmonic_index)
        if len(self.torsion_history) > 50:
            self.torsion_history.pop(0)
            
        status = "STABLE"
        modulation_applied = 0.0
        
        if harmonic_index > self.harmonic_threshold:
            self.active_modulation_state = True
            status = "RESONANCE_WARNING"
            modulation_applied = self._calculate_counter_torsion_pulse(harmonic_index)
        else:
            self.active_modulation_state = False
            
        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "harmonic_index": round(harmonic_index, 4),
            "status": status,
            "active_modulation": self.active_modulation_state,
            "counter_torsion_pulse_nm": round(modulation_applied, 4)
        }

    def _calculate_counter_torsion_pulse(self, harmonic_index: float) -> float:
        """Calculates inverse phase torque pulse to dampen harmonic amplitude."""
        excess = harmonic_index - self.harmonic_threshold
        return -(excess * 12.8)


class NairobiRollerMillFleetManager:
    """Manages a fleet of commercial roller mills across Nairobi industrial zones."""

    def __init__(self):
        self.mills: Dict[str, RollerMillTorsionModulator] = {
            "NRB-MILL-01": RollerMillTorsionModulator("NRB-MILL-01", 1200.0, 4.0),
            "NRB-MILL-02": RollerMillTorsionModulator("NRB-MILL-02", 1250.0, 4.2),
            "NRB-MILL-03": RollerMillTorsionModulator("NRB-MILL-03", 1180.0, 3.8),
        }

    def execute_fleet_sweep(self) -> List[Dict[str, any]]:
        """Performs a diagnostic sweep across all registered mills."""
        results = []
        for mill_id, modulator in self.mills.items():
            sim_rpm = modulator.nominal_rpm + random.uniform(-15.0, 15.0)
            sim_torque = random.uniform(180.0, 240.0)
            sim_vibr = random.uniform(1.0, 5.5)
            
            # Introduce artificial anomaly for testing resilience
            if mill_id == "NRB-MILL-02" and random.random() < 0.3:
                sim_vibr = 6.8
                
            telemetry = modulator.ingest_telemetry(sim_rpm, sim_torque, sim_vibr)
            results.append(telemetry)
            logger.info(f"Fleet Diagnostics -> Mill: {mill_id} | Index: {telemetry['harmonic_index']} | Status: {telemetry['status']}")
        return results


if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Amplitude Equilibrium Modulation Sentinel...")
    manager = NairobiRollerMillFleetManager()
    sweep_results = manager.execute_fleet_sweep()
    logger.info(f"Completed sweep of {len(sweep_results)} industrial roller mills in Nairobi.")
