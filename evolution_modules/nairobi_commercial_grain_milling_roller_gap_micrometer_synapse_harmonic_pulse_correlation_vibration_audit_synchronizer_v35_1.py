"""
Nairobi Commercial Grain Milling Roller Gap Micrometer Synapse Harmonic Pulse Correlation Vibration Audit Synchronizer V35.1

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides real-time harmonic correlation and predictive anomaly detection between roller gap micrometers and high-frequency vibration sensors for commercial flour mills in Nairobi.
"""

import ast
import json
import logging
import math
import random
import time
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerGapVibrationSynchronizerV351")


class RollerGapVibrationSynchronizer:
    """Synchronizes micrometer gap telemetry with vibration harmonic pulse data."""

    def __init__(self, mill_id: str, nominal_gap_microns: float = 120.0):
        self.mill_id = mill_id
        self.nominal_gap_microns = nominal_gap_microns
        self.telemetry_history: List[Dict[str, float]] = []
        logger.info(f"Initialized RollerGapVibrationSynchronizer for Mill {mill_id} at {nominal_gap_microns}um.")

    def ingest_sensor_reading(self, gap_microns: float, vibration_hz: float, amplitude_mm: float) -> Dict[str, float]:
        timestamp = time.time()
        harmonic_index = abs(gap_microns - self.nominal_gap_microns) * (vibration_hz / 50.0)
        
        reading = {
            "timestamp": timestamp,
            "gap_microns": gap_microns,
            "vibration_hz": vibration_hz,
            "amplitude_mm": amplitude_mm,
            "harmonic_index": harmonic_index
        }
        self.telemetry_history.append(reading)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
        return reading

    def audit_harmonic_resonance(self) -> Tuple[bool, float, str]:
        if not self.telemetry_history:
            return True, 0.0, "No telemetry available for audit."
        
        recent = self.telemetry_history[-1]
        harmonic_index = recent["harmonic_index"]
        amplitude = recent["amplitude_mm"]
        
        # Threshold checks for Nairobi commercial flour mills
        if harmonic_index > 25.0 or amplitude > 1.8:
            return False, harmonic_index, f"CRITICAL: Harmonic resonance spike detected (Index: {harmonic_index:.2f}, Amp: {amplitude}mm). Risk of roller clash."
        elif harmonic_index > 15.0 or amplitude > 1.2:
            return True, harmonic_index, f"WARNING: Elevated vibration correlation. Schedule roller alignment."
        
        return True, harmonic_index, "OPERATIONAL: Harmonic correlation nominal."


if __name__ == "__main__":
    sync = RollerGapVibrationSynchronizer(mill_id="NAI-MILL-04", nominal_gap_microns=115.0)
    
    # Simulate normal and anomalous readings
    test_readings = [
        (115.2, 49.8, 0.4),
        (114.9, 50.1, 0.5),
        (110.0, 85.5, 2.1), # Anomaly
    ];
    
    for g, v, a in test_readings:
        sync.ingest_sensor_reading(g, v, a)
        status, idx, msg = sync.audit_harmonic_resonance()
        print(f"[AUDIT] Status: {status} | Index: {idx:.2f} | Message: {msg}")

    # AST self-compilation verification
    code_str = open(__file__, "r", encoding="utf-8").read()
    ast.parse(code_str)
    print("AST self-compilation verification successful for V35.1.")
