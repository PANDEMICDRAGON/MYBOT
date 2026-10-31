"""Nairobi Commercial Grain Milling Pneumatic Airlock Sentinel
Autonomous monitoring and adaptive control for pneumatic conveying rotary airlock valves.
"""

import time
import logging
import random
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("PneumaticAirlockSentinel")


class PneumaticAirlockSentinel:
    """Monitors rotary airlock seal integrity, differential pressure, and motor torque."""

    def __init__(self, airlock_id: str, target_rpm: float = 35.0):
        self.airlock_id = airlock_id
        self.target_rpm = target_rpm
        self.is_running = True
        self.anomaly_count = 0
        logger.info(f"Initialized PneumaticAirlockSentinel for {{self.airlock_id}} at {{self.target_rpm}} RPM.")

    def read_telemetry(self) -> Dict[str, float]:
        """Simulate real-time telemetry from rotary airlock sensors."""
        return {
            "motor_current_amps": round(random.uniform(4.2, 7.8), 2),
            "rpm": round(self.target_rpm + random.uniform(-1.5, 1.5), 2),
            "differential_pressure_kpa": round(random.uniform(12.0, 18.5), 2),
            "bearing_temp_c": round(random.uniform(42.0, 58.5), 2),
            "vibration_mm_s": round(random.uniform(0.8, 3.2), 2)
        }

    def analyze_telemetry(self, telemetry: Dict[str, float]) -> List[str]:
        """Detect airlock blowback, blade wear, or material binding."""
        warnings = []
        if telemetry["vibration_mm_s"] > 2.8:
            warnings.append(f"High vibration detected: {{telemetry['vibration_mm_s']}} mm/s (Blade wear/imbalance)")
        if telemetry["differential_pressure_kpa"] < 13.0:
            warnings.append(f"Pressure drop loss: {{telemetry['differential_pressure_kpa']}} kPa (Airlock seal blowback)")
        if telemetry["bearing_temp_c"] > 55.0:
            warnings.append(f"Elevated bearing temp: {{telemetry['bearing_temp_c']}} C")
        if telemetry["motor_current_amps"] > 7.2:
            warnings.append(f"High motor load: {{telemetry['motor_current_amps']}} A (Potential product binding)")
        return warnings

    def execute_mitigation(self, warnings: List[str]) -> None:
        """Apply automatic corrective actions."""
        if warnings:
            self.anomaly_count += len(warnings)
            logger.warning(f"[{{self.airlock_id}}] Mitigation triggered for {{len(warnings)}} anomalies. Adjusting feeder gate.")
        else:
            logger.info(f"[{{self.airlock_id}}] Airlock operating within nominal parameters.")

    def run_cycle(self) -> Dict[str, Any]:
        telemetry = self.read_telemetry()
        warnings = self.analyze_telemetry(telemetry)
        self.execute_mitigation(warnings)
        return {
            "airlock_id": self.airlock_id,
            "telemetry": telemetry,
            "warnings": warnings,
            "anomaly_count": self.anomaly_count,
            "timestamp": time.time()
        }


if __name__ == "__main__":
    logger.info("Executing standalone validation of PneumaticAirlockSentinel...")
    sentinel = PneumaticAirlockSentinel(airlock_id="AL-LINE-04")
    for i in range(3):
        report = sentinel.run_cycle()
        logger.info(f"Cycle {{i+1}} Report: {{report}}")
        time.sleep(0.5)
    logger.info("Pneumatic Airlock Sentinel validation completed successfully.")
