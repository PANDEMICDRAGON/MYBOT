"""Nairobi Commercial Grain Milling Roller Mill Feed Gate Actuator Position Sentinel."""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("FeedGateActuatorSentinel")

class RollerMillFeedGateActuatorSentinel:
    """
    Monitors and regulates roller mill feed gate actuator positions for uniform grain distribution
    across grinding rolls in Nairobi commercial mills.
    """
    def __init__(self, mill_id: str, tolerance_mm: float = 0.05):
        self.mill_id = mill_id
        self.tolerance_mm = tolerance_mm
        self.actuator_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillFeedGateActuatorSentinel for Mill {mill_id} with tolerance {tolerance_mm}mm.")

    def record_actuation(self, target_position_mm: float, actual_position_mm: float, servo_current_ma: float) -> Dict[str, Any]:
        """Record a feed gate actuation telemetry cycle and detect drift or hysteresis."""
        timestamp = time.time()
        error = abs(actual_position_mm - target_position_mm)
        anomaly = error > self.tolerance_mm
        
        telemetry = {
            "timestamp": timestamp,
            "target_mm": target_position_mm,
            "actual_mm": actual_position_mm,
            "error_mm": error,
            "servo_current_ma": servo_current_ma,
            "anomaly": anomaly
        }
        
        self.actuator_history.append(telemetry)
        if len(self.actuator_history) > 1000:
            self.actuator_history.pop(0)
            
        if anomaly:
            logger.warning(f"[Mill {self.mill_id}] Feed gate drift detected! Target: {target_position_mm}mm, Actual: {actual_position_mm}mm (Error: {error:.3f}mm)")
            
        return telemetry

    def get_actuator_health_summary(self) -> Dict[str, Any]:
        """Return statistical health summary of the feed gate actuator."""
        if not self.actuator_history:
            return {"status": "no_data"}
            
        total_cycles = len(self.actuator_history)
        anomalies = sum(1 for h in self.actuator_history if h["anomaly"])
        avg_error = sum(h["error_mm"] for h in self.actuator_history) / total_cycles
        avg_current = sum(h["servo_current_ma"] for h in self.actuator_history) / total_cycles
        
        health_status = "DEGRADED" if (anomalies / total_cycles) > 0.05 else "OPTIMAL"
        
        return {
            "mill_id": self.mill_id,
            "total_cycles": total_cycles,
            "anomaly_count": anomalies,
            "average_error_mm": round(avg_error, 4),
            "average_servo_current_ma": round(avg_current, 2),
            "health_status": health_status
        }

if __name__ == "__main__":
    sentinel = RollerMillFeedGateActuatorSentinel(mill_id="NAI_CBD_MILL_04")
    
    # Simulate normal and anomalous feed gate operations
    test_cycles = [
        (2.0, 2.01, 450.0),
        (2.0, 2.02, 455.0),
        (2.0, 2.15, 620.0), # Anomaly / Binding
        (2.5, 2.50, 460.0),
        (2.5, 2.49, 458.0)
    ]
    
    for target, actual, current in test_cycles:
        sentinel.record_actuation(target, actual, current)
        
    summary = sentinel.get_actuator_health_summary()
    logger.info(f"Feed Gate Health Summary: {summary}")
