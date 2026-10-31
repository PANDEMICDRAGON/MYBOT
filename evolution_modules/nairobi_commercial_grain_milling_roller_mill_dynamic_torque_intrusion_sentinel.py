"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Intrusion Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Detects anomalous cyber-physical torque manipulation or malicious control-bus injection
in high-throughput roller mills used in Nairobi grain milling facilities.
"""

import logging
import time
import math
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [TorqueIntrusionSentinel]: %(message)s')
logger = logging.getLogger("RollerMillTorqueIntrusionSentinel")

class TorqueIntrusionSentinel:
    """
    Monitors roller mill drive torque metrics in real-time, applying baseline mathematical
    models and sliding-window anomaly detection to thwart malicious torque injection attacks.
    """
    def __init__(self, mill_id: str, baseline_torque_nm: float = 450.0, tolerance_pct: float = 12.5):
        self.mill_id = mill_id
        self.baseline_torque = baseline_torque_nm
        self.tolerance = tolerance_pct
        self.history: List[float] = []
        self.intrusion_alert_active = False

    def evaluate_torque_reading(self, current_torque: float, timestamp: Optional[float] = None) -> Dict[str, Any]:
        ts = timestamp or time.time()
        self.history.append(current_torque)
        if len(self.history) > 100:
            self.history.pop(0)

        deviation = abs(current_torque - self.baseline_torque) / self.baseline_torque * 100.0
        
        # Check for unnatural sharp jumps indicative of cyber-injection or physical jam
        is_anomaly = deviation > self.tolerance
        
        if is_anomaly:
            self.intrusion_alert_active = True
            logger.warning(f"[SECURITY ALERT] Mill {self.mill_id}: Torque anomaly detected! Reading: {current_torque} Nm (Deviation: {deviation:.2f}%)")
        else:
            self.intrusion_alert_active = False

        return {
            "mill_id": self.mill_id,
            "timestamp": ts,
            "current_torque_nm": current_torque,
            "baseline_nm": self.baseline_torque,
            "deviation_percent": round(deviation, 2),
            "intrusion_detected": is_anomaly,
            "status": "SECURE" if not is_anomaly else "THREAT_MITIGATION_ACTIVE"
        }

if __name__ == "__main__":
    sentinel = TorqueIntrusionSentinel(mill_id="NAI_MILL_ALPHA_04")
    test_readings = [452.1, 448.9, 455.0, 580.4, 451.2]
    for r in test_readings:
        res = sentinel.evaluate_torque_reading(r)
        logger.info(f"Evaluation Result: {res}")
