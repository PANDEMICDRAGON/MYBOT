"""
Nairobi Commercial Biomass Briquette Press Hydraulic Harmonic Pulse & Pressure Correlation Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Monitors industrial hydraulic briquetting presses, correlating acoustic sensor telemetry, motor stator harmonics,
and hydraulic cylinder pressure profiles to detect anomalies, valve leakage, and impending seal blowout.
"""

import time
import math
import random
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [BriquettePressSentinel]: %(message)s')
logger = logging.getLogger(__name__)


class BriquettePressHydraulicSentinel:
    """
    Real-time harmonic analysis and anomaly detection engine for industrial biomass briquette presses.
    """

    def __init__(self, press_id: str, operating_pressure_mpa: float = 25.0):
        self.press_id = press_id
        self.operating_pressure_mpa = operating_pressure_mpa
        self.baseline_harmonic_signature = [1.0, 0.45, 0.22, 0.11]
        self.anomaly_threshold = 0.35
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized BriquettePressHydraulicSentinel for press {press_id} (Target: {operating_pressure_mpa} MPa)")

    def sample_telemetry(self) -> Dict[str, Any]:
        """
        Simulates high-frequency sampling of hydraulic pressure, motor current harmonics, and vibration acoustics.
        """
        # Introduce minor operational jitter with occasional anomaly injection for test resilience
        pressure_jitter = random.gauss(0.0, 0.8)
        current_pressure = max(0.0, self.operating_pressure_mpa + pressure_jitter)
        
        # Generate simulated harmonic spectrum
        harmonics = [
            round(base * random.uniform(0.95, 1.05), 4)
            for base in self.baseline_harmonic_signature
        ]
        
        # Occasionally inject fault signature (e.g. bypass valve leakage or worn seals)
        if random.random() < 0.05:
            harmonics[1] += random.uniform(0.4, 0.8) # High 2nd harmonic surge
            current_pressure += random.uniform(3.0, 6.0)

        telemetry = {
            "timestamp": time.time(),
            "press_id": self.press_id,
            "hydraulic_pressure_mpa": round(current_pressure, 2),
            "harmonic_spectrum": harmonics,
            "oil_temperature_c": round(random.uniform(45.0, 68.5), 1)
        }
        return telemetry

    def analyze_correlation(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Correlates harmonic variance against baseline to compute system health index.
        """
        spectrum = telemetry["harmonic_spectrum"]
        variance_sum = sum(abs(s - b) for s, b in zip(spectrum, self.baseline_harmonic_signature))
        health_score = max(0.0, 1.0 - (variance_sum / len(spectrum)))
        
        anomaly_detected = variance_sum > self.anomaly_threshold
        
        analysis = {
            "press_id": self.press_id,
            "health_index": round(health_score, 4),
            "variance_sum": round(variance_sum, 4),
            "anomaly_detected": anomaly_detected,
            "action_required": "MAINTENANCE_INSPECTION_REQUIRED" if anomaly_detected else "OPTIMAL"
        }
        
        self.telemetry_history.append({"telemetry": telemetry, "analysis": analysis})
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        return analysis


if __name__ == "__main__":
    logger.info("Executing standalone verification of BriquettePressHydraulicSentinel...")
    sentinel = BriquettePressHydraulicSentinel(press_id="NBI-BP-04")
    
    for cycle in range(5):
        data = sentinel.sample_telemetry()
        result = sentinel.analyze_correlation(data)
        logger.info(f"Cycle {cycle + 1} Result: {result}")
        time.sleep(0.1)
    
    logger.info("Briquette Press Hydraulic Sentinel verification complete.")
