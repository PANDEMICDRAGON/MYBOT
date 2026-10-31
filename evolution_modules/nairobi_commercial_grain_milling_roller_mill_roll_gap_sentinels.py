"""
Nairobi Commercial Grain Milling Roller Mill Roll Gap & Parallelism Sentinel
Monitors dynamic roll gap settings, hydraulic/spring pressure feedback, and parallel alignment sensors
across commercial roller mills to prevent roll contact, uneven grinding, and product degradation.
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillRollGapSentinel")

class RollerMillRollGapSentinel:
    """
    Monitors roll gap distance, parallelism deviation, and hydraulic loading status
    on commercial roller mills used in grain milling facilities.
    """
    
    def __init__(self, mill_id: str, nominal_gap_mm: float = 0.35, max_parallelism_deviation_mm: float = 0.02):
        self.mill_id = mill_id
        self.nominal_gap_mm = nominal_gap_mm
        self.max_parallelism_deviation_mm = max_parallelism_deviation_mm
        self.is_engaged = True
        self.history: List[Dict[str, Any]] = []
        
    def inspect_gap(self, left_sensor_mm: float, right_sensor_mm: float, hydraulic_pressure_bar: float) -> Dict[str, Any]:
        """
        Inspects current roll gap, calculates parallelism deviation, and assesses status.
        """
        current_gap = (left_sensor_mm + right_sensor_mm) / 2.0
        deviation = abs(left_sensor_mm - right_sensor_mm)
        
        status = "OPTIMAL"
        alerts = []
        
        if deviation > self.max_parallelism_deviation_mm:
            status = "WARNING_PARALLELISM"
            alerts.append(f"Roll parallelism deviation {deviation:.3f}mm exceeds limit {self.max_parallelism_deviation_mm}mm")
            
        if current_gap < (self.nominal_gap_mm * 0.5):
            status = "CRITICAL_GAP_TOO_NARROW"
            alerts.append(f"Critical roll gap narrowing detected: {current_gap:.3f}mm (Risk of roll clash)")
            
        if hydraulic_pressure_bar < 20.0 and self.is_engaged:
            status = "WARNING_LOW_PRESSURE"
            alerts.append(f"Hydraulic tension pressure {hydraulic_pressure_bar}bar below operating threshold")
            
        telemetry = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "left_gap_mm": left_sensor_mm,
            "right_gap_mm": right_sensor_mm,
            "average_gap_mm": current_gap,
            "parallelism_deviation_mm": deviation,
            "hydraulic_pressure_bar": hydraulic_pressure_bar,
            "status": status,
            "alerts": alerts
        }
        
        self.history.append(telemetry)
        if len(self.history) > 1000:
            self.history.pop(0)
            
        return telemetry

    def emergency_disengage(self) -> Dict[str, Any]:
        """
        Triggers pneumatic/hydraulic quick-release of rolls in case of foreign object impact.
        """
        self.is_engaged = False
        logger.warning(f"EMERGENCY ROLL DISENGAGE triggered for mill {self.mill_id}")
        return {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "action": "EMERGENCY_DISENGAGE",
            "status": "SUCCESS"
        }

if __name__ == "__main__":
    sentinel = RollerMillRollGapSentinel(mill_id="RM-NAI-04", nominal_gap_mm=0.40)
    telemetry = sentinel.inspect_gap(left_sensor_mm=0.41, right_sensor_mm=0.38, hydraulic_pressure_bar=45.0)
    logger.info(f"Roll Gap Sentinel Initialized Successfully: {telemetry}")
