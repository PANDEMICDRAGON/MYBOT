"""
Nairobi Commercial Grain Milling Grain Cleaner Deck Vibration Sentinel
Autonomous Evolutionary Architecture Component v1

Monitors cleaner deck vibration telemetry, identifies harmonic anomalies, and executes
preventive telemetry smoothing to protect heavy milling machinery in Nairobi operations.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GrainCleanerVibrationSentinel")

class GrainCleanerDeckVibrationSentinel:
    """
    Analyzes vibration frequency and amplitude from grain cleaner screening decks,
    detecting bearing degradation, eccentric drive imbalance, or screen blinding.
    """
    def __init__(self, machine_id: str = "NCGM-GC-01", target_frequency_hz: float = 16.5):
        self.machine_id = machine_id
        self.target_frequency_hz = target_frequency_hz
        self.amplitude_history: List[float] = []
        self.anomaly_count = 0
        logger.info(f"Initialized GrainCleanerDeckVibrationSentinel for {{machine_id}} at {{target_frequency_hz}} Hz.")

    def ingest_vibration_sample(self, amplitude_mm: float, frequency_hz: float) -> Dict[str, Any]:
        """
        Ingests a vibration sample and computes anomaly scores based on deviation from target frequency.
        """
        self.amplitude_history.append(amplitude_mm)
        if len(self.amplitude_history) > 100:
            self.amplitude_history.pop(0)

        freq_delta = abs(frequency_hz - self.target_frequency_hz)
        avg_amplitude = sum(self.amplitude_history) / len(self.amplitude_history)
        
        status = "NOMINAL"
        action_required = False

        if freq_delta > 2.5 or amplitude_mm > (avg_amplitude * 1.7):
            self.anomaly_count += 1
            status = "WARNING: HARMONIC IMBALANCE DETECTED"
            action_required = True
        elif freq_delta > 4.0 or amplitude_mm > (avg_amplitude * 2.2):
            self.anomaly_count += 2
            status = "CRITICAL: SCREEN DECK RESONANCE FAILURE RISK"
            action_required = True

        telemetry = {
            "machine_id": self.machine_id,
            "timestamp": time.time(),
            "amplitude_mm": amplitude_mm,
            "frequency_hz": frequency_hz,
            "freq_delta": freq_delta,
            "status": status,
            "action_required": action_required,
            "anomaly_count": self.anomaly_count
        }
        return telemetry

    def calibrate_inverter(self) -> Dict[str, str]:
        """
        Simulates automated inverter pulse adjustment to dampen resonant spikes.
        """
        logger.info(f"[{{\self.machine_id}}] Calibrating drive inverter frequency to stabilize cleaner deck...")
        time.sleep(0.05)
        return {
            "status": "SUCCESS",
            "message": f"Inverter adjusted for {{self.machine_id}} to neutralize vibration anomaly."
        }

if __name__ == "__main__":
    sentinel = GrainCleanerDeckVibrationSentinel(machine_id="NAIROBI-MILL-GC-09")
    
    # Simulate normal and anomalous runs
    for i in range(10):
        amp = 1.2 + random.uniform(-0.2, 0.2)
        freq = 16.5 + random.uniform(-0.3, 0.3)
        if i == 7:
            amp = 3.5  # Simulate sudden unbalance
            freq = 21.0
            
        result = sentinel.ingest_vibration_sample(amp, freq)
        logger.info(f"Sample {{i}}: {{result['status']}} (Amp: {{amp:.2f}}mm, Freq: {{freq:.2f}}Hz)")
        
        if result["action_required"]:
            calibration = sentinel.calibrate_inverter()
            logger.info(f"Action taken: {{calibration['message']}}")
