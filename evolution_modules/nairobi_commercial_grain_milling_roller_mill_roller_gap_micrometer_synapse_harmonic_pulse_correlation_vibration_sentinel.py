"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Micrometer Synapse Harmonic Pulse Correlation Vibration Sentinel

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import time
import math
import random
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MillGapVibrationSentinel")

class RollerGapVibrationSentinel:
    """Monitors roller mill gap micrometer feedback against vibration harmonics for anomaly detection."""
    
    def __init__(self, mill_id: str, nominal_gap_microns: float = 150.0):
        self.mill_id = mill_id
        self.nominal_gap_microns = nominal_gap_microns
        self.telemetry_history: List[Dict[str, Any]] = []
        
    def sample_sensorium(self) -> Dict[str, Any]:
        """Simulates high-frequency telemetry from gap micrometer and bearing accelerometers."""
        noise = random.gauss(0, 0.8)
        current_gap = self.nominal_gap_microns + noise
        vibration_amplitude = 2.5 + abs(noise) * 1.5 + (random.random() * 0.5)
        harmonic_frequency = 50.0 + random.uniform(-0.2, 0.2)
        
        return {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "gap_microns": current_gap,
            "vibration_amplitude_mm_s": vibration_amplitude,
            "harmonic_frequency_hz": harmonic_frequency
        }
        
    def analyze_pulse_correlation(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """Correlates gap deviation with vibration harmonic spikes."""
        gap_delta = abs(sample["gap_microns"] - self.nominal_gap_microns)
        vib = sample["vibration_amplitude_mm_s"]
        
        # Harmonic anomaly threshold check
        anomaly_score = (gap_delta * 0.4) + (max(0.0, vib - 3.5) * 6.0)
        status = "OPTIMAL"
        action = "NONE"
        
        if anomaly_score > 5.0:
            status = "WARNING"
            action = "CALIBRATE_GAP_MICROMETER"
        if anomaly_score > 12.0:
            status = "CRITICAL"
            action = "EMERGENCY_ROLL_DISENGAGE"
            
        return {
            "mill_id": self.mill_id,
            "anomaly_score": round(anomaly_score, 3),
            "status": status,
            "recommended_action": action,
            "metrics": sample
        }
        
    def run_sentinel_cycle(self) -> Dict[str, Any]:
        sample = self.sample_sensorium()
        self.telemetry_history.append(sample)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
        return self.analyze_pulse_correlation(sample)

if __name__ == "__main__":
    sentinel = RollerGapVibrationSentinel(mill_id="NAIROBI-MILL-ALPHA-04")
    logger.info("Initiating Roller Gap Micrometer Synapse Harmonic Pulse Correlation Sentinel...")
    for _ in range(3):
        result = sentinel.run_sentinel_cycle()
        logger.info(f"Diagnostic Result: {result}")
        time.sleep(0.1)
