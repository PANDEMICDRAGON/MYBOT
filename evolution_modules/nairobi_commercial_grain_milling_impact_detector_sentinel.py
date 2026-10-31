"""
Nairobi Commercial Grain Milling Impact & Foreign Object Detector Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Monitors acoustic emission and vibration shock sensors on roller mill feeds to detect
foreign objects (stones, metallic debris) before they cause roll damage.
"""

import os
import time
import math
import logging
import threading
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("GrainMillingImpactSentinel")

class GrainMillingImpactSentinel:
    def __init__(self, mill_stand_id: str, shock_threshold_gs: float = 12.5):
        self.mill_stand_id = mill_stand_id
        self.shock_threshold_gs = shock_threshold_gs
        self.is_monitoring = False
        self._lock = threading.Lock()
        self.recent_events: List[Dict[str, Any]] = []
        self.trip_count = 0

    def evaluate_sensor_reading(self, vibration_g: float, acoustic_db: float) -> Dict[str, Any]:
        """Evaluates live shock and acoustic data from the mill stand feeder."""
        with self._lock:
            timestamp = time.time()
            anomaly_detected = vibration_g >= self.shock_threshold_gs
            
            reading = {
                "timestamp": timestamp,
                "mill_stand_id": self.mill_stand_id,
                "vibration_g": vibration_g,
                "acoustic_db": acoustic_db,
                "anomaly_detected": anomaly_detected
            }
            
            if anomaly_detected:
                self.trip_count += 1
                logger.warning(f"[IMPACT ALERT] Foreign object suspected on {self.mill_stand_id}! Vibration: {vibration_g}G (Threshold: {self.shock_threshold_gs}G)")
                reading["action_taken"] = "EMERGENCY_FEED_GATE_SHUTDOWN"
            else:
                reading["action_taken"] = "NORMAL_OPERATION"

            self.recent_events.append(reading)
            if len(self.recent_events) > 100:
                self.recent_events.pop(0)
                
            return reading

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "mill_stand_id": self.mill_stand_id,
                "shock_threshold_gs": self.shock_threshold_gs,
                "trip_count": self.trip_count,
                "recent_events_count": len(self.recent_events)
            }

if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Impact & Foreign Object Detector Sentinel...")
    sentinel = GrainMillingImpactSentinel(mill_stand_id="ROLL_STAND_B2_NAIROBI", shock_threshold_gs=10.0)
    
    # Simulate normal grain flow
    res1 = sentinel.evaluate_sensor_reading(vibration_g=3.2, acoustic_db=65.4)
    logger.info(f"Simulation 1: {res1}")
    
    # Simulate foreign object impact (stone or metal fragment)
    res2 = sentinel.evaluate_sensor_reading(vibration_g=14.8, acoustic_db=92.1)
    logger.info(f"Simulation 2: {res2}")
    
    print(f"Final Sentinel Status: {sentinel.get_status()}")
    logger.info("Module execution completed successfully.")
