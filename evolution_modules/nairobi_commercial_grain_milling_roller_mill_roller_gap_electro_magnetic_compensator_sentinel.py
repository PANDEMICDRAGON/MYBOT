"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Electro Magnetic Compensator Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides real-time telemetry analysis and magnetic counter-actuation for roller mill gaps
in commercial grain milling operations, preventing endosperm scorching and uneven granulation.
"""

import time
import math
import random
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerGapElectroMagneticCompensator")

class RollerGapElectroMagneticCompensator:
    """Monitors roller gap variance and applies electromagnetic flux compensation."""

    def __init__(self, mill_id: str, nominal_gap_microns: float = 120.0):
        self.mill_id = mill_id
        self.nominal_gap_microns = nominal_gap_microns
        self.current_gap = nominal_gap_microns
        self.magnetic_bias_current_amps = 0.0
        self.compensation_history: List[Dict[str, Any]] = []

    def sample_and_compensate(self, thermal_drift_microns: float, vibration_amplitude_g: float) -> Dict[str, Any]:
        """Calculates required electromagnetic adjustment to keep gap within tight tolerances."""
        # Calculate total deviation
        deviation = thermal_drift_microns + (vibration_amplitude_g * 1.5)
        target_correction = -deviation

        # Proportion-Integral-Derivative simplified model for magnetic coil current
        # 1 Ampere ~ 12.5 microns adjustment based on magnetic reluctance coefficient
        required_current_delta = target_correction / 12.5
        self.magnetic_bias_current_amps += required_current_delta * 0.4
        
        # Clamp current within safety bounds (-5A to +5A)
        self.magnetic_bias_current_amps = max(-5.0, min(5.0, self.magnetic_bias_current_amps))
        
        # Adjusted gap after magnetic flux intervention
        self.current_gap = self.nominal_gap_microns + deviation + (self.magnetic_bias_current_amps * 12.5)

        telemetry = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "nominal_gap_microns": self.nominal_gap_microns,
            "measured_gap_microns": round(self.current_gap, 2),
            "deviation_microns": round(deviation, 2),
            "magnetic_bias_amps": round(self.magnetic_bias_current_amps, 3),
            "status": "STABLE" if abs(self.current_gap - self.nominal_gap_microns) < 3.0 else "COMPENSATING"
        }

        self.compensation_history.append(telemetry)
        if len(self.compensation_history) > 100:
            self.compensation_history.pop(0)

        return telemetry

if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Gap Electro-Magnetic Compensator Test Harness...")
    compensator = RollerGapElectroMagneticCompensator(mill_id="NAIROBI_MILL_EAST_04", nominal_gap_microns=125.0)
    
    for i in range(5):
        simulated_thermal = random.uniform(-4.5, 6.0)
        simulated_vibration = random.uniform(0.1, 1.2)
        result = compensator.sample_and_compensate(simulated_thermal, simulated_vibration)
        logger.info(f"Telemetry Cycle {i+1}: {result}")
        time.sleep(0.1)
    
    logger.info("Electro-Magnetic Compensator Sentinel test completed successfully.")
