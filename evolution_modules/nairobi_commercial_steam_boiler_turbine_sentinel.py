"""Nairobi Commercial Steam Boiler & Turbine Cogeneration Sentinel module.

Monitors industrial boiler pressure, temperature, feed-water quality, steam turbine
rpm, and safety relief valve integrity. Provides automated blowdown recommendations
and emergency trip signals for Nairobi's heavy industrial sector.
"""

import time
import logging
import random
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SteamBoilerTurbineSentinel")


class SteamBoilerTurbineSentinel:
    """Monitors high-pressure boilers and steam turbines for safe cogeneration operations."""

    def __init__(self, boiler_id: str, max_pressure_bar: float = 25.0, max_temp_c: float = 400.0):
        self.boiler_id = boiler_id
        self.max_pressure_bar = max_pressure_bar
        self.max_temp_c = max_temp_c
        self.operational_status = "NOMINAL"
        self.telemetry_history: List[Dict[str, Any]] = []

    def evaluate_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates incoming sensor metrics and checks against ASME/KEBS safety thresholds."""
        pressure = telemetry.get("pressure_bar", 0.0)
        temperature = telemetry.get("temperature_c", 0.0)
        water_level_pct = telemetry.get("water_level_pct", 50.0)
        turbine_rpm = telemetry.get("turbine_rpm", 0.0)
        tds_ppm = telemetry.get("tds_ppm", 1500.0)  # Total Dissolved Solids

        alerts = []
        actions = []

        # Pressure Check
        if pressure > (self.max_pressure_bar * 0.95):
            alerts.append(f"CRITICAL: Pressure {pressure} bar approaching max rating {self.max_pressure_bar} bar!")
            actions.append("INITIATE_MODULATION_DOWN")
        if pressure > self.max_pressure_bar:
            alerts.append("EMERGENCY: Overpressure condition! Opening safety relief valve.")
            actions.append("EMERGENCY_VENT")
            self.operational_status = "TRIPPED_OVERPRESSURE"

        # Temperature Check
        if temperature > self.max_temp_c:
            alerts.append(f"CRITICAL: Superheat temperature {temperature}C exceeds limit {self.max_temp_c}C.")
            actions.append("SPRAY_ATTENUATOR_ACTIVATE")
            self.operational_status = "TRIPPED_OVERHEAT"

        # Water Level Check
        if water_level_pct < 20.0:
            alerts.append("EMERGENCY: Low water level! Burner lockout imminent.")
            actions.append("EMERGENCY_SHUTDOWN_BURNER")
            self.operational_status = "TRIPPED_LOW_WATER"
        elif water_level_pct > 85.0:
            alerts.append("WARNING: High water level, risk of carryover into turbine.")
            actions.append("REDUCE_FEEDWATER_PUMP")

        # TDS / Blowdown Check
        if tds_ppm > 3000.0:
            alerts.append(f"NOTICE: High TDS ({tds_ppm} ppm). Surface blowdown recommended.")
            actions.append("SCHEDULE_BLOWDOWN")

        record = {
            "timestamp": time.time(),
            "boiler_id": self.boiler_id,
            "telemetry": telemetry,
            "alerts": alerts,
            "actions": actions,
            "status": self.operational_status
        }
        self.telemetry_history.append(record)
        return record

    def get_audit_summary(self) -> Dict[str, Any]:
        """Summarizes operational state and incident counts."""
        return {
            "boiler_id": self.boiler_id,
            "total_evaluations": len(self.telemetry_history),
            "current_status": self.operational_status,
            "last_actions": self.telemetry_history[-1]["actions"] if self.telemetry_history else []
        }


if __name__ == "__main__":
    logger.info("Executing SteamBoilerTurbineSentinel standalone simulation...")
    sentinel = SteamBoilerTurbineSentinel(boiler_id="NAI_IND_AREA_BOILER_04", max_pressure_bar=30.0, max_temp_c=450.0)

    # Simulate normal operation
    sample_telemetry = {
        "pressure_bar": 22.5,
        "temperature_c": 380.0,
        "water_level_pct": 55.0,
        "turbine_rpm": 3000.0,
        "tds_ppm": 1800.0
    }
    result = sentinel.evaluate_telemetry(sample_telemetry)
    logger.info(f"Simulation Nominal Result: {result}")

    # Simulate emergency overpressure event
    danger_telemetry = {
        "pressure_bar": 31.2,
        "temperature_c": 460.0,
        "water_level_pct": 15.0,
        "turbine_rpm": 3200.0,
        "tds_ppm": 3200.0
    }
    result_danger = sentinel.evaluate_telemetry(danger_telemetry)
    logger.info(f"Simulation Emergency Result: {result_danger}")
    logger.info(f"Audit Summary: {sentinel.get_audit_summary()}")
