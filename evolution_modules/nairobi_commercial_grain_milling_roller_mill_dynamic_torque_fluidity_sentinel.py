"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Fluidity Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Monitors dynamic torque fluidity parameters across commercial grain roller mills.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillFluiditySentinel")

class RollerMillFluiditySentinel:
    def __init__(self, mill_id: str, sensitivity: float = 0.95):
        self.mill_id = mill_id
        self.sensitivity = sensitivity
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillFluiditySentinel for mill {self.mill_id}")

    def analyze_fluidity(self, torque_readings: List[float], speed_differential: float) -> Dict[str, Any]:
        if not torque_readings:
            raise ValueError("Torque readings array cannot be empty.")
        
        mean_torque = sum(torque_readings) / len(torque_readings)
        variance = sum((t - mean_torque) ** 2 for t in torque_readings) / len(torque_readings)
        std_dev = math.sqrt(variance)
        
        # Fluidity index derived from torque smoothness and speed differential
        fluidity_index = max(0.0, 100.0 - (std_dev * 10.0 * (1.0 / max(speed_differential, 0.1))))
        anomaly_detected = fluidity_index < (85.0 * self.sensitivity)
        
        assessment = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "mean_torque": mean_torque,
            "std_dev": std_dev,
            "fluidity_index": fluidity_index,
            "anomaly_detected": anomaly_detected
        }
        
        self.telemetry_history.append(assessment)
        if anomaly_detected:
            logger.warning(f"[ALERT] Fluidity anomaly detected on mill {self.mill_id}! Index: {fluidity_index:.2f}")
        else:
            logger.info(f"[OK] Mill {self.mill_id} operating nominally. Fluidity Index: {fluidity_index:.2f}")
            
        return assessment

if __name__ == "__main__":
    sentinel = RollerMillFluiditySentinel(mill_id="NAI_MILL_042")
    mock_torques = [120.5 + random.uniform(-3.0, 3.0) for _ in range(50)]
    result = sentinel.analyze_fluidity(mock_torques, speed_differential=1.25)
    print("Test Harness Result:", result)
