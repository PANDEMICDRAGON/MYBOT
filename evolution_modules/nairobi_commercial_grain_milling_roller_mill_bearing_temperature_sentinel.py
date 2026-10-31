"""
Nairobi Commercial Grain Milling Roller Mill Bearing Temperature Sentinel
Designed for continuous real-time thermal monitoring of roller mill bearings in Nairobi grain mills.
"""

import time
import math
import logging
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillBearingTempSentinel")


class RollerMillBearingTempSentinel:
    """
    Monitors bearing temperatures across roller mill stands, detecting anomalous thermal gradients,
    rate-of-rise spikes, and absolute threshold violations that indicate lubrication failure or mechanical binding.
    """

    def __init__(self, warning_threshold_c: float = 75.0, critical_threshold_c: float = 90.0, max_rate_of_rise: float = 5.0):
        self.warning_threshold_c = warning_threshold_c
        self.critical_threshold_c = critical_threshold_c
        self.max_rate_of_rise = max_rate_of_rise  
        self.bearing_history: Dict[str, List[Dict[str, float]]] = {}
        self.active_alerts: Dict[str, str] = {}

    def record_temperature(self, bearing_id: str, temperature_c: float, timestamp: Optional[float] = None) -> Dict[str, Any]:
        """
        Records a temperature reading for a specific bearing and evaluates thermal health.
        """
        ts = timestamp if timestamp is not None else time.time()
        if bearing_id not in self.bearing_history:
            self.bearing_history[bearing_id] = []

        history = self.bearing_history[bearing_id]
        history.append({"timestamp": ts, "temp_c": temperature_c})

        # Retain last 20 readings
        if len(history) > 20:
            history.pop(0)

        status = "NORMAL"
        message = "Bearing operating within nominal thermal parameters."

        # Check absolute thresholds
        if temperature_c >= self.critical_threshold_c:
            status = "CRITICAL"
            message = f"CRITICAL: Bearing {bearing_id} reached {temperature_c}°C (Threshold: {self.critical_threshold_c}°C). Immediate shutdown recommended!"
            self.active_alerts[bearing_id] = message
        elif temperature_c >= self.warning_threshold_c:
            status = "WARNING"
            message = f"WARNING: Bearing {bearing_id} elevated temperature at {temperature_c}°C (Threshold: {self.warning_threshold_c}°C)."
            self.active_alerts[bearing_id] = message
        elif bearing_id in self.active_alerts and temperature_c < (self.warning_threshold_c - 5.0):
            # Clear alert with hysteresis
            del self.active_alerts[bearing_id]

        # Check rate of rise if we have at least 2 points
        if len(history) >= 2:
            dt = ts - history[-2]["timestamp"]
            if dt > 0:
                rate = (temperature_c - history[-2]["temp_c"]) / (dt / 60.0)  # °C per minute
                if rate > self.max_rate_of_rise:
                    status = "CRITICAL"
                    rate_msg = f"RAPID THERMAL SPIKE: Bearing {bearing_id} rising at {rate:.2f}°C/min."
                    message = f"{message} | {rate_msg}"
                    self.active_alerts[bearing_id] = message

        return {
            "bearing_id": bearing_id,
            "temperature_c": temperature_c,
            "status": status,
            "message": message,
            "timestamp": ts
        }

    def get_system_status(self) -> Dict[str, Any]:
        """
        Returns overall sentinel health status and active alerts.
        """
        return {
            "monitored_bearings": list(self.bearing_history.keys()),
            "active_alert_count": len(self.active_alerts),
            "active_alerts": self.active_alerts.copy()
        }


if __name__ == "__main__":
    sentinel = RollerMillBearingTempSentinel(warning_threshold_c=70.0, critical_threshold_c=85.0)
    
    # Simulate normal readings
    print(sentinel.record_temperature("STAND_1_DRIVE_SIDE", 62.5))
    print(sentinel.record_temperature("STAND_1_NON_DRIVE_SIDE", 64.0))

    # Simulate temperature spike leading to warning
    print(sentinel.record_temperature("STAND_1_DRIVE_SIDE", 72.1))
    
    # Simulate rapid thermal spike
    print(sentinel.record_temperature("STAND_2_FAST_ROLL", 86.5, timestamp=time.time() + 30))
    
    print("System Status Summary:", sentinel.get_system_status())
