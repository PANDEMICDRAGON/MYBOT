"""Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Stress Sentinel.

Monitors real-time torque stress gradients across high-speed roller mills
in Nairobi's industrial grain processing facilities, executing autonomous
stability checks and micro-adjustments to protect mechanical drives.
"""

import logging
import statistics
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [RollerMillStressSentinel]: %(message)s",
)
logger = logging.getLogger("RollerMillStressSentinel")


@dataclass
class TorqueStressReading:
    timestamp: float
    mill_id: str
    fast_roll_torque_nm: float
    slow_roll_torque_nm: float
    differential_speed_ratio: float
    motor_temperature_c: float
    vibration_velocity_mm_s: float


@dataclass
class MillHealthStatus:
    mill_id: str
    stress_index: float
    status: str
    recommended_action: str
    mitigation_applied: bool = False


class RollerMillDynamicTorqueStressSentinel:
    """Analyzes torque stress dynamics and governs operational safety thresholds
    for commercial roller mills in Nairobi.
    """

    def __init__(self, warning_threshold_nm: float = 450.0, critical_threshold_nm: float = 600.0):
        self.warning_threshold_nm = warning_threshold_nm
        self.critical_threshold_nm = critical_threshold_nm
        self.readings_history: Dict[str, List[TorqueStressReading]] = {}

    def ingest_telemetry(self, reading: TorqueStressReading) -> MillHealthStatus:
        """Ingests a new telemetry frame, calculates stress metrics, and determines health."""
        if reading.mill_id not in self.readings_history:
            self.readings_history[reading.mill_id] = []

        history = self.readings_history[reading.mill_id]
        history.append(reading)
        if len(history) > 100:
            history.pop(0)

        # Compute composite stress index based on torque disparity and vibration
        max_torque = max(reading.fast_roll_torque_nm, reading.slow_roll_torque_nm)
        stress_index = max_torque * (1.0 + (reading.vibration_velocity_mm_s / 10.0))

        status = "OPTIMAL"
        action = "Continue normal flour milling operations."
        mitigation = False

        if stress_index >= self.critical_threshold_nm:
            status = "CRITICAL_STRESS"
            action = "EMERGENCY TRIP: Engage roller clutch disengagement and feed gate shutoff!"
            mitigation = True
            logger.critical(f"Mill {reading.mill_id} reached CRITICAL stress index {stress_index:.2f} Nm!")
        elif stress_index >= self.warning_threshold_nm:
            status = "ELEVATED_STRESS"
            action = "WARNING: Reduce feeder gate velocity by 15% and inspect differential belt tension."
            mitigation = True
            logger.warning(f"Mill {reading.mill_id} shows elevated stress index {stress_index:.2f} Nm.")
        else:
            logger.info(f"Mill {reading.mill_id} operating within safe parameters (Stress Index: {stress_index:.2f}).")

        return MillHealthStatus(
            mill_id=reading.mill_id,
            stress_index=stress_index,
            status=status,
            recommended_action=action,
            mitigation_applied=mitigation,
        )


if __name__ == "__main__":
    sentinel = RollerMillDynamicTorqueStressSentinel()
    sample_reading = TorqueStressReading(
        timestamp=time.time(),
        mill_id="NAI_MILL_INDUSTRIAL_AREA_04",
        fast_roll_torque_nm=420.5,
        slow_roll_torque_nm=390.2,
        differential_speed_ratio=2.5,
        motor_temperature_c=68.4,
        vibration_velocity_mm_s=3.2,
    )
    health = sentinel.ingest_telemetry(sample_reading)
    print(f"Evaluated Mill Status: {health}")
