"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torque Phase Sentinel
Designed to safeguard high-throughput dual-roll flour milling machinery in Nairobi, Kenya.
"""

import time
import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerMillDynamicTorquePhaseSentinel")


class RollerMillDynamicTorquePhaseSentinel:
    """
    Monitors electrical phase angles and dynamic torque vectors across dual roller mill drives.
    Detects phase skew, stator asymmetry, and mechanical load decoupling.
    """

    def __init__(self, mill_id: str, rated_frequency_hz: float = 50.0):
        self.mill_id = mill_id
        self.rated_frequency_hz = rated_frequency_hz
        self.phase_skew_threshold_deg = 3.5
        self.torque_ripple_limit_nm = 12.0
        self.incident_log: List[Dict[str, Any]] = []

    def analyze_drive_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes current, voltage phase angles, and instantaneous torque readings.
        
        Expected telemetry keys:
        - phase_a_angle_deg: float
        - phase_b_angle_deg: float
        - phase_c_angle_deg: float
        - fast_roll_torque_nm: float
        - slow_roll_torque_nm: float
        - motor_current_imbalance_pct: float
        """
        pa = telemetry.get("phase_a_angle_deg", 0.0)
        pb = telemetry.get("phase_b_angle_deg", 120.0)
        pc = telemetry.get("phase_c_angle_deg", 240.0)

        # Ideal 3-phase separation is 120 degrees
        skew_ab = abs((pb - pa) - 120.0)
        skew_bc = abs((pc - pb) - 120.0)
        skew_ca = abs((pa - pc) - 120.0)
        max_skew = max(skew_ab, skew_bc, skew_ca)

        fast_torque = telemetry.get("fast_roll_torque_nm", 50.0)
        slow_roll_torque = telemetry.get(
            "slow_roll_torque_nm", 45.0
        )  # typically differential ratio (e.g. 2.5:1)
        torque_delta = abs(fast_torque - (slow_roll_torque * 2.2))

        current_imbalance = telemetry.get("motor_current_imbalance_pct", 1.0)

        status = "NOMINAL"
        action_required = False
        mitigation_strategy = ""

        if max_skew > self.phase_skew_threshold_deg:
            status = "WARNING_PHASE_SKEW"
            action_required = True
            mitigation_strategy = (
                "Adjust VFD carrier frequency and inspect inverter IGBT gating."
            )

        if torque_delta > self.torque_ripple_limit_nm:
            status = "CRITICAL_TORQUE_DECOUPLING"
            action_required = True
            mitigation_strategy = (
                "Engage emergency quick-release gap actuators and inspect drive belt tension."
            )

        if current_imbalance > 5.0:
            status = "CRITICAL_MOTOR_IMBALANCE"
            action_required = True
            mitigation_strategy = (
                "Inspect stator windings for inter-turn short and check KPLC grid line stability."
            )

        assessment = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "max_phase_skew_deg": round(max_skew, 3),
            "torque_delta_nm": round(torque_delta, 3),
            "current_imbalance_pct": current_imbalance,
            "status": status,
            "action_required": action_required,
            "mitigation_strategy": mitigation_strategy,
        }

        if action_required:
            self.incident_log.append(assessment)
            logger.warning(
                f"[SENTINEL ALERT] Mill {self.mill_id} status: {status} | Strategy: {mitigation_strategy}"
            )

        return assessment


if __name__ == "__main__":
    sentinel = RollerMillDynamicTorquePhaseSentinel(mill_id="NAIROBI_MILL_ALPHA_04")
    sample_data = {
        "phase_a_angle_deg": 0.0,
        "phase_b_angle_deg": 124.2,
        "phase_c_angle_deg": 239.1,
        "fast_roll_torque_nm": 82.5,
        "slow_roll_torque_nm": 32.0,
        "motor_current_imbalance_pct": 2.1,
    }
    result = sentinel.analyze_drive_telemetry(sample_data)
    print("Sentinel Execution Test Output:", result)
