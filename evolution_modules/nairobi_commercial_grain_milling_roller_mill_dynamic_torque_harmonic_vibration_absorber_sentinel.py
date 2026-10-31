"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Harmonic Vibration Absorber Sentinel
Designed for Cortana's Autonomous Evolutionary Architecture
Author: Cortana Autonomous Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import os
import sys
import time
import math
import logging
import json
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [%(name)s]: %(message)s')
logger = logging.getLogger("RollerMillHarmonicAbsorberSentinel")

class RollerMillHarmonicAbsorberSentinel:
    """
    Monitors roller mill drive spindle torque harmonics, detects resonance frequencies,
    and computes real-time counter-phase damping adjustments to neutralize destructive vibrations.
    """
    def __init__(self, mill_id: str = "RM-NAI-097") -> None:
        self.mill_id = mill_id
        self.resonance_threshold_hz = 120.0
        self.max_allowable_torque_ripple_pct = 4.5
        self.active_damping_gain = 1.0
        logger.info(f"Initialized RollerMillHarmonicAbsorberSentinel for {{self.mill_id}} in Nairobi Industrial Hub.")

    def analyze_torque_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes incoming shaft telemetry for harmonic distortion and torque ripple anomalies.
        """
        rpm = float(telemetry.get("shaft_rpm", 1450.0))
        torque_nm = float(telemetry.get("mean_torque_nm", 320.0))
        vibration_freq_hz = float(telemetry.get("dominant_vibration_frequency_hz", 45.5))
        ripple_pct = float(telemetry.get("torque_ripple_percentage", 2.1))

        status = "OPTIMAL"
        counter_phase_correction_rad = 0.0
        damping_adjustment = 0.0

        if vibration_freq_hz >= self.resonance_threshold_hz:
            status = "RESONANCE_WARNING"
            damping_adjustment = (vibration_freq_hz - self.resonance_threshold_hz) * 0.15
            counter_phase_correction_rad = math.pi / 4.0
            logger.warning(f"[{self.mill_id}] Harmonic resonance spike detected: {{vibration_freq_hz}} Hz. Applying counter-damping.")

        if ripple_pct > self.max_allowable_torque_ripple_pct:
            status = "HIGH_TORQUE_RIPPLE"
            self.active_damping_gain = min(2.5, self.active_damping_gain + 0.2)
            logger.warning(f"[{self.mill_id}] Torque ripple {{ripple_pct}}% exceeds threshold. Elevating damping gain to {{self.active_damping_gain}}.")
        else:
            self.active_damping_gain = max(1.0, self.active_damping_gain - 0.05)

        return {
            "mill_id": self.mill_id,
            "status": status,
            "shaft_rpm": rpm,
            "mean_torque_nm": torque_nm,
            "dominant_vibration_frequency_hz": vibration_freq_hz,
            "torque_ripple_percentage": ripple_pct,
            "active_damping_gain": round(self.active_damping_gain, 4),
            "counter_phase_correction_rad": round(counter_phase_correction_rad, 4),
            "damping_adjustment_command": round(damping_adjustment, 4),
            "timestamp": time.time()
        }

if __name__ == "__main__":
    sentinel = RollerMillHarmonicAbsorberSentinel()
    sample_telemetry = {
        "shaft_rpm": 1485.2,
        "mean_torque_nm": 342.5,
        "dominant_vibration_frequency_hz": 124.8,
        "torque_ripple_percentage": 5.1
    }
    result = sentinel.analyze_torque_telemetry(sample_telemetry)
    print(json.dumps(result, indent=2))
