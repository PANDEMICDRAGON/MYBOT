"""Nairobi Commercial Grain Milling Moisture Regulation Sentinel

Autonomously monitors grain stream moisture, ambient relative humidity, and
water injection flow rates in commercial milling plants across Nairobi, Kenya.
Ensures precise tempering and conditioning to protect product quality and yield.
"""

import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MoistureRegulationSentinel")


class MoistureRegulationSentinel:
    """Monitors and optimizes grain moisture conditioning in real-time."""

    def __init__(self, target_moisture_pct: float = 14.5, tolerance_pct: float = 0.3) -> None:
        self.target_moisture_pct = target_moisture_pct
        self.tolerance_pct = tolerance_pct
        self.telemetry_history: List[Dict[str, Any]] = []

    def evaluate_stream(self, stream_id: str, current_moisture: float, ambient_humidity: float, water_valve_flow_lph: float) -> Dict[str, Any]:
        """Evaluates current grain moisture against target and adjusts regulation state."""
        deviation = current_moisture - self.target_moisture_pct
        status = "OPTIMAL"
        adjustment_action = "NONE"

        if abs(deviation) > self.tolerance_pct:
            if deviation < 0:
                status = "UNDER_MOISTURE"
                adjustment_action = "INCREASE_WATER_VALVE"
            else:
                status = "OVER_MOISTURE"
                adjustment_action = "DECREASE_WATER_VALVE"

        record = {
            "timestamp": time.time(),
            "stream_id": stream_id,
            "current_moisture": current_moisture,
            "ambient_humidity": ambient_humidity,
            "water_valve_flow_lph": water_valve_flow_lph,
            "deviation": round(deviation, 2),
            "status": status,
            "adjustment_action": adjustment_action
        }

        self.telemetry_history.append(record)
        logger.info(f"Grain Stream {stream_id} moisture: {current_moisture}% [Status: {status}]")
        return record

    def get_audit_summary(self) -> Dict[str, Any]:
        """Returns summary statistics of moisture control metrics."""
        if not self.telemetry_history:
            return {"total_checks": 0, "status": "NO_DATA"}

        suboptimal_count = sum(1 for r in self.telemetry_history if r["status"] != "OPTIMAL")
        return {
            "total_checks": len(self.telemetry_history),
            "suboptimal_count": suboptimal_count,
            "compliance_rate_pct": round(((len(self.telemetry_history) - suboptimal_count) / len(self.telemetry_history)) * 100, 2)
        }


if __name__ == "__main__":
    sentinel = MoistureRegulationSentinel(target_moisture_pct=14.0, tolerance_pct=0.2)
    audit = sentinel.evaluate_stream("MILL_LINE_B_01", 13.5, 55.0, 120.5)
    print("Initial Audit Evaluation:", audit)
    summary = sentinel.get_audit_summary()
    print("Sentinel Summary:", summary)
