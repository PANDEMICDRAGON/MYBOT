"""
Nairobi Commercial Grain Milling Grain Separator Screen Sentinel
Designed for automated monitoring of commercial milling pre-cleaner screens in Nairobi, Kenya.
"""

import time
import logging
import random
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GrainSeparatorScreenSentinel")

class GrainSeparatorScreenSentinel:
    """
    Monitors grain separator vibrating screen metrics including frequency (Hz),
    amplitude (mm), structural load (kg), and mesh blinding index (%) to prevent
    unfiltered impurities from passing to the destoner and roller mills.
    """
    def __init__(self, screen_id: str, rated_frequency_hz: float = 25.0):
        self.screen_id = screen_id
        self.rated_frequency_hz = rated_frequency_hz
        self.metrics_history: List[Dict[str, Any]] = []

    def evaluate_screen(self, current_hz: float, amplitude_mm: float, blinding_pct: float, load_kg: float) -> Dict[str, Any]:
        freq_deviation = abs(current_hz - self.rated_frequency_hz)
        status = "OPTIMAL"
        alerts = []

        if freq_deviation > 3.0:
            status = "WARNING"
            alerts.append(f"Frequency deviation detected: {current_hz} Hz (rated {self.rated_frequency_hz} Hz)")

        if blinding_pct > 75.0:
            status = "CRITICAL"
            alerts.append(f"High mesh blinding index: {blinding_pct}%. Immediate screen clearing required.")

        if amplitude_mm < 2.0 or amplitude_mm > 7.0:
            status = "CRITICAL" if status != "CRITICAL" else status
            alerts.append(f"Abnormal vibration amplitude: {amplitude_mm} mm.")

        payload = {
            "screen_id": self.screen_id,
            "timestamp": time.time(),
            "frequency_hz": current_hz,
            "amplitude_mm": amplitude_mm,
            "blinding_pct": blinding_pct,
            "load_kg": load_kg,
            "status": status,
            "alerts": alerts
        }

        self.metrics_history.append(payload);
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)

        return payload

if __name__ == "__main__":
    sentinel = GrainSeparatorScreenSentinel(screen_id="SCREEN-PRE-01", rated_frequency_hz=25.0)
    sample_hz = 24.8
    sample_amp = 4.2
    sample_blind = 45.0
    sample_load = 1200.0
    
    result = sentinel.evaluate_screen(sample_hz, sample_amp, sample_blind, sample_load)
    logger.info(f"Grain Separator Screen Evaluation: {result}")
