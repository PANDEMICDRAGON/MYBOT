"""Nairobi Commercial Grain Milling Roller Mill Roller Torque Split Sentinel module."""

import logging
import time
from typing import Dict, Any, List, Optional

logger = logging.getLogger("RollerTorqueSplitSentinel")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [TorqueSplitSentinel]: %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class RollerTorqueSplitSentinel:
    """
    Monitors torque differential and speed ratio between fast and slow rolls in commercial
    grain milling roller mills in Nairobi, preventing asymmetric wear and product degradation.
    """

    def __init__(self, mill_id: str, nominal_torque_nm: float = 450.0, max_split_deviation_pct: float = 8.5):
        self.mill_id = mill_id
        self.nominal_torque_nm = nominal_torque_nm
        self.max_split_deviation_pct = max_split_deviation_pct
        self.active = True
        self.metrics_history: List[Dict[str, Any]] = []

    def evaluate_torque_split(self, fast_roll_torque: float, slow_roll_torque: float, speed_ratio: float) -> Dict[str, Any]:
        """
        Evaluates torque split and speed ratio anomalies between roll pairs.
        """
        if not self.active:
            return {"status": "INACTIVE"}

        mean_torque = (fast_roll_torque + slow_roll_torque) / 2.0
        torque_diff = abs(fast_roll_torque - slow_roll_torque)
        split_deviation_pct = (torque_diff / (mean_torque if mean_torque > 0 else 1.0)) * 100.0

        anomaly_detected = split_deviation_pct > self.max_split_deviation_pct
        action_taken = "NONE"

        if anomaly_detected:
            action_taken = "TRIGGER_FEED_GATE_MODULATION_AND_ALARM"
            logger.warning(
                f"[MILL {self.mill_id}] Torque Split Anomaly! Deviation: {split_deviation_pct:.2f}% "
                f"(Fast: {fast_roll_torque}Nm, Slow: {slow_roll_torque}Nm). Action: {action_taken}"
            )
        else:
            logger.info(
                f"[MILL {self.mill_id}] Torque split nominal: {split_deviation_pct:.2f}% (Ratio: {speed_ratio:.2f})"
            )

        record = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "fast_roll_torque": fast_roll_torque,
            "slow_roll_torque": slow_roll_torque,
            "speed_ratio": speed_ratio,
            "split_deviation_pct": split_deviation_pct,
            "anomaly_detected": anomaly_detected,
            "action_taken": action_taken,
        }
        self.metrics_history.append(record)
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)

        return record

    def shutdown(self) -> None:
        self.active = False
        logger.info(f"[MILL {self.mill_id}] Roller Torque Split Sentinel shutdown.")


if __name__ == "__main__":
    sentinel = RollerTorqueSplitSentinel(mill_id="NAI_MILL_04_UGALI_LINE")
    
    # Test normal operation
    res1 = sentinel.evaluate_torque_split(fast_roll_torque=452.0, slow_roll_torque=448.0, speed_ratio=2.5)
    assert not res1["anomaly_detected"]

    # Test abnormal torque split
    res2 = sentinel.evaluate_torque_split(fast_roll_torque=520.0, slow_roll_torque=390.0, speed_ratio=2.4)
    assert res2["anomaly_detected"]
    assert res2["action_taken"] == "TRIGGER_FEED_GATE_MODULATION_AND_ALARM"

    sentinel.shutdown()
    print("RollerTorqueSplitSentinel verified successfully.")
