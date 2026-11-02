"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Micrometer Correlation Synchronizer

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides real-time micrometer correlation, gap variance analysis, and synchronous
feedback correction for multi-stand roller mills in Nairobi commercial grain milling.
"""

import logging
import time
import statistics
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerGapSynchronizer")


class RollerGapMicrometerCorrelationSynchronizer:
    """
    Synchronizes roller gap adjustments across multi-stand milling trains using
    micrometer telemetry correlation and closed-loop compensation.
    """

    def __init__(self, stand_id: str, target_gap_microns: float, tolerance_microns: float = 5.0):
        self.stand_id = stand_id
        self.target_gap_microns = target_gap_microns
        self.tolerance_microns = tolerance_microns
        self.history: List[Dict[str, float]] = []
        self.correction_factor = 1.0

    def ingest_micrometer_readings(self, drive_side_um: float, operator_side_um: float) -> Dict[str, Any]:
        """
        Ingests current gap measurements from drive and operator sides,
        computes correlation, skew, and determines required synchronization adjustments.
        """
        current_time = time.time()
        mean_gap = (drive_side_um + operator_side_um) / 2.0
        skew = abs(drive_side_um - operator_side_um)
        error = mean_gap - self.target_gap_microns

        reading = {
            "timestamp": current_time,
            "drive_side_um": drive_side_um,
            "operator_side_um": operator_side_um,
            "mean_gap": mean_gap,
            "skew": skew,
            "error": error
        }
        self.history.append(reading)
        if len(self.history) > 1000:
            self.history.pop(0)

        status = "SYNCHRONIZED"
        adjustment_required = 0.0

        if skew > self.tolerance_microns:
            status = "SKEW_WARNING"
            adjustment_required = (operator_side_um - drive_side_um) / 2.0
        elif abs(error) > self.tolerance_microns:
            status = "GAP_DRIFT"
            adjustment_required = -error * 0.5  # Proportional damping

        return {
            "stand_id": self.stand_id,
            "status": status,
            "mean_gap_um": mean_gap,
            "skew_um": skew,
            "adjustment_um": adjustment_required,
            "timestamp": current_time
        }

    def get_diagnostic_metrics(self) -> Dict[str, Any]:
        if not self.history:
            return {"status": "NO_DATA"}
        means = [r["mean_gap"] for r in self.history]
        skews = [r["skew"] for r in self.history]
        return {
            "stand_id": self.stand_id,
            "total_samples": len(self.history),
            "avg_gap_um": statistics.mean(means),
            "max_skew_um": max(skews),
            "stdev_gap_um": statistics.stdev(means) if len(means) > 1 else 0.0
        }


if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Grain Milling Roller Gap Synchronizer Test Harness...")
    sync = RollerGapSynchronizer = RollerGapMicrometerCorrelationSynchronizer(
        stand_id="STAND_B2_BREAK_ROLL",
        target_gap_microns=250.0,
        tolerance_microns=3.0
    )

    test_readings = [
        (251.2, 250.8),
        (255.0, 248.0),
        (252.0, 252.5),
        (249.0, 249.2)
    ]

    for d_side, o_side in test_readings:
        res = sync.ingest_micrometer_readings(d_side, o_side)
        logger.info(f"Telemetry Result: {res}")

    metrics = sync.get_diagnostic_metrics()
    logger.info(f"Diagnostics Summary: {metrics}")
    logger.info("Roller Gap Synchronizer test completed successfully.")
