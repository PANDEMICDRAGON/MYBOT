import logging
import time
import random
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger('RollerMillTorqueSkewSentinel')

class RollerMillTorqueSkewSentinel:
    """
    Monitors instantaneous torque differentials between fast and slow rolls in commercial
    grain milling stands, detecting asymmetric loading, feed starvation, or mechanical skew.
    """
    def __init__(self, mill_id: str, skew_threshold_pct: float = 8.5):
        self.mill_id = mill_id
        self.skew_threshold_pct = skew_threshold_pct
        self.telemetry_history: List[Dict[str, Any]] = []

    def analyze_torque(self, fast_roll_torque_nm: float, slow_roll_torque_nm: float) -> Dict[str, Any]:
        """
        Analyzes torque skew between fast and slow counter-rotating rolls.
        """
        mean_torque = (fast_roll_torque_nm + slow_roll_torque_nm) / 2.0 if (fast_roll_torque_nm + slow_roll_torque_nm) > 0 else 1.0
        diff = abs(fast_roll_torque_nm - slow_roll_torque_nm)
        skew_pct = (diff / mean_torque) * 100.0

        status = "NORMAL"
        action = "NONE"

        if skew_pct > self.skew_threshold_pct:
            status = "CRITICAL_SKEW"
            action = "ENGAGE_AUTOMATIC_FEED_GATE_RETRACT"
            logger.warning(f"[{self.mill_id}] TORQUE SKEW DETECTED: {skew_pct:.2f}% exceeds limit ({self.skew_threshold_pct}%). Fast: {fast_roll_torque_nm}Nm, Slow: {slow_roll_torque_nm}Nm. Action: {action}")
        else:
            logger.info(f"[{self.mill_id}] Torque skew nominal: {skew_pct:.2f}%")

        record = {
            "timestamp": time.time(),
            "fast_roll_nm": fast_roll_torque_nm,
            "slow_roll_nm": slow_roll_torque_nm,
            "skew_pct": skew_pct,
            "status": status,
            "action_taken": action
        }
        self.telemetry_history.append(record)
        return record

    def get_summary(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "samples_analyzed": len(self.telemetry_history),
            "threshold_pct": self.skew_threshold_pct
        }

if __name__ == "__main__":
    sentinel = RollerMillTorqueSkewSentinel(mill_id="NAI-MILL-04")
    # Simulate normal operation
    sentinel.analyze_torque(145.2, 142.8)
    # Simulate abnormal torque skew (feed choke / bearing bind)
    sentinel.analyze_torque(180.5, 120.1)
    print(sentinel.get_summary())
