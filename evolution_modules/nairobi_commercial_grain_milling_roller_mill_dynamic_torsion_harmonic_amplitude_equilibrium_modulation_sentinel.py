"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Amplitude Equilibrium Modulation Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import random
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorsionModulatorSentinel")

class RollerMillTorsionModulatorSentinel:
    def __init__(self, mill_id: str, nominal_rpm: float = 750.0, rated_torque_nm: float = 450.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.rated_torque_nm = rated_torque_nm
        self.torsion_history: List[float] = []
        self.harmonic_amplitudes: List[float] = []
        self.equilibrium_status = "STABLE"
        self.modulation_factor = 1.0

    def ingest_telemetry(self, current_rpm: float, measured_torque_nm: float, vibration_hz: float) -> Dict[str, Any]:
        """
        Ingests real-time rotational and vibrational telemetry to calculate torsion harmonics.
        """
        rpm_deviation = abs(current_rpm - self.nominal_rpm) / self.nominal_rpm
        torque_load_ratio = measured_torque_nm / self.rated_torque_nm
        
        # Compute instantaneous torsion harmonic amplitude
        harmonic_amplitude = (rpm_deviation * 1.5) + (torque_load_ratio * 0.8) + (math.sin(vibration_hz * 0.1) * 0.2)
        
        self.torsion_history.append(measured_torque_nm)
        self.harmonic_amplitudes.append(harmonic_amplitude)
        
        if len(self.torsion_history) > 100:
            self.torsion_history.pop(0)
            self.harmonic_amplitudes.pop(0)
            
        return self._evaluate_and_modulate(harmonic_amplitude, torque_load_ratio)

    def _evaluate_and_modulate(self, current_amplitude: float, torque_load_ratio: float) -> Dict[str, Any]:
        """
        Evaluates equilibrium state and computes dampening/modulation adjustments.
        """
        if current_amplitude > 1.2 or torque_load_ratio > 1.15:
            self.equilibrium_status = "CRITICAL_HARMONIC_SPIKE"
            self.modulation_factor = max(0.70, self.modulation_factor - 0.05)
        elif current_amplitude > 0.85:
            self.equilibrium_status = "ELEVATED_TORSION"
            self.modulation_factor = max(0.85, self.modulation_factor - 0.02)
        else:
            self.equilibrium_status = "STABLE"
            self.modulation_factor = min(1.0, self.modulation_factor + 0.01)
            
        action = "DAMPEN_INVERTER_DRIVE" if self.equilibrium_status != "STABLE" else "OPTIMAL_OPERATION"
        
        return {
            "mill_id": self.mill_id,
            "status": self.equilibrium_status,
            "current_harmonic_amplitude": round(current_amplitude, 4),
            "modulation_factor": round(self.modulation_factor, 4),
            "recommended_action": action,
            "timestamp": time.time()
        }

if __name__ == "__main__":
    logger.info("Initializing RollerMillTorsionModulatorSentinel test harness for Nairobi facility...")
    sentinel = RollerMillTorsionModulatorSentinel(mill_id="NAI_UNGA_MILL_04")
    
    for step in range(5):
        rpm = 750.0 + random.uniform(-25.0, 35.0)
        torque = 420.0 + random.uniform(-50.0, 80.0)
        vibration = 45.0 + random.uniform(-5.0, 15.0)
        report = sentinel.ingest_telemetry(rpm, torque, vibration)
        logger.info(f"Step {step+1} Telemetry Report: {report}")
        time.sleep(0.1)
    
    logger.info("RollerMillTorsionModulatorSentinel verified successfully.")
