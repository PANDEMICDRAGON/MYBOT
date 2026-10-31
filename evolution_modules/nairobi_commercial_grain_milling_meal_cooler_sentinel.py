"""
Nairobi Commercial Grain Milling Meal Cooler & Pneumatic Receiver Sentinel
Autonomous Evolutionary Module #351

Designed to monitor temperature differential, airflow velocity, moisture retention,
and cyclone discharge air locks for commercial meal cooling systems in Nairobi, Kenya.
"""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MealCoolerSentinel")

class MealCoolerSentinel:
    """
    Monitors temperature drops, static pressure drop, airlock rotation speed,
    and relative humidity of meal output from roller/hammer mills.
    """
    def __init__(self, cooler_id: str, target_temp_c: float = 28.0, max_humidity_pct: float = 13.5):
        self.cooler_id = cooler_id
        self.target_temp_c = target_temp_c
        self.max_humidity_pct = max_humidity_pct
        self.operational_status = "INITIALIZED"
        self.metrics_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized MealCoolerSentinel for unit: {self.cooler_id}")

    def inspect_cooling_cycle(self, inlet_temp: float, outlet_temp: float, airflow_cfm: float, airlock_rpm: float, meal_humidity: float) -> Dict[str, Any]:
        """
        Evaluates operational parameters of the meal cooler and pneumatic receiver.
        """
        temp_drop = inlet_temp - outlet_temp
        cooling_efficiency = (temp_drop / max(inlet_temp, 1.0)) * 100.0
        
        anomalies = []
        status = "OPTIMAL"

        if outlet_temp > (self.target_temp_c + 4.0):
            anomalies.append("EXCESSIVE_OUTLET_TEMPERATURE")
            status = "WARNING"
            
        if meal_humidity > self.max_humidity_pct:
            anomalies.append("HIGH_MEAL_MOISTURE_RISK_SPOILAGE")
            status = "CRITICAL"
            
        if airlock_rpm < 10.0 or airlock_rpm > 65.0:
            anomalies.append("ROTARY_AIRLOCK_SPEED_DEVIATION")
            status = "WARNING"

        if airflow_cfm < 1200.0:
            anomalies.append("INSUFFICIENT_COOLING_AIR_VELOCITY")
            status = "CRITICAL"

        telemetry = {
            "timestamp": time.time(),
            "cooler_id": self.cooler_id,
            "inlet_temp_c": inlet_temp,
            "outlet_temp_c": outlet_temp,
            "temp_drop_c": temp_drop,
            "cooling_efficiency_pct": round(cooling_efficiency, 2),
            "airflow_cfm": airflow_cfm,
            "airlock_rpm": airlock_rpm,
            "meal_humidity_pct": meal_humidity,
            "anomalies": anomalies,
            "status": status
        }

        self.metrics_history.append(telemetry)
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)

        logger.info(f"[MealCooler {self.cooler_id}] Status: {status} | Efficiency: {cooling_efficiency:.1f}% | Anomalies: {anomalies}")
        return telemetry

    def get_diagnostics(self) -> Dict[str, Any]:
        """Returns historical diagnostic summary."""
        if not self.metrics_history:
            return {"status": "NO_DATA"}
        latest = self.metrics_history[-1]
        return {
            "cooler_id": self.cooler_id,
            "last_status": latest["status"],
            "total_inspections": len(self.metrics_history),
            "last_efficiency": latest["cooling_efficiency_pct"]
        }

if __name__ == "__main__":
    sentinel = MealCoolerSentinel(cooler_id="MC-NAIROBI-WESTLANDS-01")
    sample_telemetry = sentinel.inspect_cooling_cycle(
        inlet_temp=54.5,
        outlet_temp=29.2,
        airflow_cfm=1850.0,
        airlock_rpm=32.0,
        meal_humidity=12.8
    )
    print("Test Harness Execution Successful:", sample_telemetry)
