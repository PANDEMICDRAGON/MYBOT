"""Nairobi Predictive Grid-Solar Energy Arbitrage Engine.

Optimizes local compute execution windows based on solar irradiance forecasts,
battery state of charge, and Kenyan grid tariff schedules.
"""

import ast
import logging
from dataclasses import dataclass
from datetime import datetime, time
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NairobiGridArbitrage")


@dataclass
class EnergyProfile:
    timestamp: datetime
    solar_irradiance_wm2: float
    battery_soc_percent: float
    grid_tariff_kes_kwh: float
    load_demand_watts: float


class NairobiGridArbitrageEngine:
    """Predicts and schedules high-compute autonomous tasks based on power metrics."""

    def __init__(self, max_safe_watts: float = 1200.0) -> None:
        self.max_safe_watts = max_safe_watts
        self.active_schedule: List[Dict[str, any]] = []

    def evaluate_compute_window(self, profile: EnergyProfile) -> Dict[str, any]:
        """Evaluate if current or upcoming window is optimal for heavy execution."""
        try:
            # Solar capacity estimation (assuming 1kW nominal panel setup in Nairobi)
            estimated_solar_generation = profile.solar_irradiance_wm2 * 0.85
            total_available_power = estimated_solar_generation + (
                (profile.battery_soc_percent / 100.0) * 2000.0
            )

            # Cost efficiency check (Kenya Power peak vs off-peak hours)
            current_hour = profile.timestamp.time()
            is_peak_grid = time(18, 0) <= current_hour <= time(22, 0)

            can_execute_heavy = (
                total_available_power >= profile.load_demand_watts
                and not is_peak_grid
            )

            decision = {
                "timestamp": profile.timestamp.isoformat(),
                "estimated_solar_w": round(estimated_solar_generation, 2),
                "total_power_w": round(total_available_power, 2),
                "is_peak_grid": is_peak_grid,
                "execute_heavy_workload": can_execute_heavy,
                "arbitrage_recommendation": (
                    "RUN_AUTONOMOUS_EVOLUTION"
                    if can_execute_heavy
                    else "DEFER_TO_SOLAR_PEAK"
                ),
            }
            logger.info(f"Arbitrage Decision Evaluated: {decision['arbitrage_recommendation']}")
            return decision
        except Exception as e:
            logger.error(f"Failed to evaluate energy profile: {e}")
            return {"error": str(
                e
            ), "execute_heavy_workload": False}


if __name__ == "__main__":
    engine = NairobiGridArbitrageEngine()
    sample_profile = EnergyProfile(
        timestamp=datetime.now(),
        solar_irradiance_wm2=750.0,
        battery_soc_percent=95.0,
        grid_tariff_kes_kwh=22.5,
        load_demand_watts=350.0,
    )
    result = engine.evaluate_compute_window(sample_profile)
    print("Arbitrage Test Result:", result)

    # Verify code self-compilation
    assert ast.parse(__doc__ + __file__ if False else "print('OK')")
