"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Microscopic Wear Sentinel
Autonomous Evolutionary Architecture Component #747
Designed for Michael Obiero, Nairobi, Kenya
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [RollerGapWearSentinel] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RollerGapMicroscopicWearSentinel:
    """
    Monitors microscopic wear patterns on roller mill corrugated rolls in grain milling facilities,
    predicting roll lifespan and optimizing gap calibration to ensure uniform particle size reduction.
    """
    
    def __init__(self, mill_id: str = "NBO_MILL_01", nominal_gap_micron: float = 150.0):
        self.mill_id = mill_id
        self.nominal_gap_micron = nominal_gap_micron
        self.wear_history: List[Dict[str, Any]] = []
        self.alarm_threshold_micron = 12.0  # Max allowable micro-deviation before re-corrugation alert
        
    def analyze_wear_telemetry(self, acoustic_emission_db: float, thermal_gradient_c: float, vibration_rms_mm_s: float, operating_hours: float) -> Dict[str, Any]:
        """
        Evaluates real-time sensor streams to calculate microscopic surface wear and estimated roll lifespan.
        """
        # Compute wear factor based on coupled thermo-acoustic and vibration metrics
        wear_rate_micron_per_100h = 0.05 + (vibration_rms_mm_s * 0.02) + (abs(thermal_gradient_c - 5.0) * 0.01)
        accumulated_wear_micron = wear_rate_micron_per_100h * (operating_hours / 100.0)
        
        effective_gap = self.nominal_gap_micron + accumulated_wear_micron
        wear_deviation = abs(effective_gap - self.nominal_gap_micron)
        
        status = "OPTIMAL"
        if wear_deviation > self.alarm_threshold_micron:
            status = "RE_CORRUGATION_RECOMMENDED"
        elif wear_deviation > (self.alarm_threshold_micron * 0.75):
            status = "WARNING_ELEVATED_WEAR"
            
        telemetry_packet = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "operating_hours": operating_hours,
            "effective_gap_micron": round(effective_gap, 3),
            "accumulated_wear_micron": round(accumulated_wear_micron, 3),
            "wear_deviation": round(wear_deviation, 3),
            "status": status
        }
        
        self.wear_history.append(telemetry_packet)
        logger.info(f"Mill {self.mill_id} | Gap: {effective_gap:.3f}um | Wear: {accumulated_wear_micron:.3f}um | Status: {status}")
        return telemetry_packet

    def get_wear_report(self) -> Dict[str, Any]:
        """Summarizes overall roller health and historical wear trends."""
        if not self.wear_history:
            return {"status": "NO_DATA"}
        
        latest = self.wear_history[-1]
        total_records = len(self.wear_history)
        return {
            "mill_id": self.mill_id,
            "total_telemetry_samples": total_records,
            "latest_status": latest["status"],
            "current_accumulated_wear_micron": latest["accumulated_wear_micron"]
        }

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Gap Microscopic Wear Sentinel Test Harness...")
    sentinel = RollerGapMicroscopicWearSentinel(mill_id="UGALI_LINE_ALPHA", nominal_gap_micron=140.0)
    
    # Simulate multi-hour operational wear tracking
    test_readings = [
        (45.2, 4.8, 0.4, 500.0),
        (48.1, 5.2, 0.6, 1200.0),
        (55.6, 7.1, 1.2, 2500.0),
        (68.9, 9.4, 2.1, 4000.0)
    ]
    
    for ae, tg, vib, hrs in test_readings:
        sentinel.analyze_wear_telemetry(acoustic_emission_db=ae, thermal_gradient_c=tg, vibration_rms_mm_s=vib, operating_hours=hrs)
        
    report = sentinel.get_wear_report()
    print(f"Execution Complete. Final Report: {report}")
