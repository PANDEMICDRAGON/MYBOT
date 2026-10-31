"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Harmonic Amplification Coefficient Deviation Delta Dispersion Diamond Sentinel Module."""

import logging
import statistics
import time
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DiamondRollerMillSentinel")


class RollerMillDiamondDispersionSentinel:
    """Monitors high-frequency torque harmonic deviation and diamond dispersion parameters."""

    def __init__(self, mill_id: str, dispersion_threshold: float = 0.045):
        self.mill_id = mill_id
        self.dispersion_threshold = dispersion_threshold
        self.coefficient_history: List[float] = []
        self.anomaly_count = 0

    def record_amplification_coefficient(self, coefficient: float) -> Dict[str, Any]:
        """Record a new coefficient and evaluate diamond dispersion delta."""
        self.coefficient_history.append(coefficient)
        if len(self.coefficient_history) > 100:
            self.coefficient_history.pop(0)

        dispersion = 0.0
        if len(self.coefficient_history) >= 5:
            mean_val = statistics.mean(self.coefficient_history)
            variance = statistics.variance(self.coefficient_history, mean_val)
            stdev = statistics.stdev(self.coefficient_history, mean_val)
            dispersion = (stdev / mean_val) if mean_val != 0 else 0.0

        status = "NOMINAL"
        if dispersion > self.dispersion_threshold:
            self.anomaly_count += 1
            status = "WARNING_DIAMOND_DISPERSION_HIGH"
            logger.warning(
                f"[MILL {self.mill_id}] Diamond dispersion anomaly detected: {dispersion:.4f} (Threshold: {self.dispersion_threshold})"
            )

        return {
            "mill_id": self.mill_id,
            "timestamp": time.time(),
            "latest_coefficient": coefficient,
            "current_dispersion": dispersion,
            "anomaly_count": self.anomaly_count,
            "status": status,
        }


if __name__ == "__main__":
    sentinel = RollerMillDiamondDispersionSentinel(mill_id="NRB-MILL-099")
    test_readings = [1.02, 1.03, 1.01, 1.08, 1.15, 0.95, 1.25]
    for val in test_readings:
        res = sentinel.record_amplification_coefficient(val)
        print(res)
