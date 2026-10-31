"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Harmonic Amplification Coefficient Deviation Sentinel"""

import time
import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillHarmonicSentinel")

class RollerMillHarmonicSentinel:
    """Monitors harmonic amplification coefficients of roller mill torque signatures to prevent catastrophic resonance."""

    def __init__(self, warning_threshold: float = 0.15, critical_threshold: float = 0.30):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.telemetry_history: List[Dict[str, Any]] = []

    def analyze_harmonic_coefficient(self, mill_id: str, base_frequency: float, measured_harmonics: List[float]) -> Dict[str, Any]:
        """Analyze the harmonic amplification coefficient deviation from baseline expectations."""
        if not measured_harmonics:
            return {"status": "ERROR", "message": "No harmonic data provided."}

        # Calculate expected vs measured amplification
        expected_fundamental = base_frequency
        dominant_harmonic = max(measured_harmonics)
        amplification_coefficient = dominant_harmonic / (expected_fundamental if expected_fundamental > 0 else 1.0)
        
        # Simulated theoretical coefficient deviation
        baseline_coefficient = 1.25
        deviation = abs(amplification_coefficient - baseline_coefficient) / baseline_coefficient

        status = "NOMINAL"
        action = "NONE"

        if deviation >= self.critical_threshold:
            status = "CRITICAL"
            action = "IMMEDIATE_INVERTER_TRIP_AND_DYNAMIC_BRAKE"
            logger.error(f"CRITICAL RESONANCE DETECTED on {mill_id}! Deviation: {deviation:.4f}")
        elif deviation >= self.warning_threshold:
            status = "WARNING"
            action = "MODULATE_FEED_GATE_AND_FREQUENCY_SHIFT"
            logger.warning(f"Harmonic amplification drift on {mill_id}. Deviation: {deviation:.4f}")
        else:
            logger.info(f"Mill {mill_id} harmonic signature nominal. Deviation: {deviation:.4f}")

        report = {
            "timestamp": time.time(),
            "mill_id": mill_id,
            "amplification_coefficient": amplification_coefficient,
            "deviation": deviation,
            "status": status,
            "action_recommended": action
        }

        self.telemetry_history.append(report)
        return report

if __name__ == "__main__":
    sentinel = RollerMillHarmonicSentinel()
    sample_harmonics = [12.5, 37.8, 75.2]
    result = sentinel.analyze_harmonic_coefficient("MILL_INDUSTRIAL_AREA_04", base_frequency=50.0, measured_harmonics=sample_harmonics)
    print("Execution Test Result:", result)
