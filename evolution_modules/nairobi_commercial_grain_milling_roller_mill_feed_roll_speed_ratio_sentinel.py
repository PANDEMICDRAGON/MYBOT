"""
Nairobi Commercial Grain Milling Roller Mill Feed Roll Speed Ratio Sentinel
Monitors differential speed ratios between fast and slow rolls to ensure optimal shearing and reduction.
"""

import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollSpeedRatioSentinel")


class RollerMillSpeedRatioSentinel:
    def __init__(self, target_ratio: float = 2.5, tolerance: float = 0.15):
        self.target_ratio = target_ratio
        self.tolerance = tolerance
        self.anomaly_log: List[Dict[str, Any]] = []

    def evaluate_ratio(self, mill_id: str, fast_rpm: float, slow_rpm: float) -> Dict[str, Any]:
        if slow_rpm <= 0:
            logger.error(f"[{mill_id}] Critical Error: Slow roll RPM is zero or negative.")
            return {
                "mill_id": mill_id,
                "status": "CRITICAL_FAILURE",
                "actual_ratio": 0.0,
                "deviation": 0.0,
                "timestamp": time.time()
            }

        actual_ratio = fast_rpm / slow_rpm
        deviation = abs(actual_ratio - self.target_ratio)
        status = "OPTIMAL"

        if deviation > self.tolerance:
            status = "WARNING_RATIO_DRIFT"
            if deviation > (self.tolerance * 2.0):
                status = "CRITICAL_SLIPPAGE_OR_DRIVE_FAILURE"
            
            alert_record = {
                "mill_id": mill_id,
                "status": status,
                "fast_rpm": fast_rpm,
                "slow_rpm": slow_rpm,
                "actual_ratio": round(actual_ratio, 3),
                "target_ratio": self.target_ratio,
                "timestamp": time.time()
            }
            self.anomaly_log.append(alert_record)
            logger.warning(f"[{mill_id}] {status}: Actual Ratio={actual_ratio:.2f}, Target={self.target_ratio}")

        return {
            "mill_id": mill_id,
            "status": status,
            "actual_ratio": round(actual_ratio, 3),
            "deviation": round(deviation, 3),
            "timestamp": time.time()
        }

    def get_audit_summary(self) -> Dict[str, Any]:
        return {
            "total_anomalies_recorded": len(self.anomaly_log),
            "recent_anomalies": self.anomaly_log[-5:]
        }


if __name__ == "__main__":
    sentinel = RollerMillSpeedRatioSentinel(target_ratio=2.5, tolerance=0.15)
    
    # Test normal operation
    res1 = sentinel.evaluate_ratio("MILL_A_LINE_1", 1250.0, 500.0)
    print("Test 1 (Normal):", res1)
    
    # Test speed drift anomaly
    res2 = sentinel.evaluate_ratio("MILL_A_LINE_1", 1100.0, 520.0)
    print("Test 2 (Drift):", res2)
    
    # Test critical slip anomaly
    res3 = sentinel.evaluate_ratio("MILL_A_LINE_1", 900.0, 600.0)
    print(
"Test 3 (Critical):", res3)
    
    print("Audit Summary:", sentinel.get_audit_summary())
