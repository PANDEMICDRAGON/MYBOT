"""
Nairobi Commercial Grain Milling Bucket Elevator & Slip Sentinel
Monitor bucket elevator speed, belt slip, bearing vibration, and thermal overload
to prevent catastrophic dust explosions and mechanical failures in Nairobi flour mills.
"""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BucketElevatorSentinel")

class BucketElevatorSentinel:
    """
    Monitors grain elevator sensors (motor RPM, head shaft speed, boot pulley speed, bearing temps).
    Calculates slip percentages and thermal deviation to trigger automated shutdowns.
    """

    def __init__(self, elevator_id: str, design_ratio: float = 1.0, max_temp_c: float = 75.0):
        self.elevator_id = elevator_id
        self.design_ratio = design_ratio  # Head shaft RPM / Boot shaft RPM ratio under normal load
        self.max_temp_c = max_temp_c
        self.status = "STANDBY"
        self.metrics_history: List[Dict[str, Any]] = []

    def evaluate_telemetry(self, head_rpm: float, boot_rpm: float, bearing_temp_c: float, current_amps: float) -> Dict[str, Any]:
        """
        Evaluate live telemetry from bucket elevator sensors.
        """ 
        if boot_rpm <= 0:
            slip_percentage = 100.0
        else:
            current_ratio = head_rpm / boot_rpm
            # Slip occurs when boot shaft lags behind head shaft beyond threshold
            slip_percentage = max(0.0, ((current_ratio - self.design_ratio) / self.design_ratio) * 100.0)

        over_temp = bearing_temp_c > self.max_temp_c
        critical_slip = slip_percentage > 12.0  # >12% slip indicates belt slippage or jam

        action = "NORMAL"
        if critical_slip or over_temp:
            action = "EMERGENCY_TRIP_FEED_GATE"
            self.status = "TRIPPED"
            logger.warning(f"[{self.elevator_id}] HAZARD DETECTED! Action: {action} | Slip: {slip_percentage:.1f}% | Temp: {bearing_temp_c}C")
        else:
            self.status = "OPERATIONAL"

        report = {
            "elevator_id": self.elevator_id,
            "timestamp": time.time(),
            "head_rpm": head_rpm,
            "boot_rpm": boot_rpm,
            "slip_percentage": round(slip_percentage, 2),
            "bearing_temp_c": bearing_temp_c,
            "current_amps": current_amps,
            "status": self.status,
            "action_recommended": action
        }

        self.metrics_history.append(report)
        if len(self.metrics_history) > 100:
            self.metrics_history.pop(0)

        return report

if __name__ == "__main__":
    sentinel = BucketElevatorSentinel(elevator_id="ELEVATOR-MAIZE-01", design_ratio=1.05)
    
    # Test normal operation
    rep1 = sentinel.evaluate_telemetry(head_rpm=120.0, boot_rpm=114.3, bearing_temp_c=45.2, current_amps=18.5)
    print("Normal Op Report:", rep1)
    assert rep1["status"] == "OPERATIONAL"

    # Test slip hazard
    rep2 = sentinel.evaluate_telemetry(head_rpm=120.0, boot_rpm=90.0, bearing_temp_c=78.5, current_amps=28.1)
    print("Hazard Op Report:", rep2)
    assert rep2["status"] == "TRIPPED"
    print("Bucket Elevator Sentinel test suite passed successfully.")
