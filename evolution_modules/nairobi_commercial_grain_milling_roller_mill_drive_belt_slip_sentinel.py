"""Nairobi Commercial Grain Milling Roller Mill Drive Belt Slip Sentinel Module."""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("RollerMillDriveBeltSlipSentinel")


class RollerMillDriveBeltSlipSentinel:
    """Monitors slip ratio between motor drive pulley and roller mill roll spindle."""

    def __init__(self, slip_threshold_percent: float = 3.5, sample_window: int = 10) -> None:
        self.slip_threshold_percent = slip_threshold_percent
        self.sample_window = sample_window
        self.history: List[Dict[str, Any]] = []

    def evaluate_belt_status(self, mill_id: str, motor_rpm: float, roll_rpm: float, gear_ratio: float = 1.0) -> Dict[str, Any]:
        """Calculates slip percentage based on expected vs actual roll RPM."""
        if motor_rpm <= 0 or roll_rpm <= 0:
            return {
                "mill_id": mill_id,
                "status": "INVALID_RPM",
                "slip_percent": 0.0,
                "alert": True,
                "timestamp": time.time()
            }

        expected_roll_rpm = motor_rpm / gear_ratio
        slip_percent = max(0.0, ((expected_roll_rpm - roll_rpm) / expected_roll_rpm) * 100.0)
        
        alert = slip_percent > self.slip_threshold_percent
        status = "SLIP_CRITICAL" if alert else "NORMAL"

        record = {
            "mill_id": mill_id,
            "motor_rpm": motor_rpm,
            "roll_rpm": roll_rpm,
            "expected_roll_rpm": expected_roll_rpm,
            "slip_percent": round(slip_percent, 2),
            "status": status,
            "alert": alert,
            "timestamp": time.time()
        }

        self.history.append(record)
        if len(self.history) > self.sample_window:
            self.history.pop(0)

        if alert:
            logger.warning("[MILL ID: %s] DRIVE BELT SLIP DETECTED! Slip: %.2f%% (Threshold: %.2f%%)", mill_id, slip_percent, self.slip_threshold_percent)
        else:
            logger.info("[MILL ID: %s] Roller mill drive belt operating normally. Slip: %.2f%%", mill_id, slip_percent)

        return record

    def get_diagnostics(self) -> Dict[str, Any]:
        """Returns rolling diagnostic statistics."""
        if not self.history:
            return {"total_readings": 0, "max_slip": 0.0, "active_alerts": 0}

        max_slip = max(item["slip_percent"] for item in self.history)
        active_alerts = sum(1 for item in self.history if item["alert"])

        return {
            "total_readings": len(self.history),
            "max_slip": max_slip,
            "active_alerts": active_alerts,
            "slip_threshold_percent": self.slip_threshold_percent
        }


if __name__ == "__main__":
    sentinel = RollerMillDriveBeltSlipSentinel(slip_threshold_percent=3.0)
    
    # Test normal operation
    sentinel.evaluate_belt_status("MILL-ALPHA-01", 1450.0, 1445.0, gear_ratio=1.0)
    
    # Test critical slip scenario
    sentinel.evaluate_belt_status(
        mill_id="MILL-ALPHA-01",
        motor_rpm=1450.0,
        roll_rpm=1380.0,
        gear_ratio=1.0
    )
    
    print("Diagnostics:", sentinel.get_diagnostics())
