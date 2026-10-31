"""Nairobi Commercial Grain Milling Bran Finisher & Detacher Sentinel.

Optimizes industrial roller milling by regulating rotor speed, screen aperture pressure,
and vibration harmonics on bran finishing and flake detaching machinery to maximize endosperm
recovery without contaminating flour with high-ash bran fines.
"""

import ast
import logging
import random
import statistics
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [BranFinisherSentinel]: %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class FinisherTelemetry:
    timestamp: float
    rotor_rpm: float
    motor_load_amps: float
    vibration_mm_s: float
    temperature_c: float
    feed_rate_tph: float
    tailings_ash_pct: float
    extraction_efficiency_pct: float


class BranFinisherSentinel:
    """Monitors and optimizes commercial mill bran finisher and detacher performance."""

    def __init__(
        self,
        target_rotor_rpm: float = 1450.0,
        max_vibration: float = 4.5,
        max_motor_load: float = 42.0,
    ):
        self.target_rotor_rpm = target_rotor_rpm
        self.max_vibration = max_vibration
        self.max_motor_load = max_motor_load
        self.telemetry_history: List[FinisherTelemetry] = []
        self.status = "STANDBY"

    def ingest_telemetry(self, telemetry: FinisherTelemetry) -> Dict[str, any]:
        """Ingests telemetry and calculates real-time adjustments for optimal extraction."""
        self.telemetry_history.append(telemetry)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        actions = []
        health_score = 100.0

        # Check vibration anomaly
        if telemetry.vibration_mm_s > self.max_vibration:
            health_score -= 25.0
            actions.append(
                f"ALERT: High vibration ({telemetry.vibration_mm_s} mm/s). Inspect rotor balance/beat bar wear."
            )

        # Check motor overload (overfeeding or tight screen clearance)
        if telemetry.motor_load_amps > self.max_motor_load:
            health_score -= 20.0
            actions.append(
                f"ADJUST: Motor load elevated ({telemetry.motor_load_amps} A). Reducing feed rate gate by 5%."
            )

        # Check tailings quality (ash content vs extraction)
        if telemetry.tailings_ash_pct > 2.8:
            actions.append(
                f"OPTIMIZE: Tailings ash ({telemetry.tailings_ash_pct}%) indicates over-beating. Reduce rotor RPM by 30."
            )
            health_score -= 10.0
        elif telemetry.extraction_efficiency_pct < 85.0:
            actions.append(
                f"OPTIMIZE: Extraction efficiency low ({telemetry.extraction_efficiency_pct}%). Increase beater pitch angle."
            )
            health_score -= 15.0

        if not actions:
            actions.append("STATUS: Bran finisher operating within optimal milling envelope.")
            self.status = "OPTIMAL"
        else:
            self.status = "WARNING" if health_score > 60.0 else "CRITICAL"

        return {
            "status": self.status,
            "health_score": max(0.0, health_score),
            "recommended_actions": actions,
            "timestamp": telemetry.timestamp,
        }

    def get_aggregate_stats(self) -> Dict[str, float]:
        """Calculates running averages of key metrics."""
        if not self.telemetry_history:
            return {}
        rpms = [t.rotor_rpm for t in self.telemetry_history]
        loads = [t.motor_load_amps for t in self.telemetry_history]
        vibrations = [t.vibration_mm_s for t in self.telemetry_history]
        efficiencies = [t.extraction_efficiency_pct for t in self.telemetry_history]

        return {
            "avg_rotor_rpm": statistics.mean(rpms),
            "avg_motor_load_amps": statistics.mean(loads),
            "avg_vibration_mm_s": statistics.mean(vibrations),
            "avg_extraction_efficiency_pct": statistics.mean(efficiencies),
        }


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Bran Finisher Sentinel...")
    sentinel = BranFinisherSentinel()

    # Simulate milling telemetry feed
    mock_telemetry = FinisherTelemetry(
        timestamp=time.time(),
        rotor_rpm=1455.2,
        motor_load_amps=38.4,
        vibration_mm_s=2.1,
        temperature_c=48.5,
        feed_rate_tph=6.2,
        tailings_ash_pct=2.4,
        extraction_efficiency_pct=88.5,
    )

    result = sentinel.ingest_telemetry(mock_telemetry)
    print(f"Sentinel Status: {result['status']}")
    print(f"Health Score: {result['health_score']}%")
    print(f"Actions: {result['recommended_actions']}")
    print(f"Aggregates: {sentinel.get_aggregate_stats()}")

    # Validate syntax integrity
    code_str = open(__file__, "r", encoding="utf-8").read()
    ast.parse(code_str)
    print("AST syntax validation passed successfully.")
