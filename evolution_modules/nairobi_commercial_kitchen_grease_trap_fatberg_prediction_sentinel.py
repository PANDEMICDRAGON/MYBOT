"""
Nairobi Commercial Kitchen Grease Trap Fatberg Prediction & Bio-Enzymatic Remediation Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import time
import math
import random
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [FATBERG_SENTINEL] %(levelname)s: %(message)s')
logger = logging.getLogger("FatbergPredictionSentinel")


class GreaseTrapFatbergPredictor:
    """
    Monitors grease trap sensor arrays (pH, temperature gradient, fluid viscosity, and ultrasonic scum layer thickness)
    to predict fatberg solidification and autonomously manage bio-enzyme dosing.
    """

    def __init__(self, trap_id: str, capacity_liters: float = 250.0):
        self.trap_id = trap_id
        self.capacity_liters = capacity_liters
        self.scum_thickness_mm = 15.0  # baseline scum layer
        self.water_temp_c = 42.0
        self.effluent_pH = 6.8
        self.viscosity_cp = 12.5  # centipoise
        self.enzyme_pump_active = False
        self.last_dosing_timestamp = 0.0
        logger.info(f"Grease Trap Sentinel initialized for {{self.trap_id}} (Capacity: {{self.capacity_liters}}L)")

    def ingest_telemetry(self, raw_data: Dict[str, float]) -> None:
        """Ingests raw IoT sensor telemetry from the commercial kitchen grease trap."""
        self.scum_thickness_mm = raw_data.get("scum_thickness_mm", self.scum_thickness_mm)
        self.water_temp_c = raw_data.get("water_temp_c", self.water_temp_c)
        self.effluent_pH = raw_data.get("effluent_pH", self.effluent_pH)
        self.viscosity_cp = raw_data.get("viscosity_cp", self.viscosity_cp)

    def compute_fatberg_risk_index(self) -> float:
        """
        Calculates a dimensionless risk index (0.0 to 1.0) based on scum depth,
        effluent temperature drops, and elevated viscosity indicative of FOG solidification.
        """
        # Scum risk factor (critical threshold at 80mm)
        scum_factor = min(1.0, self.scum_thickness_mm / 80.0)
        
        # Temperature factor: cooler water (<35C) accelerates FOG hardening
        temp_factor = 1.0 if self.water_temp_c < 35.0 else max(0.0, (50.0 - self.water_temp_c) / 15.0)
        
        # Viscosity factor (baseline normal ~10 cP, thick fatberg > 45 cP)
        viscosity_factor = min(1.0, max(0.0, (self.viscosity_cp - 10.0) / 35.0))

        # Weighted risk score
        risk_index = (0.5 * scum_factor) + (0.3 * viscosity_factor) + (0.2 * temp_factor)
        return round(min(1.0, max(0.0, risk_index)), 4)

    def evaluate_remediation_action(self) -> Dict[str, Any]:
        """
        Determines whether to trigger bio-enzymatic dosing or escalate an alert
        to facility maintenance in Nairobi.
        """
        risk = self.compute_fatberg_risk_index()
        action_taken = "NONE"
        current_time = time.time()

        # Trigger bio-enzyme dosing if risk exceeds 0.65 and coolddown has elapsed (3600s)
        if risk >= 0.65 and not self.enzyme_pump_active:
            if (current_time - self.last_dosing_timestamp) > 3600:
                self.enzyme_pump_active = True
                self.last_dosing_timestamp = current_time
                action_taken = "TRIGGER_BIO_ENZYME_DOSING"
                logger.warning(f"High Fatberg Risk ({{risk}})! Activating targeted bio-enzyme dosing pump for {{self.trap_id}}.")
            else:
                action_taken = "COOLDOWN_ACTIVE"
        elif risk < 0.40 and self.enzyme_pump_active:
            self.enzyme_pump_active = False
            action_taken = "CEASE_DOSING_NORMAL_FLOW"

        return {
            "trap_id": self.trap_id,
            "fatberg_risk_index": risk,
            "scum_thickness_mm": self.scum_thickness_mm,
            "viscosity_cp": self.viscosity_cp,
            "water_temp_c": self.water_temp_c,
            "action_taken": action_taken,
            "enzyme_pump_active": self.enzyme_pump_active,
            "timestamp": current_time
        }


if __name__ == "__main__":
    print("=== Executing Nairobi Commercial Kitchen Grease Trap Fatberg Prediction Harness ===")
    sentinel = GreaseTrapFatbergPredictor(trap_id="TRAP-NBO-WESTLANDS-04")

    # Simulate fluctuating kitchen telemetry
    mock_telemetry_stream = [
        {"scum_thickness_mm": 20.0, "water_temp_c": 41.0, "effluent_pH": 6.7, "viscosity_cp": 11.0},
        {"scum_thickness_mm": 45.0, "water_temp_c": 36.0, "effluent_pH": 6.2, "viscosity_cp": 28.5},
        {"scum_thickness_mm": 78.0, "water_temp_c": 31.0, "effluent_pH": 5.8, "viscosity_cp": 48.0},
    ];

    for idx, telemetry in enumerate(mock_telemetry_stream, 1):
        print(f"\n-- Simulation Cycle {{idx}} --")
        sentinel.ingest_telemetry(telemetry)
        report = sentinel.evaluate_remediation_action()
        print(f"Telemetry Ingested: {{telemetry}}")
        print(f"Evaluation Report: {{report}}")

    print("=== Fatberg Prediction Sentinel Test Complete ===")
