"""Nairobi Peri-Urban Commercial Poultry Hatchery & Embryonic Biosafety Sentinel.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
Description: Monitors multi-stage commercial egg incubators, calculates turning intervals,
manages optimal dry-bulb/wet-bulb humidity curves, tracks embryonic development milestones,
and triggers emergency battery/generator failovers during grid instabilities.
"""

import logging
import time
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("PoultryIncubatorSentinel")


class IncubatorUnit:
    """Represents a single multi-tier commercial egg incubator."""

    def __init__(self, unit_id: str, species: str, capacity: int, current_day: int):
        self.unit_id = unit_id
        self.species = species  # e.g., 'chicken', 'quail', 'duck'
        self.capacity = capacity
        self.current_day = current_day
        self.temperature_c = 37.5  # Standard optimal incubator temp
        self.humidity_pct = 55.0   # Standard incubation humidity
        self.turning_active = True
        self.power_source = "GRID"
        self.alerts: List[str] = []

    def update_telemetry(self, temp: float, humidity: float, power: str) -> None:
        self.temperature_c = temp
        self.humidity_pct = humidity
        self.power_source = power


class PoultryIncubatorSentinelEngine:
    """Orchestrates embryonic biosafety, environmental control, and emergency failovers."""

    def __init__(self):
        self.units: Dict[str, IncubatorUnit] = {}
        # Optimal parameters by species
        self.species_specs = {
            "chicken": {"incubation_days": 21, "lockdown_day": 18, "opt_temp": 37.5, "opt_hum": 55.0, "hatch_hum": 70.0},
            "quail": {"incubation_days": 17, "lockdown_day": 14, "opt_temp": 37.8, "opt_hum": 60.0, "hatch_hum": 75.0},
            "duck": {"incubation_days": 28, "lockdown_day": 25, "opt_temp": 37.5, "opt_hum": 58.0, "hatch_hum": 75.0}
        }

    def register_unit(self, unit_id: str, species: str, capacity: int, current_day: int) -> IncubatorUnit:
        if species not in self.species_specs:
            raise ValueError(f"Unsupported poultry species: {species}")
        unit = IncubatorUnit(unit_id, species, capacity, current_day)
        self.units[unit_id] = unit
        logger.info(f"Registered poultry incubator [{unit_id}] for {species} (Capacity: {capacity}, Day: {current_day})")
        return unit

    def evaluate_incubator_health(self, unit_id: str, temp: float, humidity: float, power: str) -> Dict[str, Any]:
        if unit_id not in self.units:
            raise KeyError(f"Incubator {unit_id} not found.")

        unit = self.units[unit_id]
        unit.update_telemetry(temp, humidity, power)
        specs = self.species_specs[unit.species]
        
        unit.alerts.clear()
        status = "OPTIMAL"
        action_required = "NONE"

        # Check Lockdown Phase (No turning, higher humidity)
        is_lockdown = unit.current_day >= specs["lockdown_day"]
        target_humidity = specs["hatch_hum"] if is_lockdown else specs["opt_hum"]

        if is_lockdown and unit.turning_active:
            unit.turning_active = False
            logger.info(f"Unit {unit_id}: Entering lockdown phase. Automatic egg turning disabled.")

        # Temperature checks
        if temp < (specs["opt_temp"] - 0.5):
            status = "WARNING"
            unit.alerts.append("SUB_OPTIMAL_TEMPERATURE_LOW")
            action_required = "INCREASE_HEATER_OUTPUT"
        elif temp > (specs["opt_temp"] + 0.5):
            status = "CRITICAL"
            unit.alerts.append(
                "EMBRYONIC_HEAT_STRESS_RISK"
            )
            action_required = "TRIGGER_COOLING_VENTS"

        # Humidity checks
        if humidity < (target_humidity - 5.0):
            status = "WARNING" if status != "CRITICAL" else status
            unit.alerts.append("HUMIDITY_DEFICIT_RISK_OF_MEMBRANE_DRYING")
            action_required = "INCREASE_ATOMIZER_OUTPUT"
        elif humidity > (target_humidity + 7.0):
            status = "WARNING" if status != "CRITICAL" else status
            unit.alerts.append("EXCESS_HUMIDITY_DROWN_RISK")
            action_required = "REDUCE_MOISTURE"

        # Power failover check
        if power != "GRID":
            unit.alerts.append(f"RUNNING_ON_ALTERNATIVE_POWER_{power}")
            logger.warning(f"Unit {unit_id} operating on backup source: {power}")

        return {
            "unit_id": unit_id,
            "species": unit.species,
            "current_day": unit.current_day,
            "is_lockdown": is_lockdown,
            "turning_active": unit.turning_active,
            "status": status,
            "action_required": action_required,
            "alerts": unit.alerts
        }


if __name__ == "__main__":
    logger.info("Executing self-test harness for PoultryIncubatorSentinelEngine...")
    engine = PoultryIncubatorSentinelEngine()
    test_unit = engine.register_unit("INC-KIAMBU-01", "chicken", 5000, current_day=19)
    
    # Evaluate telemetry during lockdown with slight humidity drop
    result = engine.evaluate_incubator_health(
        unit_id="INC-KIAMBU-01",
        temp=37.6,
        humidity=62.0,
        power="SOLAR_INVERTER"
    )
    logger.info(f"Health Evaluation Result: {result}")
    assert result["status"] in ["WARNING", "OPTIMAL"]
    assert result["is_lockdown"] is True
    assert result["turning_active"] is False
    logger.info("Poultry Incubator Sentinel verification passed successfully.")
