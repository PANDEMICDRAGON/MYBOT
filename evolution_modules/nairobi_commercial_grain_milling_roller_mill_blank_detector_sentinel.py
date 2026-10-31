"""Nairobi Commercial Grain Milling Roller Mill Blank Detector Sentinel

Monitors roller mill load current, acoustic emission, and vibration signatures
to detect 'blank running' (no grain between rolls) and prevent roll damage.
"""

import time
import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RollerMillBlankDetectorSentinel")

class RollerMillBlankDetectorSentinel:
    def __init__(self, mill_id: str, rated_amps: float = 45.0, blank_threshold_ratio: float = 0.25):
        self.mill_id = mill_id
        self.rated_amps = rated_amps
        self.blank_threshold_ratio = blank_threshold_ratio
        self.blank_current_limit = rated_amps * blank_threshold_ratio
        self.anomaly_count = 0
        logger.info(f"Initialized Blank Detector Sentinel for Mill {self.mill_id} | Blank Limit: {self.blank_current_limit:.2f}A")

    def evaluate_telemetry(self, current_amps: float, vibration_mm_s: float, acoustic_db: float) -> Dict[str, Any]:
        """
        Evaluates motor current, vibration, and acoustic level to determine if the mill is running blank.
        """
        status = "NORMAL"
        action = "NONE"

        # Blank running condition: low motor amp draw combined with high frequency acoustic noise and low vibration damping
        is_low_load = current_amps < self.blank_current_limit
        is_high_acoustic = acoustic_db > 82.0

        if is_low_load and is_high_acoustic:
            self.anomaly_count += 1
            status = "BLANK_RUNNING_DETECTED"
            if self.anomaly_count >= 3:
                action = "EMERGENCY_FEED_GATE_CLOSE"
                logger.warning(f"[{self.mill_id}] BLANK RUNNING CONFIRMED! Current: {current_amps}A, Acoustic: {acoustic_db}dB. Action: {action}")
            else:
                action = "WARNING_PENDING_TRIP"
                logger.warning(f"[{self.mill_id}] Potential blank run detected. Anomaly count: {self.anomaly_count}")
        else:
            if self.anomaly_count > 0:
                self.anomaly_count -= 1

        return {
            "mill_id": self.mill_id,
            "status": status,
            "current_amps": current_amps,
            "vibration_mm_s": vibration_mm_s,
            "acoustic_db": acoustic_db,
            "anomaly_count": self.anomaly_count,
            "action_triggered": action,
            "timestamp": time.time()
        }

if __name__ == "__main__":
    sentinel = RollerMillBlankDetectorSentinel(mill_id="RM-NAI-04")
    
    # Simulate normal load
    telemetry_normal = sentinel.evaluate_telemetry(current_amps=38.5, vibration_mm_s=2.1, acoustic_db=68.5)
    print("Normal Test:", telemetry_normal)
    
    # Simulate blank running (starved feed)
    for _ in range(3):
        telemetry_blank = sentinel.evaluate_telemetry(current_amps=9.2, vibration_mm_s=4.8, acoustic_db=85.4)
        print("Blank Test:", telemetry_blank)
