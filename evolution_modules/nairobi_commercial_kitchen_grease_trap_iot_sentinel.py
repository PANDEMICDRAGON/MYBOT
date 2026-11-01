"""Nairobi Commercial Kitchen Grease Trap IoT Sentinel & Effluent Compliance.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Monitors commercial kitchen grease trap telemetry (FOG accumulation, pH, temperature,
level sensors, and enzymatic dosing status) to ensure compliance with Nairobi City County
sewerage effluent regulations and prevent municipal drainage clogs.
"""

import time
import logging
import random
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("GreaseTrapIoT-" + __name__)

class GreaseTrapConfig:
    """Configuration parameters for commercial grease trap monitoring."""
    def __init__(
        self, 
        max_fog_thickness_cm: float = 12.0, 
        min_pH: float = 5.5,
        max_pH: float = 9.0,
        max_temperature_c: float = 45.0,
        dosing_interval_hours: int = 12
    ):
        self.max_fog_thickness_cm = max_fog_thickness_cm
        self.min_pH = min_pH
        self.max_pH = max_pH
        self.max_temperature_c = max_temperature_c
        self.dosing_interval_hours = dosing_interval_hours


class GreaseTrapTelemetry:
    """Represents a point-in-time telemetry sample from the grease trap IoT sensors."""
    def __init__(
        self,
        trap_id: str,
        fog_layer_cm: float,
        water_temp_c: float,
        effluent_ph: float,
        ambient_temp_c: float,
        heater_active: bool,
        enzyme_pump_active: bool,
        high_level_alarm: bool
    ):
        self.trap_id = trap_id
        self.fog_layer_cm = fog_layer_cm
        self.water_temp_c = water_temp_c
        self.effluent_ph = effluent_ph
        self.ambient_temp_c = ambient_temp_c
        self.heater_active = heater_active
        self.enzyme_pump_active = enzyme_pump_active
        self.high_level_alarm = high_level_alarm
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trap_id": self.trap_id,
            "fog_layer_cm": self.fog_layer_cm,
            "water_temp_c": self.water_temp_c,
            "effluent_ph": self.effluent_ph,
            "ambient_temp_c": self.ambient_temp_c,
            "heater_active": self.heater_active,
            "enzyme_pump_active": self.enzyme_pump_active,
            "high_level_alarm": self.high_level_alarm,
            "timestamp": self.timestamp
        }


class GreaseTrapSentinelEngine:
    """Analyzes grease trap telemetry and dictates actuation policies for compliance."""
    def __init__(self, config: GreaseTrapConfig):
        self.config = config
        self.audit_log: List[Dict[str, Any]] = []

    def evaluate_telemetry(self, telemetry: GreaseTrapTelemetry) -> Dict[str, Any]:
        """Evaluate telemetry against compliance thresholds and return action commands."""
        alerts = []
        actions = {
            "trigger_heater": False,
            "trigger_enzyme_dosing": False,
            "dispatch_pump_out": False,
            "emergency_shutoff_kitchen_inflow": False
        }

        # FOG Thickness Check
        if telemetry.fog_layer_cm >= self.config.max_fog_thickness_cm:
            alerts.append(f"CRITICAL: FOG layer thickness ({telemetry.fog_layer_cm}cm) exceeds threshold ({self.config.max_fog_thickness_cm}cm).")
            actions["dispatch_pump_out"] = True
            actions["emergency_shutoff_kitchen_inflow"] = True

        # pH Compliance Check (Nairobi City County bylaws)
        if telemetry.effluent_ph < self.config.min_pH or telemetry.effluent_ph > self.config.max_pH:
            alerts.append(f"WARNING: Effluent pH ({telemetry.effluent_ph}) out of compliance range [{self.config.min_pH}-{self.config.max_pH}].")

        # Temperature Check
        if telemetry.water_temp_c > self.config.max_temperature_c:
            alerts.append(f"NOTICE: Grease trap water temperature ({telemetry.water_temp_c}°C) high. Risk of emulsification escape.")
            actions["trigger_heater"] = False
        else:
            actions["trigger_heater"] = True

        # High Level Alarm
        if telemetry.high_level_alarm:
            alerts.append("EMERGENCY: High liquid level detected in interceptor chamber!")
            actions["emergency_shutoff_kitchen_inflow"] = True
            actions["dispatch_pump_out"] = True

        assessment = {
            "trap_id": telemetry.trap_id,
            "timestamp": telemetry.timestamp,
            "compliant": len(alerts) == 0,
            "alerts": alerts,
            "recommended_actions": actions
        }

        self.audit_log.append(assessment)
        return assessment

    def simulate_telemetry_stream(self, trap_id: str, iterations: int = 3) -> List[Dict[str, Any]]:
        """Simulates a live IoT stream for validation and testing."""
        results = []
        for i in range(iterations):
            # Inject occasional anomalies for realism
            fog = round(random.uniform(2.0, 14.0), 2)
            water_temp = round(random.uniform(30.0, 50.0), 1)
            ph = round(random.uniform(5.0, 10.0), 1)
            ambient = round(random.uniform(20.0, 32.0), 1)
            high_alarm = fog > 13.0

            sample = GreaseTrapTelemetry(
                trap_id=trap_id,
                fog_layer_cm=fog,
                water_temp_c=water_temp,
                effluent_ph=ph,
                ambient_temp_c=ambient,
                heater_active=water_temp < 38.0,
                enzyme_pump_active=(i % 2 == 0),
                high_level_alarm=high_alarm
            )
            results.append(self.evaluate_telemetry(sample))
        return results


if __name__ == "__main__":
    logger.info("Initializing Nairobi Commercial Kitchen Grease Trap IoT Sentinel...")
    config = GreaseTrapConfig()
    sentinel = GreaseTrapSentinelEngine(config)
    
    simulation_results = sentinel.simulate_telemetry_stream("TRAP_WESTLANDS_04", iterations=3)
    for res in simulation_results:
        logger.info(f"Evaluation Result: {res}")
    logger.info("Grease Trap Sentinel operational and compliance verification complete.")
