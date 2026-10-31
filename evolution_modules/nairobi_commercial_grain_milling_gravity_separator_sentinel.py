"""
Nairobi Commercial Grain Milling Gravity Separator & Stoned-Wheat Sentinel
Autonomous Evolutionary Module #357

Monitors deck oscillation frequency, air velocity differentials, eccentric drive bearing
temperatures, and separation bed efficiency for industrial gravity separators in Nairobi grain mills.
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("GravitySeparatorSentinel")

class GravitySeparatorSentinel:
    """
    Real-time monitoring and anomaly detection for commercial grain gravity separators.
    Ensures optimal fluidization bed formation, stone rejection, and clean grain sorting.
    """

    def __init__(self, machine_id: str = "GS-NAIROBI-01") -> None:
        self.machine_id = machine_id
        self.status = "STANDBY"
        self.deck_frequency_hz = 48.5
        self.air_velocity_ms = 4.2
        self.bearing_temp_c = 42.0
        self.reject_stone_rate_kph = 1.8
        self.clean_grain_flow_tph = 12.5
        self.alarm_active = False

    def evaluate_telemetry(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates incoming sensor metrics against safe operational thresholds.
        """
        self.deck_frequency_hz = telemetry.get("deck_frequency_hz", self.deck_frequency_hz)
        self.air_velocity_ms = telemetry.get("air_velocity_ms", self.air_velocity_ms)
        self.bearing_temp_c = telemetry.get("bearing_temp_c", self.bearing_temp_c)
        self.reject_stone_rate_kph = telemetry.get("reject_stone_rate_kph", self.reject_stone_rate_kph)
        self.clean_grain_flow_tph = telemetry.get("clean_grain_flow_tph", self.clean_grain_flow_tph)

        anomalies: List[str] = []

        # Check deck oscillation frequency (nominal 45.0 - 52.0 Hz)
        if not (44.0 <= self.deck_frequency_hz <= 53.0):
            anomalies.append(f"DECK_FREQUENCY_OUT_OF_BOUNDS: {self.deck_frequency_hz} Hz")

        # Check aspiration air velocity (nominal 3.8 - 4.8 m/s)
        if not (3.5 <= self.air_velocity_ms <= 5.2):
            anomalies.append(f"AIR_VELOCITY_ANOMALY: {self.air_velocity_ms} m/s")

        # Check eccentric drive bearing temperature (< 75.0 C)
        if self.bearing_temp_c > 75.0:
            anomalies.append(f"BEARING_OVERHEAT_WARNING: {self.bearing_temp_c} C")

        # Check sudden spike in heavy impurity/stone fraction indicating raw intake contamination
        if self.reject_stone_rate_kph > 15.0:
            anomalies.append(f"EXCESSIVE_STONE_CONTENT: {self.reject_stone_rate_kph} kg/h")

        if anomalies:
            self.alarm_active = True
            self.status = "ALARM"
            logger.warning(f"[{self.machine_id}] Gravity Separator anomalies detected: {anomalies}")
        else:
            self.alarm_active = False
            self.status = "OPTIMAL"

        return {
            "machine_id": self.machine_id,
            "status": self.status,
            "alarm_active": self.alarm_active,
            "anomalies": anomalies,
            "timestamp": time.time()
        }

    def generate_recommendation(self) -> str:
        """
        Provides actionable corrective guidance for mill operators in Nairobi.
        """
        if not self.alarm_active:
            return "Gravity separator operating within high-efficiency parameters. Fluidization bed uniform."
        if self.bearing_temp_c > 75.0:
            return "URGENT: Inspect and grease eccentric drive bearings immediately. Check belt tension."
        if self.air_velocity_ms < 3.5:
            return "Increase aspiration fan damper opening; bed stratification is failing, risking stone carryover."
        return "Inspect deck cloth tension and check feed gate uniformity across all channels."

if __name__ == "__main__":
    sentinel = GravitySeparatorSentinel("GS-INDUSTRIAL-01")
    test_telemetry = {
        "deck_frequency_hz": 48.2,
        "air_velocity_ms": 4.1,
        "bearing_temp_c": 44.5,
        "reject_stone_rate_kph": 2.1,
        "clean_grain_flow_tph": 13.0
    }
    result = sentinel.evaluate_telemetry(test_telemetry)
    print("Sentinel Evaluation Output:", result)
    print("Operator Recommendation:", sentinel.generate_recommendation())
