"""
Nairobi Commercial Grain Silo Aeration & Moisture Equilibrium Sentinel
Designed for autonomous psychrometric analysis and automated aeration fan management
in Nairobi grain storage and milling facilities.
"""

import logging
import math
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [SiloAerationSentinel]: %(message)s')
logger = logging.getLogger("GrainSiloAerationSentinel")

@dataclass
class SiloTelemetry:
    silo_id: str
    grain_type: str
    tonnage: float
    grain_temperature_c: float
    grain_moisture_pct: float
    ambient_temperature_c: float
    ambient_humidity_pct: float
    fan_status: bool

class GrainSiloAerationSentinel:
    """
    Autonomous controller for grain silo aeration systems, ensuring equilibrium moisture
    content (EMC) is maintained and preventing spoilage and hot spots.
    """

    SAFE_MOISTURE_LIMITS = {
        "maize": 13.5,
        "wheat": 12.5,
        "beans": 15.0,
        "sorghum": 13.0
    }

    def __init__(self, facility_name: str):
        self.facility_name = facility_name
        logger.info(f"Initializing Grain Silo Aeration Sentinel for facility: {facility_name}")

    def calculate_equilibrium_moisture(self, temp_c: float, rel_humidity: float, grain_type: str) -> float:
        """
        Calculates the approximate Equilibrium Moisture Content (EMC) for grain
        given ambient air conditions using Henderson's equation approximation.
        "" -" (simplified for operational robustness)
        """
        rh_fraction = max(0.01, min(0.99, rel_humidity / 100.0))
        # Henderson constants approximation for cereal grains
        c = 0.00005
        n = 1.8
        try:
            emc = ((-math.log(1.0 - rh_fraction)) / (c * (temp_c + 273.15))) ** (1.0 / n)
            return round(emc * 100, 2)
        except Exception as e:
            logger.error(f"EMC calculation error: {e}")
            return 13.0

    def evaluate_aeration_decision(self, telemetry: SiloTelemetry) -> Dict[str, Any]:
        """
        Evaluates whether aeration fans should run based on grain condition,
        ambient temperature differential, and relative humidity.
        """
        max_safe_moisture = self.SAFE_MOISTURE_LIMITS.get(telemetry.grain_type.lower(), 13.5)
        emc = self.calculate_equilibrium_moisture(
            telemetry.ambient_temperature_c,
            telemetry.ambient_humidity_pct,
            telemetry.grain_type
        )

        action = "OFF"
        reasons = []

        # Rule 1: High grain moisture or hot spots requiring cooling
        temp_diff = telemetry.grain_temperature_c - telemetry.ambient_temperature_c
        
        if telemetry.grain_temperature_c > 28.0 and temp_diff > 3.0 and telemetry.ambient_humidity_pct < 75.0:
            action = "ON"
            reasons.append("Cooling cycle initiated: Grain temp is significantly higher than ambient.")
        elif telemetry.grain_moisture_pct > max_safe_moisture and emc < telemetry.grain_moisture_pct:
            action = "ON"
            reasons.append(f"Drying cycle initiated: Ambient EMC ({emc}%) is lower than grain moisture ({telemetry.grain_moisture_pct}%).")
        elif telemetry.grain_moisture_pct <= max_safe_moisture and temp_diff <= 0:
            action = "OFF"
            reasons.append("Conditions optimal. Fans off to prevent moisture addition or unnecessary power draw.")
        else:
            # Prevent moisture addition if ambient humidity is too high
            if telemetry.ambient_humidity_pct > 80.0:
                action = "OFF"
                reasons.append("Fans halted: Ambient humidity dangerously high (>80%), risk of moisture absorption.")
            else:
                action = "MAINTAIN"
                reasons.append("Holding current state. Conditions stable.")

        return {
            "silo_id": telemetry.silo_id,
            "facility": self.facility_name,
            "recommended_action": action,
            "calculated_emc_pct": emc,
            "max_safe_moisture_pct": max_safe_moisture,
            "temperature_differential_c": round(temp_diff, 2),
            "reasons": reasons
        }

    def audit_facility(self, silos: List[SiloTelemetry]) -> List[Dict[str, Any]]:
        """Audits a batch of silos and returns aeration directives."""
        audit_results = []
        for silo in silos:
            result = self.evaluate_aeration_decision(silo)
            audit_results.append(result)
            logger.info(f"Silo {silo.silo_id} [{silo.grain_type}]: Action -> {result['recommended_action']}")
        return audit_results

if __name__ == "__main__":
    sentinel = GrainSiloAerationSentinel(facility_name="Nairobi Industrial Area Grain Terminal #4")
    test_silos = [
        SiloTelemetry(
            silo_id="SL-01",
            grain_type="maize",
            tonnage=1200.0,
            grain_temperature_c=31.5,
            grain_moisture_pct=14.2,
            ambient_temperature_c=22.0,
            ambient_humidity_pct=60.0,
            fan_status=False
        ),
        SiloTelemetry(
            silo_id="SL-02",
            grain_type="wheat",
            tonnage=850.0,
            grain_temperature_c=24.0,
            grain_moisture_pct=11.8,
            ambient_temperature_c=25.0,
            ambient_humidity_pct=85.0,
            fan_status=True
        )
    ]
    directives = sentinel.audit_facility(test_silos)
    print("Execution Successful. Directives Generated:", len(directives))
