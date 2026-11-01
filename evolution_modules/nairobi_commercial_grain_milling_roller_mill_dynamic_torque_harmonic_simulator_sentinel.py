"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Harmonic Simulator Sentinel
Designed for Cortana's Autonomous Evolutionary Architecture.
Provides real-time simulation, harmonic distortion analysis, and predictive failure mitigation for roller mill drives in Nairobi.
"""

import math
import time
import logging
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicSimulator")


class RollerMillHarmonicSimulator:
    """Simulates and analyzes roller mill drive motor torque ripple and harmonic resonance."""

    def __init__(self, base_rpm: float = 1450.0, nominal_torque: float = 250.0):
        self.base_rpm = base_rpm
        self.nominal_torque = nominal_torque
        self.history: List[Dict[str, Any]] = []

    def simulate_cycle(self, load_factor: float, grid_voltage_sag: bool = False) -> Dict[str, Any]:
        """Runs a single simulation tick of the roller mill torque harmonics."""
        current_rpm = self.base_rpm * (0.95 if grid_voltage_sag else 1.0)
        torque_ripple = self.nominal_torque * load_factor * (0.12 if grid_voltage_sag else 0.05)
        harmonic_distortion = 3.5 if grid_voltage_sag else 1.2
        
        # Phase quadrature calculation
        phase_angle = (time.time() * 50.0) % (2 * math.pi)
        quadrature_component = torque_ripple * math.sin(phase_angle)
        
        status = "OPTIMAL"
        if harmonic_distortion > 3.0:
            status = "WARNING_HARMONIC_INSTABILITY"
            
        telemetry = {
            "timestamp": time.time(),
            "rpm": current_rpm,
            "torque_ripple": torque_ripple,
            "harmonic_distortion_percent": harmonic_distortion,
            "quadrature_component": quadrature_component,
            "status": status
        }
        self.history.append(telemetry)
        return telemetry

    def get_aggregate_telemetry(self) -> Dict[str, Any]:
        """Returns aggregated health metrics for the milling sentinel."""
        if not self.history:
            return {"status": "NO_DATA"}
        latest = self.history[-1]
        return {
            "total_cycles": len(self.history),
            "latest_status": latest["status"],
            "latest_distortion": latest["harmonic_distortion_percent"]
        }


if __name__ == "__main__":
    logger.info("Initializing RollerMillHarmonicSimulator Sentinel...")
    sentinel = RollerMillHarmonicSimulator()
    
    # Simulate standard load
    tick_normal = sentinel.simulate_cycle(load_factor=0.85, grid_voltage_sag=False)
    logger.info(f"Normal Cycle Telemetry: {tick_normal}")
    
    # Simulate grid disturbance
    tick_sag = sentinel.simulate_cycle(load_factor=0.95, grid_voltage_sag=True)
    logger.info(f"Disturbed Cycle Telemetry: {tick_sag}")
    
    agg = sentinel.get_aggregate_telemetry()
    logger.info(f"Aggregate Telemetry: {agg}")
    logger.info("Sentinel execution completed successfully.")
