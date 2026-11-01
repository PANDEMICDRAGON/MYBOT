"""
Nairobi Commercial Kitchen Grease Odor Scrubber Ionic Plasma Electrostatic Precipitator Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import time
import logging
import random
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [KitchenScrubberSentinel]: %(message)s")

class KitchenScrubberSentinel:
    """
    Monitors and optimizes commercial kitchen exhaust electrostatic filtration, plasma ionization,
    and VOC ozone scrubbing arrays to prevent grease buildup and neighborhood odor complaints.
    """
    def __init__(self, scrubber_id: str, airflow_cfm: float = 5000.0):
        self.scrubber_id = scrubber_id
        self.airflow_cfm = airflow_cfm
        self.ep_voltage_kv = 12.0  # Electrostatic Precipitator kV
        self.plasma_current_ma = 450.0  # Ionic plasma cell mA
        self.uv_lamp_hours_used = 1200.0
        self.max_uv_lamp_hours = 8000.0
        self.duct_static_pressure_pa = 250.0  # Pascals
        self.voc_ppm_inlet = 180.0
        self.voc_ppm_outlet = 12.0
        self.grease_accumulation_index = 0.15  # 0.0 to 1.0 scale
        logging.info(f"Initialized Kitchen Scrubber Sentinel [{self.scrubber_id}] for {self.airflow_cfm} CFM exhaust.")

    def sample_telemetry(self) -> Dict[str, Any]:
        """Simulates real-time sensor polling from the scrubber stack."""
        # Introduce slight operational drift
        self.ep_voltage_kv += random.uniform(-0.2, 0.2)
        self.plasma_current_ma += random.uniform(-5.0, 5.0)
        self.duct_static_pressure_pa += random.uniform(-2.0, 2.0)
        self.grease_accumulation_index += 0.0001
        self.uv_lamp_hours_used += 0.5

        scrubbing_efficiency = max(0.0, min(100.0, 100.0 * (1.0 - (self.voc_ppm_outlet / max(1.0, self.voc_ppm_inlet)))))
        
        return {
            "scrubber_id": self.scrubber_id,
            "ep_voltage_kv": round(self.ep_voltage_kv, 2),
            "plasma_current_ma": round(self.plasma_current_ma, 2),
            "uv_lamp_life_pct": round(100.0 * (1.0 - (self.uv_lamp_hours_used / self.max_uv_lamp_hours)), 1),
            "duct_static_pressure_pa": round(self.duct_static_pressure_pa, 1),
            "voc_scrubbing_efficiency_pct": round(scrubbing_efficiency, 2),
            "grease_accumulation_index": round(self.grease_accumulation_index, 3),
            "timestamp": time.time()
        }

    def diagnose_and_mitigate(self, metrics: Dict[str, Any]) -> List[str]:
        """Evaluates telemetry and triggers automated voltage tuning or wash cycles."""
        actions = []
        
        if metrics["ep_voltage_kv"] < 10.0:
            actions.append("Boost EP transformer tap-changer voltage to restore particulate capture.")
            self.ep_voltage_kv = 12.0
            
        if metrics["duct_static_pressure_pa"] > 320.0:
            actions.append("WARNING: High static pressure detected. Electrostatic mesh or pre-filters heavily loaded with grease. Triggering automated detergent wash cycle.")
            self.grease_accumulation_index = max(0.0, self.grease_accumulation_index - 0.1)
            self.duct_static_pressure_pa = 250.0
            
        if metrics["uv_lamp_life_pct"] < 15.0:
            actions.append("CRITICAL: UV-C Ozone Scrubber lamps approaching end-of-life. Scheduling replacement before Nairobi County environmental audit.")
            
        if metrics["voc_scrubbing_efficiency_pct"] < 85.0:
            actions.append("Increase plasma generator injection frequency to neutralize elevated kitchen VOC surge.")
            self.plasma_current_ma = 520.0

        return actions

if __name__ == "__main__":
    print("--- Executing Nairobi Commercial Kitchen Scrubber Sentinel Test Harness ---")
    sentinel = KitchenScrubberSentinel(scrubber_id="WESTLANDS-KITCHEN-EXT-04")
    for cycle in range(3):
        telemetry = sentinel.sample_telemetry()
        remedies = sentinel.diagnose_and_mitigate(telemetry)
        print(f"Cycle {cycle+1} Telemetry: {telemetry}")
        print(f"Cycle {cycle+1} Mitigations: {remedies if remedies else ['All systems nominal']}\n")
    print("--- Sentinel Validation Complete ---")
