"""
Nairobi Commercial Grain Milling Grain Cleaner Air Aspiration & Separator Sentinel
Designed for automated monitoring and control of grain cleaning pneumatic aspiration ducts,
cyclone separators, and deck screen vibration in Nairobi milling plants.
"""

import ast
import logging
import time
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [GRAIN_CLEANER_SENTINEL] %(levelname)s: %(message)s')
logger = logging.getLogger("GrainCleanerSentinel")

class GrainCleanerAspirationSentinel:
    """
    Monitors and adjusts the air aspiration velocity, cyclone pressure drop,
    and screen vibration frequency for commercial grain cleaners.
    """
    def __init__(self, target_air_velocity_ms: float = 12.5, target_cyclone_pa: float = 850.0):
        self.target_air_velocity_ms = target_air_velocity_ms
        self.target_cyclone_pa = target_cyclone_pa
        self.status = "STANDBY"

    def evaluate_cleaner_metrics(self, current_velocity: float, cyclone_dp: float, vibration_hz: float) -> Dict[str, Any]:
        """
        Evaluates operational telemetry from the grain cleaner system.
        """
        velocity_diff = current_velocity - self.target_air_velocity_ms
        dp_diff = cyclone_dp - self.target_cyclone_pa

        alerts: List[str] = []
        action = "OPTIMAL"

        if abs(velocity_diff) > 2.0:
            if velocity_diff < 0:
                alerts.append("Aspiration velocity too low: Risk of light chaff entering milling stream.")
                action = "INCREASE_FAN_RPM"
            else:
                alerts.append("Aspiration velocity too high: Risk of good grain loss into aspiration waste.")
                action = "DECREASE_FAN_RPM"

        if cyclone_dp < (self.target_cyclone_pa * 0.7):
            alerts.append("Cyclone pressure drop low: Possible air leak or cyclone blockage.")
            action = "INSPECT_CYCLONE_SEAL"
        elif cyclone_dp > (self.target_cyclone_pa * 1.3):
            alerts.append("Cyclone pressure drop high: Filter bag blinding or duct choking detected.")
            action = "PURGE_CYCLONE_FILTERS"

        if vibration_hz < 8.0 or vibration_hz > 16.0:
            alerts.append(f"Vibration frequency {vibration_hz}Hz outside optimal separation range (8-16Hz).")
            action = "ADJUST_ECCENTRIC_WEIGHTS"

        self.status = "ALERT" if alerts else "NORMAL"

        return {
            "status": self.status,
            "recommended_action": action,
            "alerts": alerts,
            "telemetry": {
                "air_velocity_ms": current_velocity,
                "cyclone_dp_pa": cyclone_dp,
                "vibration_hz": vibration_hz,
                "timestamp": time.time()
            }
        }

if __name__ == "__main__":
    logger.info("Initializing Grain Cleaner Air Aspiration Sentinel Test Harness...")
    sentinel = GrainCleanerAspirationSentinel()
    
    # Test suboptimal telemetry
    report = sentinel.evaluate_cleaner_metrics(current_velocity=9.2, cyclone_dp=600.0, vibration_hz=6.5)
    logger.info(f"Evaluation Report: {report}")
    
    # Verify clean AST compilation
    code_source = open(__file__, "r").read()
    parsed_ast = ast.parse(code_source)
    logger.info(f"AST compilation check passed successfully: {len(parsed_ast.body)} nodes verified.")
