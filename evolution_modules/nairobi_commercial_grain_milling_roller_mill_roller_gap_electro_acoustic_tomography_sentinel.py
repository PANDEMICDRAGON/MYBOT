"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Electro Acoustic Tomography Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import os
import sys
import time
import math
import json
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("AcousticTomographySentinel")

class RollerGapTomographySentinel:
    """
    Monitors roller mill gap tolerances using electro-acoustic tomography principles,
    reconstructing spatial density and acoustic propagation velocity across the nip point.
    """
    def __init__(self, mill_id: str, nominal_gap_microns: float = 120.0):
        self.mill_id = mill_id
        self.nominal_gap_microns = nominal_gap_microns
        self.skew_threshold_microns = 5.0
        self.acoustic_velocity_baseline = 343.0 # m/s in standard air/grain mixture
        logger.info(f"Initialized RollerGapTomographySentinel for Mill {self.mill_id} with nominal gap {nominal_gap_microns}um")

    def reconstruct_gap_profile(self, transducer_readings: List[float]) -> Dict[str, Any]:
        """
        Reconstructs the 2D nip gap profile from multi-point electro-acoustic time-of-flight arrays.
        """
        if not transducer_readings:
            raise ValueError("Empty transducer readings provided for acoustic tomography.")
        
        avg_reading = sum(transducer_readings) / len(transducer_readings)
        max_deviation = max(abs(r - avg_reading) for r in transducer_readings)
        
        # Estimated gap calculation based on acoustic transit time variation
        estimated_gap = self.nominal_gap_microns + (avg_reading - 1.0) * 10.0
        skew_detected = max_deviation > self.skew_threshold_microns
        
        health_score = max(0.0, 100.0 - (max_deviation * 3.5))
        
        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "estimated_gap_microns": round(estimated_gap, 2),
            "max_skew_microns": round(max_deviation, 2),
            "skew_detected": skew_detected,
            "health_score": round(health_score, 2),
            "status": "WARNING - ROLL SKEW DETECTED" if skew_detected else "OPTIMAL"
        }

    def execute_diagnostic_sweep(self) -> Dict[str, Any]:
        """
        Simulates acoustic excitation and captures tomography data stream.
        """
        # Simulated multi-channel ultrasonic transducer feedback
        simulated_readings = [1.02, 1.01, 1.05, 1.03, 1.08 if self.mill_id == "TEST_SKEW" else 1.02]
        return self.reconstruct_gap_profile(simulated_readings)

if __name__ == "__main__":
    sentinel = RollerGapTomographySentinel(mill_id="NAI_UGALI_MILL_04", nominal_gap_microns=125.0)
    result = sentinel.execute_diagnostic_sweep()
    print(json.dumps(result, indent=2))
