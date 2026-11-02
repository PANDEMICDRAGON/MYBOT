"""Nairobi Commercial Grain Milling Roller Mill Roller Gap Electro Acoustic Resonance Sentinel"""

import time
import math
import random
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RollerGapElectroAcousticResonanceSentinel")

class RollerGapElectroAcousticResonanceSentinel:
    """
    Monitors high-frequency electro-acoustic resonance across roller mill gaps in commercial
    grain milling facilities in Nairobi. Detects micro-variations in particle shear, roll gap
    drift, and harmonic distortion to optimize flour yield and prevent mechanical failure.
    """
    
    def __init__(self, mill_id: str = "NRB-MILL-01", target_frequency_hz: float = 12500.0):
        self.mill_id = mill_id
        self.target_frequency_hz = target_frequency_hz
        self.resonance_history: List[float] = []
        self.anomaly_count = 0
        logger.info(f"Initialized {self.__class__.__name__} for mill [{self.mill_id}] @ {self.target_frequency_hz}Hz")

    def sample_resonance_spectra(self) -> Dict[str, Any]:
        """Simulates real-time electro-acoustic telemetry sampling across the roller gap."""
        noise = random.gauss(0.0, 15.2)
        drift = math.sin(time.time() * 0.1) * 25.0
        current_freq = self.target_frequency_hz + noise + drift
        amplitude_db = 72.5 + (random.random() * 8.0) - (abs(noise) * 0.1)
        
        # Acoustic emission energy index
        energy_index = max(0.0, min(100.0, 50.0 + (current_freq - self.target_frequency_hz) * 0.2 + (amplitude_db - 70.0) * 0.5))
        
        telemetry = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "measured_frequency_hz": round(current_freq, 2),
            "amplitude_db": round(amplitude_db, 2),
            "energy_index": round(energy_index, 2)
        }
        
        self.resonance_history.append(energy_index)
        if len(self.resonance_history) > 100:
            self.resonance_history.pop(0)
            
        return telemetry

    def evaluate_gap_integrity(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates acoustic signature against optimal milling parameters."""
        energy = telemetry["energy_index"]
        status = "OPTIMAL"
        corrective_action = "NONE"
        
        if energy > 85.0:
            status = "CRITICAL_HIGH_SHEAR"
            corrective_action = "AUTOMATED_MICRO_RETRACT_ROLLERS"
            self.anomaly_count += 1
        elif energy < 20.0:
            status = "WARNING_CHOKE_OR_GAP_WIDENING"
            corrective_action = "INSPECT_FEED_GATE_AND_TIGHTEN_GAP"
            self.anomaly_count += 1
            
        return {
            "status": status,
            "energy_index": energy,
            "anomaly_count": self.anomaly_count,
            "corrective_action": corrective_action
        }

    def run_diagnostic_cycle(self) -> Dict[str, Any]:
        """Executes a full sample and evaluation cycle."""
        telemetry = self.sample_resonance_spectra()
        evaluation = self.evaluate_gap_integrity(telemetry)
        return {
            "telemetry": telemetry,
            "evaluation": evaluation
        }

if __name__ == "__main__":
    sentinel = RollerGapElectroAcousticResonanceSentinel(mill_id="NRB-UGALI-MILL-09")
    logger.info("Starting Roller Gap Electro Acoustic Resonance Sentinel Diagnostic Loop...")
    for i in range(3):
        result = sentinel.run_diagnostic_cycle()
        logger.info(f"Cycle {i+1} Result: {result}")
        time.sleep(0.5)
    logger.info("Sentinel diagnostic loop completed successfully.")
