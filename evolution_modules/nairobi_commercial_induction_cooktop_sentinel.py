import logging
import math
import random
import time
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [InductionSentinel]: %(message)s')

class CommercialInductionSentinel:
    """
    Monitors commercial induction cooktop power quality, harmonic distortion (THD),
    IGBT thermal drift, and magnetic cookware coupling efficiency for Nairobi kitchens.
    """
    def __init__(self, unit_id: str, rated_power_kw: float = 15.0):
        self.unit_id = unit_id
        self.rated_power_kw = rated_power_kw
        self.igbt_temp_c: float = 45.0
        self.thd_percent: float = 2.5
        self.pan_coupling_efficiency: float = 0.95
        self.supply_voltage: float = 415.0  # 3-phase standard in Kenya
        self.status = "STANDBY"
        logging.info(f"Initialized Induction Sentinel for unit {self.unit_id} ({self.rated_power_kw}kW)")

    def sample_telemetry(self, raw_telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Ingests raw sensor readings and updates internal metrics."""
        self.igbt_temp_c = raw_telemetry.get("igbt_temp_c", self.igbt_temp_c)
        self.thd_percent = raw_telemetry.get("thd_percent", self.thd_percent)
        self.pan_coupling_efficiency = raw_telemetry.get("pan_coupling_efficiency", self.pan_coupling_efficiency)
        self.supply_voltage = raw_telemetry.get("supply_voltage", self.supply_voltage)
        
        return {
            "unit_id": self.unit_id,
            "igbt_temp_c": self.igbt_temp_c,
            "thd_percent": self.thd_percent,
            "pan_coupling_efficiency": self.pan_coupling_efficiency,
            "supply_voltage": self.supply_voltage
        }

    def evaluate_safety_and_efficiency(self) -> Dict[str, Any]:
        """
        Analyzes operational parameters against safety thresholds and harmonics limits.
        Returns mitigation directives if anomalies are detected.
        """
        alerts = []
        actions = []

        # Thermal Check on IGBT Inverters
        if self.igbt_temp_c > 85.0:
            alerts.append("CRITICAL_IGBT_OVERHEAT")
            actions.append("REDUCE_POWER_TO_50_PERCENT")
            self.status = "THERMAL_THROTTLED"
        elif self.igbt_temp_c > 75.0:
            alerts.append("WARNING_IGBT_ELEVATED_TEMP")
            actions.append("INCREASE_COOLING_FAN_SPEED")
            self.status = "ELEVATED"
        else:
            self.status = "OPTIMAL"

        # Total Harmonic Distortion (THD) Check (IEEE 519 Standard < 5% preferred)
        if self.thd_percent > 8.0:
            alerts.append(
                f"EXCESSIVE_GRID_THD: {self.thd_percent}%")
            actions.append("ENGAGE_ACTIVE_HARMONIC_FILTER")

        # Pan Coupling Efficiency Check
        if self.pan_coupling_efficiency < 0.75:
            alerts.append("POOR_COOKWARE_COUPLING")
            actions.append("NOTIFY_CHEF_CHECK_PAN_FLATNESS")

        # Supply Voltage Fluctuation (Nairobi Grid Dips)
        if self.supply_voltage < 360.0 or self.supply_voltage > 456.0:
            alerts.append(f"GRID_VOLTAGE_OUT_OF_BOUNDS: {self.supply_voltage}V")
            actions.append("TRIGGER_BROWNOUT_PROTECTION_RELAY")

        return {
            "unit_id": self.unit_id,
            "status": self.status,
            "alerts": alerts,
            "actions_recommended": actions,
            "timestamp": time.time()
        }

    def run_harmonic_simulation_cycle(self, iterations: int = 3) -> List[Dict[str, Any]]:
        """Runs a simulation loop to test sentinel reactions under fluctuating grid conditions."""
        results = []
        for i in range(iterations):
            simulated_temp = 50.0 + (i * 14.0) + random.uniform(-2.0, 2.0)
            simulated_thd = 3.0 + (i * 2.1) + random.uniform(-0.5, 0.5)
            simulated_voltage = 415.0 - (i * 20.0)
            sim_data = {
                "igbt_temp_c": simulated_temp,
                "thd_percent": simulated_thd,
                "pan_coupling_efficiency": 0.90 - (i * 0.05),
                "supply_voltage": simulated_voltage
            }
            self.sample_telemetry(sim_data)
            eval_res = self.evaluate_safety_and_efficiency()
            results.append(eval_res)
        return results

if __name__ == "__main__":
    sentinel = CommercialInductionSentinel(unit_id="NBI-KITCHEN-INDUCTION-04", rated_power_kw=20.0)
    simulation_output = sentinel.run_harmonic_simulation_cycle(iterations=3)
    for step, res in enumerate(simulation_output):
        logging.info(f"Simulation Step {step+1}: {res}")
