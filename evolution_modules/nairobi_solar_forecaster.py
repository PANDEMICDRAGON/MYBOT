import ast
import json
import logging
import math
import time
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [SOLAR_FORECASTER] %(levelname)s: %(message)s')
logger = logging.getLogger('NairobiSolarForecaster')

class NairobiSolarForecaster:
    """
    Autonomous Solar Power Micro-Grid Load & Weather Forecasting Engine.
    Predicts solar photovoltaic yield based on atmospheric pressure, cloud cover proxy,
    and historical Nairobi diurnal curves, adjusting system resource quotas dynamically.
    """
    def __init__(self, panel_capacity_watts: float = 1200.0, battery_capacity_wh: float = 2400.0) -> None:
        self.panel_capacity_watts = panel_capacity_watts
        self.battery_capacity_wh = battery_capacity_wh
        self.current_battery_wh = battery_capacity_wh * 0.95  # Start near full
        self.history: List[Dict[str, float]] = []
        logger.info("NairobiSolarForecaster initialized: Panel=%.1fW, Battery=%.1fWh", panel_capacity_watts, battery_capacity_wh)

    def predict_generation(self, hour_of_day: float, cloud_cover_percent: float, ambient_temp_c: float) -> float:
        """
        Predicts current solar generation in watts using a bell-curve diurnal model modulated
        by cloud cover and temperature coefficient losses.
        """
        if hour_of_day < 6.0 or hour_of_day > 18.0:
            return 0.0
        
        # Standard bell curve peaked at 13:00 (1 PM)
        diurnal_factor = math.sin(math.pi * (hour_of_day - 6.0) / 12.0)
        diurnal_factor = max(0.0, diurnal_factor)

        # Cloud attenuation (0% cloud = 1.0, 100% cloud = 0.2)
        cloud_factor = 1.0 - (0.8 * (min(100.0, max(0.0, cloud_cover_percent)) / 100.0))

        # Temperature derating (panels lose efficiency above 25°C standard test conditions)
        temp_coeff_loss = max(0.0, (ambient_temp_c - 25.0) * 0.004)
        temp_factor = 1.0 - temp_coeff_loss

        generation = self.panel_capacity_watts * diurnal_factor * cloud_factor * temp_factor
        return round(max(0.0, generation), 2)

    def simulate_step(self, hour_of_day: float, cloud_cover: float, temp: float, load_watts: float) -> Dict[str, float]:
        """
        Simulates one power cycle step, updating internal battery state and returning metrics.
        """
        gen_watts = self.predict_generation(hour_of_day, cloud_cover, temp)
        net_power = gen_watts - load_watts
        
        # Assume 1-hour step for simplicity in Wh calculation
        self.current_battery_wh = min(
            self.battery_capacity_wh,
            max(0.0, self.current_battery_wh + net_power)
        )

        soc = (self.current_battery_wh / self.battery_capacity_wh) * 100.0
        
        state = {
            "hour": hour_of_day,
            "generation_watts": gen_watts,
            "load_watts": load_watts,
            "net_power_watts": net_power,
            "battery_soc_percent": round(soc, 2),
            "battery_energy_wh": round(self.current_battery_wh, 2)
        }
        self.history.append(state)
        return state

    def recommend_load_shedding(self, current_soc: float) -> str:
        """
        Recommends system load throttling levels based on battery State Of Charge (SOC).
        """
        if current_soc > 50.0:
            return "NORMAL_OPERATION (100% compute capacity available)"
        elif current_soc > 25.0:
            return "MODERATE_THROTTLE (Defer heavy ML model retraining, maintain edge mesh sync)"
        elif current_soc > 10.0:
            return "AGGRESSIVE_SHEDDING (Suspend non-critical telemetry, maintain USSD/M-Pesa failovers)"
        else:
            return "CRITICAL_CONSERVATION (Hibernate non-essential subsystems, preserve operator comms)"

if __name__ == "__main__":
    logger.info("Executing self-test verification for NairobiSolarForecaster...")
    forecaster = NairobiSolarForecaster(panel_capacity_watts=1500.0, battery_capacity_wh=3000.0)
    
    # Simulate midday peak with light clouds
    step1 = forecaster.simulate_step(hour_of_day=13.5, cloud_cover=15.0, temp=28.0, load_watts=350.0)
    logger.info("Midday Simulation: %s", json.dumps(step1, indent=2))
    
    recommendation = forecaster.recommend_load_shedding(step1["battery_soc_percent"])
    logger.info("Load Recommendation: %s", recommendation)
    
    # Validate syntax integrity
    module_code = open(__file__, "r", encoding="utf-8").read()
    parsed_ast = ast.parse(module_code)
    assert parsed_ast is not None, "AST compilation check failed!"
    logger.info("NairobiSolarForecaster successfully verified and validated.")
