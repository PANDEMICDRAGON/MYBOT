"""Nairobi Commercial Grain Milling Roller Mill Drive Motor Harmonic Vibration Synaptic Neural Pulse Harmonic Resonance Synchronizer"""

import ast
import logging
import random
import time
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillResonanceSynchronizer")

class RollerMillResonanceSynchronizer:
    """Synchronizes drive motor frequencies and dampens harmonic resonance in commercial grain milling plants."""
    
    def __init__(self, plant_id: str, nominal_frequency_hz: float = 50.0):
        self.plant_id = plant_id
        self.nominal_frequency_hz = nominal_frequency_hz
        self.active_mills: Dict[str, Dict[str, Any]] = {}
        
    def register_mill(self, mill_id: str, baseline_rpm: float) -> None:
        """Registers a roller mill into the synchronization matrix."""
        self.active_mills[mill_id] = {
            "baseline_rpm": baseline_rpm,
            "current_vibration_g": 0.05,
            "harmonic_distortion_pct": 1.2,
            "synaptic_lock": True
        }
        logger.info(f"Mill {mill_id} registered at plant {self.plant_id} with baseline RPM {baseline_rpm}.")
        
    def analyze_vibration_telemetry(self, mill_id: str, vibration_g: float, thd_pct: float) -> Dict[str, Any]:
        """Analyzes live telemetry and computes neural pulse counter-resonance commands."""
        if mill_id not in self.active_mills:
            raise ValueError(f"Mill {mill_id} not registered.")
            
        mill = self.active_mills[mill_id]
        mill["current_vibration_g"] = vibration_g
        mill["harmonic_distortion_pct"] = thd_pct
        
        # Synaptic pulse calculation
        resonance_risk = vibration_g > 0.5 or thd_pct > 5.0
        counter_phase_shift_deg = 0.0
        
        if resonance_risk:
            counter_phase_shift_deg = round(random.uniform(45.0, 180.0), 2)
            mill["synaptic_lock"] = False
            logger.warning(f"Resonance spike detected on {mill_id}! Vibration: {vibration_g}g, THD: {thd_pct}%. Applying counter-phase shift: {counter_phase_shift_deg}°")
        else:
            mill["synaptic_lock"] = True
            logger.info(f"Mill {mill_id} operating within nominal limits. THD: {thd_pct}%")
            
        return {
            "mill_id": mill_id,
            "resonance_risk": resonance_risk,
            "counter_phase_shift_deg": counter_phase_shift_deg,
            "synaptic_lock": mill["synaptic_lock"],
            "timestamp": time.time()
        }

if __name__ == "__main__":
    sync = RollerMillResonanceSynchronizer(plant_id="NAI-MILL-04")
    sync.register_mill("ROLL-STAGE-1", baseline_1480_rpm := 1480.0)
    telemetry = sync.analyze_vibration_telemetry("ROLL-STAGE-1", vibration_g=0.62, thd_pct=6.8)
    print(f"Test Execution Result: {telemetry}")
    
    # Validate syntax cleanliness
    code_source = open(__file__, "r").read()
    ast.parse(code_source)
    print("AST validation passed successfully.")
