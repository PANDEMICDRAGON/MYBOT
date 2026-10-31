"""
Nairobi Commercial Grain Silo Fumigation & Atmospheric Gas Sentinel
Autonomous Evolutionary Architecture - Cycle #319
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [SiloFumigationSentinel]: %(message)s')

class GrainSiloFumigationSentinel:
    """
    Monitors atmospheric composition (Phosphine PH3, Carbon Dioxide CO2, Oxygen O2),
    temperature, and humidity inside commercial grain silos in Nairobi, issuing safety
    interlocks, ventilation triggers, and fumigation dosing recommendations.
    """
    def __init__(self, silo_id: str, grain_type: str = "maize", capacity_metric_tons: float = 5000.0):
        self.silo_id = silo_id
        self.grain_type = grain_type
        self.capacity_metric_tons = capacity_metric_tons
        self.active_fumigation = False
        self.phosphine_ppm = 0.0
        self.co2_percentage = 0.0
        self.oxygen_percentage = 20.9
        self.temperature_celsius = 25.0
        self.relative_humidity = 60.0
        self.ventilation_active = False
        self.safety_lockout = False
        logging.info(f"Initialized GrainSiloFumigationSentinel for Silo {self.silo_id} ({self.grain_type}, {self.capacity_metric_tons} MT)")

    def update_sensors(self, ph3: float, co2: float, o2: float, temp: float, rh: float) -> None:
        """Ingests live telemetry from silo sensor arrays."""
        self.phosphine_ppm = max(0.0, ph3)
        self.co2_percentage = max(0.0, co2)
        self.oxygen_percentage = max(0.0, min(100.0, o2))
        self.temperature_celsius = temp
        self.relative_humidity = max(0.0, min(100.0, rh))
        
        # Evaluate safety parameters
        if self.phosphine_ppm > 50.0 or self.oxygen_percentage < 19.0:
            self.safety_lockout = True
            logging.warning(f"[ALERT] Silo {self.silo_id} HAZARD DETECTED! PH3: {self.phosphine_ppm} ppm, O2: {self.oxygen_percentage}%")
        else:
            self.safety_lockout = False

    def regulate_atmosphere(self) -> Dict[str, Any]:
        """
        Performs real-time atmospheric control logic for grain preservation.
        Returns status dictionary with recommended actuator commands.
        """
        actions = {
            "silo_id": self.silo_id,
            "ventilation_command": "IDLE",
            "dosing_valve": "CLOSED",
            "risk_level": "LOW"
        }

        if self.safety_lockout:
            actions["ventilation_command"] = "EMERGENCY_PURGE"
            actions["dosing_valve"] = "LOCKED_OUT"
            actions["risk_level"] = "CRITICAL"
            self.ventilation_active = True
            return actions

        # Spoilage and humidity control
        if self.relative_humidity > 75.0 or self.temperature_celsius > 32.0:
            actions["ventilation_command"] = "CYCLE_FANS"
            self.ventilation_active = True
            actions["risk_level"] = "MODERATE"
        else:
            actions["ventilation_command"] = "OFF"
            self.ventilation_active = False

        # Fumigation maintenance
        if self.active_fumigation and self.phosphine_ppm < 200.0:
            actions["dosing_valve"] = "INJECT_PHOSPHINE"
        else:
            actions["dosing_valve"] = "CLOSED"

        return actions

    def audit_metrics(self) -> Dict[str, Any]:
        """Returns comprehensive status summary."""
        return {
            "silo_id": self.silo_id,
            "grain_type": self.grain_type,
            "phosphine_ppm": self.phosphine_ppm,
            "co2_percentage": self.co2_percentage,
            "oxygen_percentage": self.oxygen_percentage,
            "temperature_celsius": self.temperature_celsius,
            "relative_humidity": self.relative_humidity,
            "ventilation_active": self.ventilation_active,
            "safety_lockout": self.safety_lockout
        }

if __name__ == "__main__":
    print("--- Executing Nairobi Commercial Grain Silo Fumigation Sentinel Test Harness ---")
    sentinel = GrainSiloFumigationSentinel(silo_id="NAI-SILO-09", grain_type="white_maize", capacity_metric_tons=10000.0)
    
    # Simulate normal state
    sentinel.update_sensors(ph3=0.0, co2=0.04, o2=20.9, temp=24.5, rh=55.0)
    print("Normal State Audit:", sentinel.audit_metrics())
    print("Normal Control Action:", sentinel.regulate_atmosphere())
    
    # Simulate fumigation phase
    sentinel.active_fumigation = True
    sentinel.update_sensors(ph3=180.5, co2=1.2, o2=20.2, temp=26.0, rh=62.0)
    print("\nFumigation State Audit:", sentinel.audit_metrics())
    print("Fumigation Control Action:", sentinel.regulate_atmosphere())
    
    # Simulate gas leak / oxygen depletion hazard
    sentinel.update_sensors(ph3=75.0, co2=4.5, o2=17.5, temp=29.0, rh=78.0)
    print("\nHazard State Audit:", sentinel.audit_metrics())
    print("Hazard Control Action:", sentinel.regulate_atmosphere())
    print("--- Sentinel Test Complete ---")
