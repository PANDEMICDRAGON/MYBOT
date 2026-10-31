"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Flutter Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import time
import math
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorqueFlutterSentinel")

class RollerMillTorqueFlutterSentinel:
    """
    Monitors high-frequency torque flutter on commercial grain mill roller shafts,
    preventing micro-resonance fatigue and optimizing milling roll parallelism.
    """
    def __init__(self, mill_id: str, flutter_threshold_nm: float = 14.5):
        self.mill_id = mill_id
        self.flutter_threshold_nm = flutter_threshold_nm
        self.telemetry_history: List[Dict[str, Any]] = []
        self.alert_count = 0

    def ingest_torque_signal(self, timestamp: float, torque_samples: List[float]) -> Dict[str, Any]:
        """
        Analyzes a batch of torque samples for high-frequency flutter.
        """
        if not torque_samples:
            return {"status": "NO_DATA", "flutter_index": 0.0}

        mean_torque = sum(torque_samples) / len(torque_samples)
        variance = sum((x - mean_torque) ** 2 for x in torque_samples) / len(torque_samples)
        flutter_index = math.sqrt(variance)

        status = "OPTIMAL"
        if flutter_index > self.flutter_threshold_nm:
            status = "FLUTTER_WARNING"
            self.alert_count += 1
            logger.warning(f"[{self.mill_id}] Torque flutter anomaly detected! Index: {flutter_index:.2f} Nm")

        record = {
            "timestamp": timestamp,
            "mean_torque": mean_torque,
            "flutter_index": flutter_index,
            "status": status
        }
        self.telemetry_history.append(record)
        return record

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "mill_id": self.mill_id,
            "total_samples_analyzed": len(self.telemetry_history),
            "total_alerts": self.alert_count,
            "current_status": self.telemetry_history[-1]["status"] if self.telemetry_history else "IDLE"
        }

if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Flutter Sentinel...")
    sentinel = RollerMillTorqueFlutterSentinel(mill_id="ROLLER_MILL_UGALI_01")
    
    # Simulate smooth operation
    sample_time = time.time()
    res1 = sentinel.ingest_torque_signal(sample_time, [120.5, 120.8, 120.2, 120.6, 120.4])
    print("Simulation 1:", res1)
    
    # Simulate flutter spike
    res2 = sentinel.ingest_torque_signal(sample_time + 1.0, [110.0, 145.2, 95.8, 155.4, 102.1])
    print("Simulation 2:", res2)
    
    print("Diagnostics:", sentinel.get_diagnostics())
