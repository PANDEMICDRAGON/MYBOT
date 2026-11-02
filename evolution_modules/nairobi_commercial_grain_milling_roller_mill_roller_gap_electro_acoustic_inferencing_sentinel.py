"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Electro Acoustic Inferencing Sentinel

Autonomous Evolutionary Architecture Component #769
Designed for Michael Obiero in Nairobi, Kenya.

Provides real-time monitoring, spectral analysis, and closed-loop compensation for roller gap tolerances
and acoustic anomalies in industrial grain roller mills.
"""

import os
import sys
import time
import math
import json
import logging
import threading
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerGapElectroAcousticInferencingSentinel")

class RollerGapElectroAcousticInferencingSentinel:
    """
    Monitors roller mill gap geometry via electro-acoustic transducers, predicts mechanical
    wear or grain feed inconsistency, and emits automated compensation signals.
    """
    def __init__(self, mill_id: str = "NBO-MILL-01", target_gap_microns: float = 120.0):
        self.mill_id = mill_id
        self.target_gap_microns = target_gap_microns
        self.running = False
        self._lock = threading.Lock()
        self.telemetry_history: List[Dict[str, Any]] = []
        self.anomaly_count = 0

    def start_monitoring(self) -> None:
        with self._lock:
            self.running = True
        logger.info(f"[{self.mill_id}] Electro-Acoustic Inferencing Sentinel activated for target gap {self.target_gap_microns}um.")

    def stop_monitoring(self) -> None:
        with self._lock:
            self.running = False
        logger.info(f"[{self.mill_id}] Electro-Acoustic Inferencing Sentinel deactivated.")

    def process_sensor_frame(self, acoustic_amplitude_db: float, current_gap_microns: float, vibration_hz: float) -> Dict[str, Any]:
        """
        Analyzes incoming electro-acoustic and gap telemetry to detect micro-collisions,
        bearing micro-fractures, or uneven grain feed.
        """
        gap_delta = current_gap_microns - self.target_gap_microns
        spectral_stress_index = (abs(acoustic_amplitude_db) * 0.6) + (abs(vibration_hz) * 0.4)
        
        status = "NOMINAL"
        correction_offset = 0.0

        if abs(gap_delta) > 15.0 or spectral_stress_index > 85.0:
            status = "WARNING"
            correction_offset = -0.5 * gap_delta
        if abs(gap_delta) > 30.0 or spectral_stress_index > 120.0:
            status = "CRITICAL"
            correction_offset = -0.8 * gap_delta
            with self._lock:
                self.anomaly_count += 1

        payload = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "acoustic_amplitude_db": acoustic_amplitude_db,
            "current_gap_microns": current_gap_microns,
            "gap_delta": gap_delta,
            "vibration_hz": vibration_hz,
            "spectral_stress_index": spectral_stress_index,
            "status": status,
            "recommended_correction_microns": correction_offset
        }

        with self._lock:
            self.telemetry_history.append(payload)
            if len(self.telemetry_history) > 1000:
                self.telemetry_history.pop(0)

        return payload

    def get_diagnostics(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "mill_id": self.mill_id,
                "running": self.running,
                "anomaly_count": self.anomaly_count,
                "last_telemetry": self.telemetry_history[-1] if self.telemetry_history else None
            }

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Roller Gap Electro Acoustic Inferencing Sentinel Test...")
    sentinel = RollerGapElectroAcousticInferencingSentinel(mill_id="TEST-MILL-99", target_gap_microns=100.0)
    sentinel.start_monitoring()
    
    # Simulate frames
    sample_frame = sentinel.process_sensor_frame(acoustic_amplitude_db=72.5, current_gap_microns=112.0, vibration_hz=45.0)
    print("Sample Frame Result:", json.dumps(sample_frame, indent=2))
    
    diag = sentinel.get_diagnostics()
    print("Diagnostics:", json.dumps(diag, indent=2))
    sentinel.stop_monitoring()
    print("Sentinel Test Completed Successfully.")
