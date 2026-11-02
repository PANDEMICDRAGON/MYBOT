"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Electro Acoustic Heterodyne Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import random
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HeterodyneSentinel")


class RollerGapElectroAcousticHeterodyneSentinel:
    """
    Monitors high-frequency acoustic heterodyne signals emitted across commercial roller mill gaps
    to detect micro-slippage, uneven grain feed, and roller bearing wear.
    """
    def __init__(self, mill_id: str, base_frequency_hz: float = 40000.0):
        self.mill_id = mill_id
        self.base_frequency_hz = base_frequency_hz
        self.status = "ARMED"
        self.telemetry_history: List[Dict[str, Any]] = []

    def sample_heterodyne_signal(self) -> Dict[str, Any]:
        """Simulates reading acoustic heterodyne mixing values from mill gap sensors."""
        # Generate synthetic acoustic variation with occasional anomaly spikes
        noise = random.gauss(0, 1.5)
        anomaly_factor = random.choices([1.0, 1.0, 1.0, 4.5], weights=[70, 20, 9, 1])[0]
        
        shift_hz = (noise * 12.0) * anomaly_factor
        amplitude_db = 65.0 + (noise * 2.5) * anomaly_factor
        
        timestamp = time.time()
        reading = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "heterodyne_shift_hz": round(shift_hz, 3),
            "amplitude_db": round(amplitude_db, 2),
            "anomaly_detected": abs(shift_hz) > 40.0 or amplitude_db > 75.0
        }
        
        self.telemetry_history.append(reading)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        return reading

    def evaluate_integrity(self) -> Dict[str, Any]:
        """Evaluates recent readings and triggers self-preservation protocols if needed."""
        if not self.telemetry_history:
            return {"status": "NO_DATA"}
            
        recent = self.telemetry_history[-1]
        if recent["anomaly_detected"]:
            self.status = "WARNING_HIGH_VIBRATION"
            logger.warning(f"[{self.mill_id}] Heterodyne anomaly detected! Shift: {recent['heterodyne_shift_hz']} Hz, Amp: {recent['amplitude_db']} dB")
        else:
            self.status = "NOMINAL"
            
        return {
            "mill_id": self.mill_id,
            "status": self.status,
            "latest_reading": recent,
            "total_samples": len(self.telemetry_history)
        }


if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Roller Gap Electro Acoustic Heterodyne Sentinel...")
    sentinel = RollerGapElectroAcousticHeterodyneSentinel(mill_id="NRB-MILL-04")
    
    for i in range(5):
        reading = sentinel.sample_heterodyne_signal()
        report = sentinel.evaluate_integrity()
        logger.info(f"Cycle {i+1}: {report}")
        time.sleep(0.1)
    
    logger.info("Sentinel test sequence completed successfully.")
