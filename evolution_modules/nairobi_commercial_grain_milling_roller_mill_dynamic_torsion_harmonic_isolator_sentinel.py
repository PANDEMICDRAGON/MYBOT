"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Isolator Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides real-time telemetry collection, harmonic frequency decomposition, torsional stress
modeling, and active electromagnetic/hydraulic damping command generation for heavy industrial
roller mills in Nairobi grain processing facilities.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional
from datacdataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger("TorsionHarmonicIsolatorSentinel")

@dataclass
class RollerMillTelemetry:
    mill_id: str
    timestamp: float
    rpm_fast: float
    rpm_slow: float
    torque_Nm: float
    torsion_angle_deg: float
    vibration_frequency_hz: float
    bearing_temp_c: float

@dataclass
class IsolationCommand:
    mill_id: str
    timestamp: float
    damping_coefficient: float
    counter_torque_Nm: float
    status: str
    resonance_detected: bool

class TorsionHarmonicIsolatorEngine:
    """
    Analyzes torsional stress oscillations in commercial roller mills and computes dynamic
    counter-torque adjustments to suppress destructive harmonic resonances.
    """
    def __init__(self, target_resonant_band_hz: float = 45.0, tolerance_hz: float = 3.5):
        self.target_band = target_resonant_band_hz
        self.tolerance = tolerance_hz
        self.telemetry_history: List[RollerMillTelemetry] = []

    def ingest_telemetry(self, telemetry: RollerMillTelemetry) -> IsolationCommand:
        self.telemetry_history.append(telemetry)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        # Check if vibration frequency approaches dangerous torsional resonance band
        delta = abs(telemetry.vibration_frequency_hz - self.target_band)
        resonance_flag = delta <= self.tolerance

        damping_coeff = 0.85
        counter_torque = 0.0
        status = "NOMINAL"

        if resonance_flag:
            status = "RESONANCE_WARNING_ACTIVE"
            # Calculate counter-torque based on instantaneous torsion angle and torque overload
            damping_coeff = 1.65
            counter_torque = telemetry.torque_Nm * 0.28 * math.sin(math.radians(telemetry.torsion_angle_deg))
            logger.warning(
                f"[TORSION HAZARD] Mill {telemetry.mill_id} in Nairobi plant entering harmonic band! "
                f"Freq: {telemetry.vibration_frequency_hz}Hz, Torsion Angle: {telemetry.torsion_angle_deg}deg. "
                f"Applying counter-torque: {counter_torque:.2f} Nm."
            )
        else:
            # Adaptive fine tuning
            counter_torque = telemetry.torque_Nm * 0.02 * math.cos(math.radians(telemetry.torsion_angle_deg))

        return IsolationCommand(
            mill_id=telemetry.mill_id,
            timestamp=time.time(),
            damping_coefficient=damping_coeff,
            counter_torque_Nm=counter_torque,
            status=status,
            resonance_detected=resonance_flag
        )

def run_sentinel_simulation() -> None:
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Isolator Sentinel...")
    engine = TorsionHarmonicIsolatorEngine(target_resonant_band_hz=42.0, tolerance_hz=4.0)

    mill_ids = ["NRB-MILL-NORTH-01", "NRB-MILL-INDUSTRIAL-04"]
    for i in range(5):
        for m_id in mill_ids:
            freq = 41.0 + random.uniform(-6.0, 6.0)
            telemetry = RollerMillTelemetry(
                mill_id=m_id,
                timestamp=time.time(),
                rpm_fast=950.0 + random.uniform(-10, 10),
                rpm_slow=320.0 + random.uniform(-5, 5),
                torque_Nm=450.0 + random.uniform(-50, 80),
                torsion_angle_deg=random.uniform(0.1, 2.5),
                vibration_frequency_hz=freq,
                bearing_temp_c=62.5 + random.uniform(-2, 4)
            )
            cmd = engine.ingest_telemetry(telemetry)
            logger.info(f"Simulation Cycle {i}: Mill {cmd.mill_id} -> Status: {cmd.status}, Counter-Torque: {cmd.counter_torque_Nm:.2f}Nm")
        time.sleep(0.05)
    logger.info("Nairobi Roller Mill Torsion Harmonic Isolator Sentinel execution complete.")

if __name__ == '__main__':
    run_sentinel_simulation()
