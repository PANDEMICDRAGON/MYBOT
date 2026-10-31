"""
Nairobi Commercial Grain Milling Roller Mill Bearing Temperature & Vibration Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import logging
import math
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillBearingSentinel")

class RollerMillBearingSentinel:
    """
    Monitors roller mill bearing health via simulated vibration harmonics (g RMS),
    bearing race temperatures, and acoustic emission metrics. Triggers automated
    greasing cycles or emergency mill trip if wear limits are exceeded.
    """
    def __init__(self, mill_id: str, warning_temp_c: float = 75.0, critical_temp_c: float = 90.0,
                 max_vibration_g: float = 4.5):
        self.mill_id = mill_id
        self.warning_temp_c = warning_temp_c
        self.critical_temp_c = critical_temp_c
        self.max_vibration_g = max_vibration_g
        self.telemetry_history: List[Dict[str, Any]] = []
        self.auto_greased_count = 0
        self.trip_triggered = False

    def evaluate_telemetry(self, timestamp: float, temp_c: float, vibration_g: float, rpm: float) -> Dict[str, Any]:
        """
        Evaluates bearing sensor telemetry for anomalous thermal spikes or vibration harmonics.
        """
        status = "OPTIMAL"
        action_required = "NONE"
        
        if temp_c >= self.critical_temp_c or vibration_g >= self.max_vibration_g:
            status = "CRITICAL_FAULT"
            action_required = "EMERGENCY_MILL_TRIP"
            self.trip_triggered = True
            logger.error(f"[{self.mill_id}] CRITICAL FAULT! Temp: {temp_c}°C, Vib: {vibration_g}g. Trip initiated!")
        elif temp_c >= self.warning_temp_c or vibration_g >= (self.max_vibration_g * 0.75):
            status = "WARNING"
            action_required = "AUTO_GREASE_INJECTION"
            self.auto_greased_count += 1
            logger.warning(f"[{self.mill_id}] Warning threshold breached. Triggering automated grease purge (#{self.auto_greased_count}).")
        
        record = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "temp_c": temp_c,
            "vibration_g": vibration_g,
            "rpm": rpm,
            "status": status,
            "action": action_required
        }
        self.telemetry_history.append(record);
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        return record

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "trip_triggered": self.trip_triggered,
            "auto_greased_count": self.auto_greased_count,
            "total_records": len(self.telemetry_history)
        }

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Bearing Sentinel...")
    sentinel = RollerMillBearingSentinel(mill_id="MILL-RM-04")
    
    # Test nominal condition
    res1 = sentinel.evaluate_telemetry(time.time(), 62.5, 1.2, 1200.0)
    print(f"Nominal Check: {res1['status']}")
    
    # Test warning condition
    res2 = sentinel.evaluate_telemetry(time.time(), 78.0, 3.8, 1200.0)
    print(f"Warning Check: {res2['status']} | Action: {res2['action']}")
    
    # Test critical condition
    res3 = sentinel.evaluate_telemetry(time.time(), 92.5, 5.1, 1180.0)
    print(f"Critical Check: {res3['status']} | Action: {res3['action']}")
    
    print("Diagnostics:", sentinel.get_diagnostics())
    print("Roller Mill Bearing Sentinel test completed successfully.")
