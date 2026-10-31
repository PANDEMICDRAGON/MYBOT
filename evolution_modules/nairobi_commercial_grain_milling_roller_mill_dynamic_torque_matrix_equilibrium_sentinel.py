"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Equilibrium Sentinel

Maintains real-time equilibrium across multi-axis torque matrices in commercial roller mills.
Designed for industrial grain processing plants in Nairobi, Kenya.
"""

import logging
import time
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorqueEquilibriumSentinel")

class RollerMillTorqueEquilibriumSentinel:
    def __init__(self, mill_id: str, equilibrium_threshold: float = 0.05):
        self.mill_id = mill_id
        self.equilibrium_threshold = equilibrium_threshold
        self.telemetry_history: List[Dict[str, float]] = []
        self.status = "STANDBY"

    def ingest_torque_matrix(self, matrix: Dict[str, float]) -> Dict[str, Any]:
        """Ingests a multi-axis torque matrix (fast roll, slow roll, differential) and evaluates equilibrium."""
        required_axes = ["fast_roll_torque", "slow_roll_torque", "differential_torque"]
        for axis in required_axes:
            if axis not in matrix:
                raise ValueError(f"Missing required torque axis: {axis}")

        self.telemetry_history.append(matrix)
        if len(self.telemetry_history) > 100:
            self.telemetry_history.pop(0)

        # Evaluate variance between fast and slow rolls
        fast = matrix["fast_roll_torque"]
        slow = matrix["slow_roll_torque"]
        diff = matrix["differential_torque"]
        
        ratio = abs(fast - slow) / ((fast + slow) / 2.0 if (fast + slow) > 0 else 1.0)
        
        equilibrium_violated = ratio > self.equilibrium_threshold
        self.status = "WARNING_IMBALANCE" if equilibrium_violated else "EQUILIBRIUM_STABLE"

        assessment = {
            "mill_id": self.mill_id,
            "status": self.status,
            "imbalance_ratio": round(ratio, 4),
            "equilibrium_violated": equilibrium_violated,
            "timestamp": time.time()
        }

        if equilibrium_violated:
            logger.warning(f"[{self.mill_id}] Torque matrix equilibrium violated! Imbalance ratio: {ratio:.4f}")
        else:
            logger.info(f"[{self.mill_id}] Torque matrix stable. Imbalance ratio: {ratio:.4f}")

        return assessment

    def get_aggregate_stats(self) -> Dict[str, float]:
        """Computes aggregate metrics from telemetry history."""
        if not self.telemetry_history:
            return {}
        fast_torques = [m["fast_roll_torque"] for m in self.telemetry_history]
        slow_torques = [m["slow_roll_torque"] for m in self.telemetry_history]
        return {
            "mean_fast_torque": statistics.mean(fast_torques),
            "mean_slow_torque": statistics.mean(slow_torques),
            "max_imbalance_observed": max(abs(f - s) for f, s in zip(fast_torques, slow_torques))
        }

if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Matrix Equilibrium Sentinel Test...")
    sentinel = RollerMillTorqueEquilibriumSentinel(mill_id="NAI-MILL-04")
    
    # Simulate normal operation
    sample_matrix = {"fast_roll_torque": 120.5, "slow_roll_torque": 119.8, "differential_torque": 0.7}
    result = sentinel.ingest_torque_matrix(sample_matrix)
    print("Test Result 1:", result)

    # Simulate torque spike / imbalance
    imbalance_matrix = {"fast_roll_torque": 155.0, "slow_roll_torque": 110.0, "differential_torque": 45.0}
    result2 = sentinel.ingest_torque_matrix(imbalance_matrix)
    print("Test Result 2:", result2)
    print("Aggregate Stats:", sentinel.get_aggregate_stats())
    logger.info("Sentinel Test Completed Successfully.")
