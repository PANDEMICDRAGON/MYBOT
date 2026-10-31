"""Nairobi Commercial Ozone Water Treatment & Bottling Sentinel.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
Description:
    Manages real-time sensor telemetry for commercial ozone water treatment
    plants, including ORP levels, dissolved ozone concentration (ppm),
    ambient ozone gas leak detectors, backwash pressure differentials, and
    automated emergency shutdown protocols.
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("OzoneWaterSentinel")


class OzoneTreatmentSystem:
    """Monitors and controls commercial ozone water treatment and bottling lines."""

    def __init__(self, plant_id: str, max_ozone_ppm: float = 0.4, max_ambient_ppm: float = 0.1):
        self.plant_id = plant_id
        self.max_ozone_ppm = max_ozone_ppm
        self.max_ambient_ppm = max_ambient_ppm
        self.is_ozone_generator_active = False
        self.is_emergency_shutdown = False
        self.last_telemetry: Dict[str, Any] = {}
        self.alarm_log: List[str] = []

    def evaluate_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates incoming sensor streams and executes safety interlocks."""
        self.last_telemetry = telemetry
        timestamp = telemetry.get("timestamp", time.time())
        dissolved_ozone = telemetry.get("dissolved_ozone_ppm", 0.0)
        ambient_ozone = telemetry.get("ambient_ozone_ppm", 0.0)
        orp_mv = telemetry.get("orp_mv", 0.0)
        filter_delta_bar = telemetry.get("filter_delta_bar", 0.0)
        water_flow_lpm = telemetry.get("water_flow_lpm", 0.0)

        actions = []

        # Safety Check 1: Ambient Ozone Leak Detection ( OSHA limit ~0.1 ppm )
        if ambient_ozone > self.max_ambient_ppm:
            self.is_emergency_shutdown = True
            self.is_ozone_generator_active = False
            msg = f"CRITICAL: Ambient ozone leak detected ({ambient_ozone} ppm)! Emergency shutdown engaged."
            logger.critical(msg)
            self.alarm_log.append(f"{timestamp}: {msg}")
            actions.append("SHUTDOWN_GENERATOR")
            actions.append("ACTIVATE_EXHAUST_FAN")

        # Safety Check 2: Dissolved Ozone Over-concentration
        elif dissolved_ozone > self.max_ozone_ppm:
            self.is_ozone_generator_active = False
            msg = f"WARNING: Dissolved ozone too high ({dissolved_ozone} ppm). Pausing generator."
            logger.warning(msg)
            self.alarm_log.append(f"{timestamp}: {msg}")
            actions.append("PAUSE_GENERATOR")

        # Operational Check 3: Filter Backwash Required
        if filter_delta_bar > 1.5:
            msg = f"NOTICE: High micro-filter pressure differential ({filter_delta_bar} bar). Initiate backwash."
            logger.info(msg)
            actions.append("TRIGGER_FILTER_BACKWASH")

        # Normal Operation
        if not self.is_emergency_shutdown and dissolved_ozone <= self.max_ozone_ppm and ambient_ozone <= self.max_ambient_ppm:
            if water_flow_lpm > 10.0 and not self.is_ozone_generator_active:
                self.is_ozone_generator_active = True
                actions.append("START_GENERATOR")

        return {
            "plant_id": self.plant_id,
            "status": "EMERGENCY_SHUTDOWN" if self.is_emergency_shutdown else "OPERATIONAL",
            "generator_active": self.is_ozone_generator_active,
            "orp_mv": orp_mv,
            "dissolved_ozone_ppm": dissolved_ozone,
            "ambient_ozone_ppm": ambient_ozone,
            "actions_triggered": actions,
            "timestamp": timestamp
        }

    def reset_system(self, operator_key: str) -> bool:
        """Resets emergency shutdown after manual operator verification in Nairobi."""
        if operator_key == "MICHAEL_OBIERO_SECURE_AUTH":
            self.is_emergency_shutdown = False
            logger.info("Operator successfully cleared ozone sentinel emergency state.")
            return True
        logger.warning("Unauthorized reset attempt on ozone treatment system.")
        return False


if __name__ == "__main__":
    print("Initializing Nairobi Commercial Ozone Water Treatment & Bottling Sentinel Test Harness...")
    sentinel = OzoneTestSystem = OzoneTreatmentSystem("PLANT_NAI_CBD_01")

    # Test normal running telemetry
    telemetry_normal = {
        "timestamp": time.time(),
        "dissolved_ozone_ppm": 0.25,
        "ambient_ozone_ppm": 0.02,
        "orp_mv": 750.0,
        "filter_delta_bar": 0.8,
        "water_flow_lpm": 45.0
    }
    result_1 = sentinel.evaluate_telemetry(telemetry_normal)
    print("Telemetry Result 1:", json.dumps(result_1, indent=2))

    # Test ambient leak emergency
    telemetry_leak = {
        "timestamp": time.time() + 10,
        "dissolved_ozone_ppm": 0.28,
        "ambient_ozone_ppm": 0.35,
        "orp_mv": 820.0,
        "filter_delta_bar": 1.6,
        "water_flow_lpm": 0.0
    }
    result_2 = sentinel.evaluate_telemetry(telemetry_leak)
    print("Telemetry Result 2 (Leak Simulation):", json.dumps(result_2, indent=2))

    # Reset test
    sentinel.reset_system("MICHAEL_OBIERO_SECURE_AUTH")
    print("Sentinel state after reset:", sentinel.is_emergency_shutdown)
    print("Ozone Sentinel Module test completed successfully.")
