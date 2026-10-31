"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Harmonic Amplification Coefficient Deviation Delta Sentinel."""

import logging
import math
import random
import time
from typing import Dict, List, Optional, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [RollerMillDeltaSentinel] %(message)s"
)
logger = logging.getLogger("RollerMillDeltaSentinel")


class RollerMillDeltaSentinel:
    """Monitors high-frequency torque harmonic coefficient deviations in industrial roller mills."""

    def __init__(self, mill_id: str, baseline_coefficient: float = 1.25, threshold: float = 0.15):
        self.mill_id = mill_id
        self.baseline_coefficient = baseline_coefficient
        self.threshold = threshold
        self.coefficient_history: List[float] = []
        logger.info(f"Initialized RollerMillDeltaSentinel for mill {mill_id} with baseline {baseline_coefficient}")

    def compute_deviation_delta(self, current_coefficient: float) -> Dict[str, Any]:
        """Computes the first and second derivative delta of harmonic amplification coefficient shifts."""
        self.coefficient_history.append(current_coefficient);
        if len(self.coefficient_history) > 50:
            self.coefficient_history.pop(0)

        deviation = current_coefficient - self.baseline_coefficient
        
        delta_rate = 0.0
        if len(self.coefficient_history) >= 2:
            delta_rate = self.coefficient_history[-1] - self.coefficient_history[-2]

        second_delta = 0.0
        if len(self.coefficient_history) >= 3:
            second_delta = (self.coefficient_history[-1] - 2 * self.coefficient_history[-2] + self.coefficient_history[-3])

        is_anomaly = abs(deviation) > self.threshold or abs(delta_rate) > (self.threshold * 0.5)

        status = {
            "mill_id": self.mill_id,
            "current_coefficient": current_coefficient,
            "deviation": round(deviation, 4),
            "delta_rate": round(delta_rate, 4),
            "second_delta": round(second_delta, 4),
            "is_anomaly": is_anomaly,
            "timestamp": time.time()
        }

        if is_anomaly:
            logger.warning(f"ANOMALY DETECTED in mill {self.mill_id}: Deviation={deviation:.4f}, DeltaRate={delta_rate:.4f}")
        else:
            logger.info(f"Mill {self.mill_id} operating nominally. Coefficient: {current_coefficient:.4f}")

        return status


if __name__ == "__main__":
    logger.info("Executing standalone diagnostic validation for RollerMillDeltaSentinel...")
    sentinel = RollerMillDeltaSentinel(mill_id="NAIROBI-UGALI-MILL-07")
    
    # Simulate normal operation followed by a sudden harmonic spike
    test_values = [1.26, 1.25, 1.27, 1.24, 1.48, 1.55]
    for val in test_values:
        report = sentinel.compute_deviation_delta(val)
        print(report)
        time.sleep(0.05)
    logger.info("RollerMillDeltaSentinel validation sequence completed successfully.")
