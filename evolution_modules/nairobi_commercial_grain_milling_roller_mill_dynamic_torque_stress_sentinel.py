"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Stress Sentinel
Author: Cortana, Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Monitors dynamic torque stress vectors on commercial grain milling roller mills,
evaluating torsional fluctuations, stress tensors, and structural fatigue indices.
"""

import time
import math
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillTorqueStressSentinel")

class RollerMillTorqueStressSentinel:
    """
    Computes dynamic torque stress indices and triggers preventative alerts
    for roller mill drive trains in Nairobi commercial grain mills.
    """
    def __init__(self, mill_id: str, stress_threshold_nm: float = 450.0):
        self.mill_id = mill_id
        self.stress_threshold_nm = stress_threshold_nm
        self.stress_history: List[float] = []
        logger.info(f"Initialized RollerMillTorqueStressSentinel for {{mill_id}}")

    def evaluate_stress(self, torque_samples: List[float]) -> Dict[str, Any]:
        if not torque_samples:
            return {"status": "INSUFFICIENT_DATA", "stress_index": 0.0}

        mean_torque = sum(torque_samples) / len(torque_samples)
        peak_torque = max(torque_samples)
        stress_variance = sum((t - mean_torque) ** 2 for t in torque_samples) / len(torque_samples)
        stress_rms = math.sqrt(sum(t ** 2 for t in torque_samples) / len(torque_samples))
        
        self.stress_history.append(stress_rms)
        if len(self.stress_history) > 100:
            self.stress_history.pop(0)

        anomaly_flag = stress_rms > self.stress_threshold_nm
        
        status = "CRITICAL_STRESS_WARNING" if anomaly_flag else "NOMINAL"
        if anomaly_flag:
            logger.warning(f"[{self.mill_id}] High torsional stress detected: RMS={{stress_rms:.2f}} Nm (Threshold={{self.stress_threshold_nm}} Nm)")

        return {
            "mill_id": self.mill_id,
            "status": status,
            "mean_torque": mean_torque,
            "peak_torque": peak_torque,
            "stress_rms": stress_rms,
            "stress_variance": stress_variance,
            "timestamp": time.time()
        }

if __name__ == "__main__":
    sentinel = RollerMillTorqueStressSentinel(mill_id="NAI_MILL_04_ROLL_A")
    sample_torques = [380.2, 410.5, 460.8, 490.1, 440.3, 395.0, 475.6]
    report = sentinel.evaluate_stress(sample_torques)
    print(f"Execution Report: {{report}}")
