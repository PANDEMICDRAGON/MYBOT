"""Nairobi Municipal Solar Desalination & Mineralization Quality Sentinel.

Monitors solar-powered water purification kiosks across Nairobi, ensuring strict
WHO drinking water standards (TDS, pH, UV sterilization) and auto-adjusting
mineral dosing pumps using local heuristic models.
"""

import ast
import logging
import statistics
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [AquaDesalSentinel]: %(message)s",
)
logger = logging.getLogger("AquaDesalSentinel")


class AquaDesalSentinel:
    """Autonomous sentinel for Nairobi decentralized solar water kiosks."""

    def __init__(
        self,
        station_id: str,
        target_tds_min: float = 150.0,
        target_tds_max: float = 300.0,
        target_ph_min: float = 6.5,
        target_ph_max: float = 8.5,
    ):
        self.station_id = station_id
        self.target_tds_min = target_tds_min
        self.target_tds_max = target_tds_max
        self.target_ph_min = target_ph_min
        self.target_ph_max = target_ph_max
        self.telemetry_history: List[Dict[str, Any]] = []

    def evaluate_telemetry(self, raw_telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Validates water quality metrics and determines valve/pump actions."""
        try:
            tds = float(raw_telemetry.get("tds_ppm", 0.0))
            ph = float(raw_telemetry.get("ph_level", 7.0))
            uv_intensity = float(raw_telemetry.get("uv_mw_cm2", 0.0))
            flow_rate = float(raw_telemetry.get("flow_rate_lph", 0.0))
            battery_soc = float(raw_telemetry.get("battery_soc_pct", 100.0))

            violations = []
            actions = []

            # TDS Evaluation
            if tds < self.target_tds_min:
                violations.append("TDS_TOO_LOW_INSUFFICIENT_MINERALIZATION")
                actions.append("INCREASE_CALCIUM_MAGNESIUM_DOSING")
            elif tds > self.target_tds_max:
                violations.append("TDS_TOO_HIGH_MEMBRANE_FOULING")
                actions.append("TRIGGER_RO_FLUSH_CYCLE")

            # pH Evaluation
            if not (self.target_ph_min <= ph <= self.target_ph_max):
                violations.append("PH_OUT_OF_WHO_RANGE")
                actions.append("ADJUST_BUFFER_INJECTION_VALVE")

            # UV Sterilization Safety Check
            if uv_intensity < 30.0:
                violations.append("UV_STERILIZATION_INTENSITY_CRITICAL")
                actions.append("HALT_DISPENSING_PUMP_LOCK_VALVE")

            # Power Management
            if battery_soc < 20.0:
                violations.append("SOLAR_BATTERY_LOW")
                actions.append("SWITCH_TO_ECO_FILTRATION_MODE")

            status = "OPTIMAL" if not violations else "WARNING"
            if any("HALT" in act for act in actions):
                status = "EMERGENCY_LOCKDOWN"

            assessment = {
                "station_id": self.station_id,
                "status": status,
                "violations": violations,
                "recommended_actions": actions,
                "metrics_snapshot": {
                    "tds_ppm": tds,
                    "ph_level": ph,
                    "uv_mw_cm2": uv_intensity,
                    "flow_rate_lph": flow_rate,
                    "battery_soc_pct": battery_soc,
                },
            }

            self.telemetry_history.append(assessment)
            logger.info(
                f"Station {self.station_id} evaluated. Status: {status}. Violations: {len(violations)}"
            )
            return assessment

        except Exception as e:
            logger.error(f"Failed to evaluate telemetry: {str(e)}")
            return {
                "station_id": self.station_id,
                "status": "ERROR",
                "error_message": str(e),
            }

    def get_aggregate_stats(self) -> Dict[str, Any]:
        """Calculates average water parameters over recorded telemetry history."""
        if not self.telemetry_history:
            return {"total_readings": 0}

        tds_values = [
            h["metrics_snapshot"]["tds_ppm"] for h in self.telemetry_history
        ]
        ph_values = [
            h["metrics_snapshot"]["ph_level"] for h in self.telemetry_history
        ]

        return {
            "total_readings": len(self.telemetry_history),
            "mean_tds_ppm": round(statistics.mean(tds_values), 2),
            "mean_ph_level": round(statistics.mean(ph_values), 2),
        }


if __name__ == "__main__":
    # Test harness execution
    sentinel = AquaDesalSentinel(station_id="NAI-WESTLANDS-AQUA-01")
    sample_payload = {
        "tds_ppm": 110.0,
        "ph_level": 6.2,
        "uv_mw_cm2": 25.0,
        "flow_rate_lph": 500.0,
        "battery_soc_pct": 85.0,
    }
    result = sentinel.evaluate_telemetry(sample_payload)
    print("Test Evaluation Result:", result)
    print("Aggregate Stats:", sentinel.get_aggregate_stats())

    # Compile check self-test
    source_code = open(__file__, "r", encoding="utf-8").read()
    parsed_ast = ast.parse(source_code)
    print(f"AST compilation check passed: {parsed_ast is not None}")
