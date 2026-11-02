"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Amplitude Equilibrium Modulator Sentinel

This module provides real-time telemetry analysis, harmonic torsion tracking, amplitude equilibrium modulation,
and automated dampening command dispatch for commercial grain milling roller mill drives in Nairobi, Kenya.
"""

import logging
import time
import random
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorsionModulator")


class RollerMillTorsionModulator:
    """
    Monitors torsional stress, harmonic frequencies, and amplitude oscillations in roller mill shafts,
    calculating equilibrium adjustments and issuing real-time damping signals.
    """

    def __init__(self, mill_id: str, nominal_rpm: float = 1200.0):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.telemetry_history: List[Dict[str, Any]] = []
        self.equilibrium_factor = 1.0
        logger.info(f"Initialized RollerMillTorsionModulator for mill: {self.mill_id} at {nominal_rpm} RPM")

    def ingest_sensor_data(self, vibration_amplitude: float, torsion_stress_mpa: float, harmonic_distortion_pct: float) -> Dict[str, Any]:
        """
        Ingests current operational metrics from roller mill sensors.
        """
        timestamp = time.time()
        status = "OPTIMAL"
        
        # Analyze threshold deviations
        if harmonic_distortion_pct > 8.5 or torsion_stress_mpa > 150.0:
            status = "WARNING_HIGH_STRESS"
        if vibration_amplitude > 4.5:
            status = "CRITICAL_RESONANCE_RISK"
            
        reading = {
            "timestamp": timestamp,
            "vibration_amplitude": vibration_amplitude,
            "torsion_stress_mpa": torsion_stress_mpa,
            "harmonic_distortion_pct": harmonic_distortion_pct,
            "status": status
        }
        self.telemetry_history.append(reading)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        return reading

    def calculate_equilibrium_modulation(self) -> float:
        """
        Computes counter-harmonic amplitude adjustments to restore equilibrium.
        """
        if not self.telemetry_history:
            return 1.0
            
        latest = self.telemetry_history[-1]
        stress = latest["torsion_stress_mpa"]
        distortion = latest["harmonic_distortion_pct"]
        
        # Dynamic adjustment calculation
        adjustment = 1.0 - ((stress / 300.0) * 0.15) - ((distortion / 20.0) * 0.10)
        self.equilibrium_factor = max(0.5, min(1.5, adjustment))
        
        logger.debug(f"Calculated equilibrium factor: {self.equilibrium_factor:.4f} for mill {self.mill_id}")
        return self.equilibrium_factor

    def execute_stabilization_routine(self) -> Dict[str, Any]:
        """
        Executes dampening routine and returns actuator command payload.
        """
        factor = self.calculate_equilibrium_modulation()
        latest = self.telemetry_history[-1] if self.telemetry_history else {}
        
        action = "MAINTAIN"
        if factor < 0.85:
            action = "APPLY_MAGNETORHEOLOGICAL_DAMPENING"
        elif factor > 1.15:
            action = "OPTIMIZE_INVERTER_TORQUE_VECTOR"
            
        command = {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "equilibrium_factor": factor,
            "action_dispatched": action,
            "target_rpm": self.nominal_rpm * factor,
            "source_status": latest.get("status", "UNKNOWN")
        }
        logger.info(f"Dispatching command for {self.mill_id}: {action} (Factor: {factor:.3f})")
        return command


if __name__ == "__main__":
    print("--- Executing RollerMillTorsionModulator Test Harness ---")
    modulator = RollerMillTorsionModulator(mill_id="NAIROBI_MILL_ALPHA_04", nominal_rpm=1250.0)
    
    # Simulate fluctuating telemetry
    for i in range(5):
        vib = random.uniform(1.2, 5.0)
        stress = random.uniform(90.0, 175.0)
        harmonic = random.uniform(3.0, 11.0)
        
        modulator.ingest_sensor_data(vib, stress, harmonic)
        cmd = modulator.execute_stabilization_routine()
        print(f"Iteration {i+1} Command: {cmd}")
    print("--- Test Harness Completed Successfully ---")
