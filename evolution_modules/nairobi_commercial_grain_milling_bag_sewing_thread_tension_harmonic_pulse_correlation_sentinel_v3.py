"""
Nairobi Commercial Grain Milling Bag Sewing Thread Tension Harmonic Pulse Correlation Sentinel V3
Designed for automated packaging lines in Nairobi grain mills.
"""

import os
import time
import math
import logging
import json
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("BagSewingThreadTensionSentinelV3")

class BagSewingThreadTensionSentinel:
    """
    Monitors high-speed bag sewing machine needle reciprocation and thread tension
    via harmonic pulse correlation to preempt thread breakage and loose stitches.
    """
    def __init__(self, machine_id: str = "NAI_MILL_BAG_SEW_03", nominal_tension_n: float = 12.5):
        self.machine_id = machine_id
        self.nominal_tension_n = nominal_tension_n
        self.anomaly_count = 0
        logger.info(f"Initialized {self.machine_id} with nominal tension {self.nominal_tension_n} N")

    def audit_cycle(self, telemetry_stream: List[float]) -> Dict[str, Any]:
        """
        Analyzes a batch of tension readings and vibration harmonic pulses.
        """
        if not telemetry_stream:
            return {"status": "IDLE", "risk_score": 0.0}

        mean_tension = sum(telemetry_stream) / len(telemetry_stream)
        variance = sum((t - mean_tension) ** 2 for t in telemetry_stream) / len(telemetry_stream)
        std_dev = math.sqrt(variance)

        deviation = abs(mean_tension - self.nominal_tension_n)
        risk_score = min(100.0, (deviation * 4.0) + (std_dev * 6.0))

        status = "OPTIMAL"
        if risk_score > 75.0:
            status = "CRITICAL_INTERVENTION_REQUIRED"
            self.anomaly_count += 1
            logger.error(f"[{self.machine_id}] CRITICAL: Thread tension anomaly detected! Risk: {risk_score:.2f}")
        elif risk_score > 40.0:
            status = "WARNING"
            logger.warning(f"[{self.machine_id}] WARNING: Tension drift detected. Risk: {risk_score:.2f}")
        else:
            logger.info(f"[{self.machine_id}] STATUS NORMAL. Risk: {risk_score:.2f}")

        return {
            "machine_id": self.machine_id,
            "status": status,
            "mean_tension_n": round(mean_tension, 2),
            "tension_std_dev": round(std_dev, 2),
            "risk_score": round(risk_score, 2),
            "anomaly_count": self.anomaly_count,
            "timestamp": time.time()
        }

if __name__ == "__main__":
    sentinel = BagSewingThreadTensionSentinel()
    # Test normal stream
    normal_stream = [12.4, 12.5, 12.6, 12.5, 12.4, 12.5]
    print(json.dumps(sentinel.audit_cycle(normal_stream), indent=2))
    # Test anomalous stream (tension drop/spike indicating loose thread or imminent snap)
    anomalous_stream = [8.1, 16.4, 7.2, 18.9, 11.1, 19.5]
    print(json.dumps(sentinel.audit_cycle(anomalous_stream), indent=2))
