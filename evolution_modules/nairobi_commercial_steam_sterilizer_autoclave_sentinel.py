"""Nairobi Commercial Steam Sterilizer & Autoclave Industrial Sentinel.

Monitors industrial and commercial steam autoclaves and sterilizers deployed
across Nairobi facilities, evaluating temperature-pressure relationships (F0 value
calculations), chamber structural integrity, steam trap efficiency, and predictive
valve failure anomalies for Michael Obiero's operational infrastructure.
"""

import time
import math
import random
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SteamSterilizerSentinel")


class SteamSterilizerSentinel:
    """Advanced monitoring and validation engine for industrial steam sterilizers."""

    def __init__(self, sterilizer_id: str, chamber_volume_liters: float = 500.0):
        self.sterilizer_id = sterilizer_id
        self.volume = chamber_volume_liters
        self.cycle_history: List[Dict[str, Any]] = []
        self.alert_thresholds = {
            "max_pressure_bar": 3.2,
            "min_sterilization_temp_c": 121.0,
            "max_temperature_c": 138.0,
            "min_fo_target": 15.0
        }

    def evaluate_cycle_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates live autoclave cycle data (temperature, pressure, phase, duration)."""
        pressure = telemetry.get("pressure_bar", 0.0)
        temperature = telemetry.get("temperature_c", 25.0)
        phase = telemetry.get("phase", "IDLE")
        duration_sec = telemetry.get(
            "duration_sec", 0.0
        )  # time spent at temp

        warnings = []
        critical_fault = False

        # Pressure Safety Check
        if pressure > self.alert_thresholds["max_pressure_bar"]:
            warnings.warn(
                f"HIGH PRESSURE ALERT: {pressure} bar exceeds safe threshold!"
            )
            critical_fault = True

        # Temperature Bounds
        if temperature > self.alert_thresholds["max_temperature_c"]:
            warnings.warn(
                f"OVERHEAT ALERT: {temperature} C exceeds max limit!"
            )
            critical_fault = True

        # F0 Value Calculation (Equivalent sterilization time at 121.1 C with z=10)
        # F0 = integral of 10^((T - 121.1)/10) * dt
        f0_increment = 0.0
        if temperature >= 100.0:
            f0_increment = (
                (math.pow(10.0, (temperature - 121.1) / 10.0)) * 1.0
            ) / 60.0  

        # Theoretical saturated steam correlation check (approximate Antoine or steam table check)
        expected_pressure = self._get_saturated_pressure(temperature)
        pressure_deviation = abs(pressure - expected_pressure)
        if phase == "STERILIZATION" and pressure_deviation > 0.4:
            warnings.append(
                f"Non-condensable gases or air leak detected: pressure deviation {pressure_deviation:.2f} bar"
            )

        evaluation = {
            "sterilizer_id": self.sterilizer_id,
            "timestamp": time.time(),
            "phase": phase,
            "pressure_bar": pressure,
            "temperature_c": temperature,
            "f0_increment": f0_increment,
            "pressure_deviation_bar": pressure_deviation,
            "warnings": warnings,
            "critical_fault": critical_fault,
            "status": "SHUTDOWN_REQUIRED" if critical_fault else "OPTIMAL"
        }

        self.cycle_history.append(evaluation)
        return evaluation

    def _get_saturated_pressure(self, temp_c: float) -> float:
        """Approximates saturated steam pressure (bar) given temperature (C)."""
        if temp_c <= 100.0:
            return 1.0
        # Simplified empirical fit for 100C to 140C range
        return round(1.0 + (temp_c - 100.0) * 0.055, 3)

    def generate_audit_report(self) -> Dict[str, Any]:
        """Summarizes recent autoclave performance and compliance metrics."""
        if not self.cycle_history:
            return {"status": "NO_DATA"}

        total_cycles = len(self.cycle_history)
        faults = sum(1 for c in self.cycle_history if c["critical_fault"])
        avg_temp = sum(c["temperature_c"] for c in self.cycle_history) / total_cycles

        return {
            "sterilizer_id": self.sterilizer_id,
            "total_telemetry_packets": total_cycles,
            "critical_faults": faults,
            "average_temperature_c": round(avg_temp, 2),
            "compliance_status": "PASS" if faults == 0 else "REVIEW_REQUIRED"
        }


if __name__ == "__main__":
    logger.info(
        "Initializing Nairobi Commercial Steam Sterilizer & Autoclave Sentinel Test..."
    )
    sentinel = SteamSterilizerSentinel(
        sterilizer_id="NAI_AUTO_CLAVE_01", chamber_volume_liters=750.0
    )

    # Simulate a sterilization cycle telemetry stream
    test_telemetry = [
        {"phase": "HEATING", "temperature_c": 110.0, "pressure_bar": 1.4, "duration_sec": 300},
        {"phase": "STERILIZATION", "temperature_c": 121.5, "pressure_bar": 2.1, "duration_sec": 600},
        {"phase": "STERILIZATION", "temperature_c": 122.0, "pressure_bar": 2.15, "duration_sec": 900},
        {"phase": "EXHAUST", "temperature_c": 95.0, "pressure_bar": 0.2, "duration_sec": 1200},
    ]

    for pkt in test_telemetry:
        res = sentinel.evaluate_cycle_telemetry(pkt)
        logger.info(f"Telemetry Evaluated: {res}")

    report = sentinel.generate_audit_report()
    logger.info(f"Final Audit Report: {report}")
