"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Backlash Sentinel Module."""

import time
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillBacklashSentinel")


class RollerMillBacklashSentinel:
    """Monitors drive-train backlash, gear-mesh hysteresis, and angular play in commercial roller mills."""

    def __init__(self, mill_id: str, backlash_tolerance_deg: float = 0.75):
        self.mill_id = mill_id
        self.backlash_tolerance_deg = backlash_tolerance_deg
        self.telemetry_history: List[Dict[str, Any]] = []
        self.alert_state = False

    def evaluate_cycle(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Ingests motor shaft encoder data and opposing roller torque signals to compute mechanical play."""
        timestamp = telemetry.get("timestamp", time.time())
        motor_angle = telemetry.get("motor_angle_deg", 0.0)
        roller_angle = telemetry.get("roller_angle_deg", 0.0)
        instant_torque = telemetry.get("instant_torque_nm", 0.0)

        # Compute instantaneous angular hysteresis / backlash
        angular_play = abs(motor_angle - roller_angle)
        self.telemetry_history.append({
            "timestamp": timestamp,
            "angular_play": angular_play,
            "instant_torque": instant_torque
        })

        # Keep rolling window
        if len(self.telemetry_history) > 100:
            self.telemetry_history.pop(0)

        recent_play = [t["angular_play"] for t in self.telemetry_history]
        mean_play = statistics.mean(recent_play) if recent_play else 0.0

        self.alert_state = mean_play > self.backlash_tolerance_deg

        status = {
            "mill_id": self.mill_id,
            "timestamp": timestamp,
            "mean_angular_play_deg": round(mean_play, 4),
            "tolerance_deg": self.backlash_tolerance_deg,
            "backlash_anomaly_detected": self.alert_state
        }

        if self.alert_state:
            logger.warning(f"[BACKLASH SENTINEL] Warning: Excessive gear play detected in {self.mill_id}! Mean play: {mean_play:.2f}°")
        else:
            logger.info(f"[BACKLASH SENTINEL] {self.mill_id} mechanical backlash nominal: {mean_play:.2f}°")

        return status


if __name__ == "__main__":
    sentinel = RollerMillBacklashSentinel(mill_id="NAI-MILL-04-WESTLANDS")
    sample_telemetry = {
        "timestamp": time.time(),
        "motor_angle_deg": 142.5,
        "roller_angle_deg": 141.6,
        "instant_torque_nm": 450.2
    }
    result = sentinel.evaluate_cycle(sample_telemetry)
    print(result)
